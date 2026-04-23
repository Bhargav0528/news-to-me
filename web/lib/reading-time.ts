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

/**
 * Reading time from a pre-computed word count.
 * Use this for article collections where you can't concatenate a single body.
 */
export function readingTimeFromWords(wordCount: number): string {
  const minutes = Math.max(1, Math.ceil(wordCount / 200));
  return `${minutes} min read`;
}
