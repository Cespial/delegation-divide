import type { MetadataRoute } from "next";
import { SITE, ocupaciones, paises, resumen } from "@/lib/datos";

export default function sitemap(): MetadataRoute.Sitemap {
  const fecha = new Date(resumen.fecha);
  const fijas: [string, number][] = [["", 1], ["/occupations", 0.9], ["/countries", 0.9], ["/report", 0.9], ["/methodology", 0.8], ["/data", 0.8], ["/compare", 0.5], ["/about", 0.4]];
  return [
    ...fijas.map(([r, p]) => ({ url: `${SITE}${r}`, lastModified: fecha, changeFrequency: "monthly" as const, priority: p })),
    ...ocupaciones.map((o) => ({ url: `${SITE}/occupations/${o.isco}`, lastModified: fecha, changeFrequency: "yearly" as const, priority: 0.6 })),
    ...paises.map((p) => ({ url: `${SITE}/countries/${p.iso3}`, lastModified: fecha, changeFrequency: "yearly" as const, priority: 0.6 })),
  ];
}
