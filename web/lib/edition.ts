import editionData from "@/public/data/edition.json";
import type { Edition } from "./edition-types";

/**
 * Load the current edition data.
 * Called at build time by server components — no runtime fetch.
 */
export async function getEdition(): Promise<Edition> {
  return editionData as Edition;
}

/**
 * Format a date string for display in the masthead.
 * Input: "2026-04-13"
 * Output: "April 13, 2026"
 */
export function formatEditionDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
