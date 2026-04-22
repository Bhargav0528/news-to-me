/**
 * Estimate reading time for a body of text.
 * Assumes ~200 words per minute (typical newspaper reading speed).
 * Returns a formatted string like "3 min read".
 */
export function readingTime(text: string): string {
  const words = text.trim().split(/\s+/).length;
  const minutes = Math.ceil(words / 200);
  return `${minutes} min read`;
}
