export function geometry(scene) {
  const { width, height, corners, labels } = scene;
  const corner = (r, c) => corners[r * (width + 1) + c];
  const boundary = [corner(0, 0), corner(0, width), corner(height, width), corner(height, 0)];
  const cells = labels.map((label, id) => {
    const row = Math.floor(id / width), col = id % width;
    const polygon = [corner(row, col), corner(row, col + 1),
      corner(row + 1, col + 1), corner(row + 1, col)];
    const center = [0, 1].map(axis => polygon.reduce((n, p) => n + p[axis], 0) / 4);
    return { id, row, col, label, polygon, center };
  });
  return { boundary, cells };
}
