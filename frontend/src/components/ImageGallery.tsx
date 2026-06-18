import { useState } from "react";
import type { RetrievedImage } from "../types";
import { resolveFileUrl } from "../api/client";
import { ImageIcon } from "./icons";

export function ImageGallery({ images }: { images: RetrievedImage[] }) {
  const [zoom, setZoom] = useState<{ url: string; page: number | null } | null>(
    null,
  );

  // Only the server URL is browser-loadable; the local filesystem path
  // the backend also returns is not reachable from the browser.
  const renderable = images
    .map((img) => ({ ...img, url: resolveFileUrl(img.image_url) }))
    .filter((img): img is typeof img & { url: string } => Boolean(img.url));

  if (!renderable.length) return null;

  return (
    <div className="images">
      <h3 className="section-label">
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <ImageIcon size={14} /> Retrieved figures
        </span>
      </h3>
      <div className="images-grid">
        {renderable.map((img, i) => (
          <div
            key={i}
            className="img-card"
            onClick={() => setZoom({ url: img.url, page: img.page })}
          >
            <img src={img.url} alt={`Figure from page ${img.page ?? "?"}`} loading="lazy" />
            <div className="cap">Page {img.page ?? "?"}</div>
          </div>
        ))}
      </div>

      {zoom && (
        <div className="lightbox" onClick={() => setZoom(null)}>
          <img src={zoom.url} alt={`Figure from page ${zoom.page ?? "?"}`} />
          {zoom.page != null && <div className="lb-cap">Page {zoom.page}</div>}
        </div>
      )}
    </div>
  );
}
