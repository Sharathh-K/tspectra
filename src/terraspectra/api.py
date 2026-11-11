"""Local FastAPI service. Send raw TIFF bytes, not a local path or multipart form."""
from contextlib import asynccontextmanager
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
import rasterio

from terraspectra.tiling import TilePredictor, classify_raster

MAX_BYTES = 128 * 1024 * 1024
MAX_TILES = 256


@asynccontextmanager
async def lifespan(app):
    app.state.predictor = TilePredictor()
    app.state.busy = False  # One upload/inference per single-worker local service.
    yield


app = FastAPI(title='TerraSpectra local inference', version='0.4.0', lifespan=lifespan)


@app.get('/api/health')
def health():
    return {'status': 'ready', 'model': 'CNN + transformer', 'device': 'cpu',
            'max_upload_mib': 128, 'max_tiles': MAX_TILES, 'busy': app.state.busy}


async def process_upload(request, tiled):
    if app.state.busy:
        raise HTTPException(429, 'Another image is being processed. Please retry shortly.')
    app.state.busy = True
    directory = Path(tempfile.mkdtemp(prefix='terraspectra-api-'))
    keep_for_download = False
    try:
        total = 0
        # Streams into a temporary file rather than reading the whole upload into RAM.
        with (directory/'input.tif').open('wb') as handle:
            async for chunk in request.stream():
                total += len(chunk)
                if total > MAX_BYTES:
                    raise HTTPException(413, 'Upload exceeds 128 MiB.')
                handle.write(chunk)
        if total == 0:
            raise HTTPException(422, 'Upload an actual TIFF file as the request body.')
        report = await run_in_threadpool(
            classify_raster, directory/'input.tif', directory/'predictions.tif',
            app.state.predictor, MAX_TILES, not tiled)
        if not tiled:
            return report
        (directory/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
        archive = directory/'predictions.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
            for name in ['predictions.tif','summary.json']:
                bundle.write(directory/name,name)
        keep_for_download = True
        return FileResponse(archive, media_type='application/zip', filename='terraspectra-predictions.zip',
                            background=BackgroundTask(shutil.rmtree,directory,ignore_errors=True))
    except (ValueError, rasterio.errors.RasterioIOError) as error:
        raise HTTPException(422, 'Unsupported TIFF: ' + str(error)) from error
    finally:
        app.state.busy = False
        if not keep_for_download:
            shutil.rmtree(directory,ignore_errors=True)


BODY_SCHEMA = {'requestBody': {'required': True, 'content': {
    'application/octet-stream': {'schema': {'type': 'string', 'format': 'binary'}}}}}


@app.post('/api/predict', openapi_extra=BODY_SCHEMA)
async def predict_patch(request: Request):
    return await process_upload(request, tiled=False)


@app.post('/api/tile', openapi_extra=BODY_SCHEMA)
async def predict_tiles(request: Request):
    return await process_upload(request, tiled=True)
