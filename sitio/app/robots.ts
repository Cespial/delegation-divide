import type { MetadataRoute } from "next";
import { INDEXAR, SITE } from "@/lib/datos";

// Open to every crawler, AI crawlers included, once INDEXAR=1: being read and cited is the point of the index.
export default function robots(): MetadataRoute.Robots {
  if (!INDEXAR) return { rules: [{ userAgent: "*", disallow: "/" }] };
  return { rules: [{ userAgent: "*", allow: "/" }], sitemap: `${SITE}/sitemap.xml`, host: SITE };
}
