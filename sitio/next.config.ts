import type { NextConfig } from "next";

// Static site: every page is prerendered at build time from sitio/datos/*.json (see datos/exportar.py).
// The JSON API under /adi/ is meant for agents and scripts, so it is served with open CORS and a long cache.
const config: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  outputFileTracingIncludes: { "/**": ["./datos/**/*.json", "./fonts-og/*.ttf"] },
  async headers() {
    return [
      {
        source: "/adi/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Cache-Control", value: "public, max-age=3600, s-maxage=86400" },
        ],
      },
      { source: "/data/:path*", headers: [{ key: "Access-Control-Allow-Origin", value: "*" }] },
    ];
  },
};

export default config;
