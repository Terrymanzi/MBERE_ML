import { slugify } from "./slugify";

export interface LegalHeading {
  id: string;
  text: string;
}

/** Parses `##` headings out of raw legal markdown, in document order, for the table of contents. */
export function extractHeadings(markdown: string): LegalHeading[] {
  const headings: LegalHeading[] = [];
  for (const line of markdown.split("\n")) {
    const match = /^##\s+(.+)$/.exec(line.trim());
    if (match) {
      const text = match[1].trim();
      headings.push({ id: slugify(text), text });
    }
  }
  return headings;
}
