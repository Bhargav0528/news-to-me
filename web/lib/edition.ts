import editionData from "@/public/data/edition.json";
import type { Edition } from "./edition-types";

/**
 * Load the current edition data.
 * Static import at build time — no runtime fetch, no revalidation needed.
 * Daily cron (PO-5, Sprint 3) will rebuild the whole site with fresh data.
 */
export function getEdition(): Edition {
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
