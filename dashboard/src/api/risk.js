export const apiBase = (import.meta.env.VITE_API_URL || (import.meta.env.MODE === 'api' ? '/api' : '')).replace(/\/$/, '');

export async function fetchScene(signal) {
  const response = await fetch(apiBase ? apiBase + '/risk' : '/mock/risk.json', { signal });
  if (!response.ok) throw new Error('Scene request failed (' + response.status + ').');
  const scene = await response.json();
  if (scene.crs !== 'EPSG:4326' || scene.labels.length !== scene.width * scene.height ||
      scene.corners.length !== (scene.width + 1) * (scene.height + 1)) {
    throw new Error('The scene grid is incomplete or uses an unsupported CRS.');
  }
  return scene;
}
