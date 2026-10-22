import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import "./globals.css";
import { Marca } from "@/components/Marca";
import { Nav } from "@/components/Nav";
import { JsonLd } from "@/components/JsonLd";
import { AUTORES, HF, REPO, SITE, cifra, resumen } from "@/lib/datos";

const barlow = localFont({
  variable: "--f-barlow", display: "swap",
  src: [
    { path: "./fonts/Barlow-Regular.woff2", weight: "400", style: "normal" },
    { path: "./fonts/Barlow-Italic.woff2", weight: "400", style: "italic" },
    { path: "./fonts/Barlow-Medium.woff2", weight: "500", style: "normal" },
    { path: "./fonts/Barlow-SemiBold.woff2", weight: "600", style: "normal" },
    { path: "./fonts/Barlow-Bold.woff2", weight: "700", style: "normal" },
  ],
});
const cond = localFont({
  variable: "--f-cond", display: "swap",
  src: [
    { path: "./fonts/BarlowCondensed-SemiBold.woff2", weight: "600", style: "normal" },
    { path: "./fonts/BarlowCondensed-Bold.woff2", weight: "700", style: "normal" },
    { path: "./fonts/BarlowCondensed-ExtraBold.woff2", weight: "800", style: "normal" },
  ],
});
const mono = localFont({
  variable: "--f-mono", display: "swap",
  src: [
    { path: "./fonts/JetBrainsMono-Regular.woff2", weight: "400", style: "normal" },
    { path: "./fonts/JetBrainsMono-Medium.woff2", weight: "500", style: "normal" },
  ],
});

const DESCRIPCION = `An open, preregistered index of how much work AI agents can take over: ${cifra("cobertura.tareas")} task statements, ${cifra("cobertura.isco")} ISCO-08 occupations, ${cifra("cobertura.paises")} countries. ${cifra("titular.global.l2")}% of task time in world employment is at least partly delegable.`;

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: { default: "Agent Delegability Index (ADI): how much work can AI agents take over?", template: "%s · Agent Delegability Index" },
  description: DESCRIPCION,
  applicationName: "Agent Delegability Index",
  authors: AUTORES.map((a) => ({ name: a.nombre, url: `https://orcid.org/${a.orcid}` })),
  keywords: ["AI agents", "delegation", "future of work", "automation", "ISCO-08", "O*NET", "labour markets", "delegation divide", "AI exposure index"],
  alternates: { canonical: "/" },
  openGraph: { type: "website", siteName: "Agent Delegability Index", locale: "en_US" },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};
export const viewport: Viewport = { themeColor: "#f8f8f7", width: "device-width", initialScale: 1 };

const organizacion = {
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "WebSite", "@id": `${SITE}/#website`, url: SITE, name: "Agent Delegability Index", alternateName: "ADI", inLanguage: "en" },
    { "@type": "Organization", "@id": `${SITE}/#org`, name: "Agent Delegability Index", alternateName: "ADI", url: SITE, logo: `${SITE}/icon.svg`,
      sameAs: [REPO, HF, `https://doi.org/${resumen.doi_datos_concepto}`] },
  ],
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${barlow.variable} ${cond.variable} ${mono.variable}`}>
      <body>
        <a className="salto" href="#contenido">Skip to content</a>
        <header className="cabecera">
          <div className="envoltura">
            <Link href="/" className="marca"><Marca decorativa /><span>Agent Delegability Index · v{resumen.version}</span></Link>
            <Nav />
          </div>
        </header>
        <main id="contenido">{children}</main>
        <footer className="pie">
          <div className="envoltura pie-rejilla">
            <div>
              <h2>Agent Delegability Index</h2>
              <p>An open index of how much of each task an AI agent can take over, by {AUTORES.map((a) => a.nombre).join(" and ")}.
                Version {resumen.version}, October 2026. Preregistered at OSF.</p>
              <p className="nota">Text, data and figures: CC BY 4.0. Code: MIT. Includes information from O*NET 30.2 by USDOL/ETA (CC BY 4.0).</p>
            </div>
            <div>
              <h2>Explore</h2>
              <ul><li><Link href="/occupations">Occupations</Link></li><li><Link href="/countries">Countries</Link></li><li><Link href="/compare">Compare</Link></li><li><Link href="/methodology">Methodology</Link></li></ul>
            </div>
            <div>
              <h2>Cite and reuse</h2>
              <ul><li><Link href="/report">Report 2026.1</Link></li><li><Link href="/data">Data and API</Link></li>
                <li><a href={`https://doi.org/${resumen.doi_datos}`}>Dataset DOI</a></li><li><a href={`https://doi.org/${resumen.doi_prerregistro}`}>Preregistration</a></li></ul>
            </div>
            <div>
              <h2>Source</h2>
              <ul><li><a href={REPO}>GitHub</a></li><li><a href={HF}>Hugging Face</a></li><li><a href="/llms.txt">llms.txt</a></li><li><Link href="/about">About</Link></li></ul>
            </div>
          </div>
        </footer>
        <JsonLd datos={organizacion} />
      </body>
    </html>
  );
}
