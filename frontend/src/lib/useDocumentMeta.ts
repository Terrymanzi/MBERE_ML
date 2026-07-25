import { useEffect } from "react";

const BASE_TITLE = "MBERE ML Platform";

/** Sets the document title and meta description for the current page (no react-helmet dependency in this app). */
export function useDocumentMeta(title: string, description: string): void {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = `${title} — ${BASE_TITLE}`;

    let meta = document.querySelector<HTMLMetaElement>(
      'meta[name="description"]',
    );
    const previousDescription = meta?.getAttribute("content") ?? null;
    if (!meta) {
      meta = document.createElement("meta");
      meta.setAttribute("name", "description");
      document.head.appendChild(meta);
    }
    meta.setAttribute("content", description);

    return () => {
      document.title = previousTitle;
      if (meta && previousDescription !== null) {
        meta.setAttribute("content", previousDescription);
      }
    };
  }, [title, description]);
}
