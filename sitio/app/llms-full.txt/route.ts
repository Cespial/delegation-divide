import fs from "node:fs";
import path from "node:path";
import { SITE } from "@/lib/datos";

export const dynamic = "force-static";

// The repository's llms-full.txt (copied by datos/exportar.py), with the GitHub Pages base replaced by this site's.
export function GET() {
  const t = fs.readFileSync(path.join(process.cwd(), "datos", "llms-full.txt"), "utf8").replaceAll("https://cespial.github.io/delegation-divide", SITE);
  return new Response(t, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
