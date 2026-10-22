import type { MetadataRoute } from "next";
import { SITE } from "@/lib/datos";

// Open to every crawler, AI crawlers included: being read and cited is the point of the index.
export default function robots(): MetadataRoute.Robots {
  return { rules: [{ userAgent: "*", allow: "/" }], sitemap: `${SITE}/sitemap.xml`, host: SITE };
}
