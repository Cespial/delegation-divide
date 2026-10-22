import type { MetadataRoute } from "next";
import { SITE, ocupaciones, paises, resumen } from "@/lib/datos";

export default function sitemap(): MetadataRoute.Sitemap {
  const fecha = new Date(resumen.fecha);
  const fijas: [string, number][] = [["", 1], ["/adi", 1], ["/adi/occupations", 0.9], ["/adi/countries", 0.9], ["/adi/report", 0.9], ["/adi/methodology", 0.8], ["/adi/data", 0.8], ["/adi/compare", 0.5], ["/about", 0.4]];
  return [
    ...fijas.map(([r, p]) => ({ url: `${SITE}${r}`, lastModified: fecha, changeFrequency: "monthly" as const, priority: p })),
    ...ocupaciones.map((o) => ({ url: `${SITE}/adi/occupations/${o.isco}`, lastModified: fecha, changeFrequency: "yearly" as const, priority: 0.6 })),
    ...paises.map((p) => ({ url: `${SITE}/adi/countries/${p.iso3}`, lastModified: fecha, changeFrequency: "yearly" as const, priority: 0.6 })),
  ];
}
