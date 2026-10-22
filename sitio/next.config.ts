import type { NextConfig } from "next";

// Static site: every page is prerendered at build time from sitio/datos/*.json (see datos/exportar.py).
// The lab lives at the root and the ADI under /adi. Its JSON API (/adi/v2026.1/…) is meant for agents and scripts,
// so it is served with open CORS and a long cache. The ADI pages first lived at the root: those paths redirect.
const VIEJAS = ["occupations", "countries", "compare", "methodology", "report", "data"];

const config: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  outputFileTracingIncludes: { "/**": ["./datos/**/*.json", "./fonts-og/*.ttf"] },
  async headers() {
    return [
      {
        source: "/adi/v2026.1/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Cache-Control", value: "public, max-age=3600, s-maxage=86400" },
        ],
      },
      { source: "/data/:path*", headers: [{ key: "Access-Control-Allow-Origin", value: "*" }] },
    ];
  },
  async redirects() {
    return VIEJAS.flatMap((r) => [
      { source: `/${r}`, destination: `/adi/${r}`, permanent: true },
      // /report/*.pdf|webp and /data/*.csv are files, so only page paths (no dot) redirect.
      ...(r === "report" || r === "data" ? [] : [{ source: `/${r}/:p([^.]+)`, destination: `/adi/${r}/:p`, permanent: true }]),
    ]);
  },
};

export default config;
