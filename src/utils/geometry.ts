export function calculatePixelDistance(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

export function convertToRealDistance(
  pixelDistance: number,
  scaleFactor: number
): number {
  return Math.round(pixelDistance * scaleFactor * 10) / 10;
}

export function formatDistance(distance: number, unit: string): string {
  return `${distance} ${unit}`;
}
