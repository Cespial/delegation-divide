import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import "./globals.css";
import { MarcaLab } from "@/components/Marca";
import { Nav } from "@/components/Nav";
import { JsonLd } from "@/components/JsonLd";
import { APOYO, AUTORES, HF, LAB, REPO, SITE, cifra, resumen } from "@/lib/datos";

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

const DESCRIPCION = `Balam Labs builds open, preregistered indices of what AI agents can do. Its first, the Agent Delegability Index, rates ${cifra("cobertura.tareas")} task statements and finds that ${cifra("titular.global.l2")}% of task time in world employment is at least partly delegable to AI agents.`;

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: { default: "Balam Labs: independent indices of what AI agents can do", template: `%s · ${LAB}` },
  description: DESCRIPCION,
  applicationName: LAB,
  authors: AUTORES.map((a) => ({ name: a.nombre, url: `https://orcid.org/${a.orcid}` })),
  keywords: ["Balam Labs", "AI agents", "delegation", "future of work", "automation", "ISCO-08", "O*NET", "labour markets", "delegation divide", "AI exposure index"],
  alternates: { canonical: "/" },
  openGraph: { type: "website", siteName: LAB, locale: "en_US" },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};
export const viewport: Viewport = { themeColor: "#f8f8f7", width: "device-width", initialScale: 1 };

const organizacion = {
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "WebSite", "@id": `${SITE}/#website`, url: SITE, name: LAB, alternateName: "blabs", inLanguage: "en", publisher: { "@id": `${SITE}/#org` } },
    { "@type": "Organization", "@id": `${SITE}/#org`, name: LAB, alternateName: "blabs", url: SITE, logo: `${SITE}/icon.svg`,
      sameAs: [REPO, HF, `https://doi.org/${resumen.doi_datos_concepto}`] },
  ],
};

const NAV_LAB = [["/adi", "ADI"], ["/adi/report", "Report"], ["/adi/data", "Data"], ["/about", "About"]] as const;

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${barlow.variable} ${cond.variable} ${mono.variable}`}>
      <body>
        <a className="salto" href="#contenido">Skip to content</a>
        <header className="cabecera">
          <div className="envoltura">
            <Link href="/" className="marca"><MarcaLab /></Link>
            <Nav enlaces={NAV_LAB} etiqueta="Main" />
          </div>
        </header>
        <main id="contenido">{children}</main>
        <footer className="pie">
          <div className="envoltura pie-rejilla">
            <div>
              <h2>{LAB}</h2>
              <p>Independent, open indices of what AI agents can do, by {AUTORES.map((a) => a.nombre).join(" and ")}. Every rating, score and line of code is published.</p>
              <p className="nota">{APOYO} Text, data and figures: CC BY 4.0. Code: MIT. Includes information from O*NET 30.2 by USDOL/ETA (CC BY 4.0).</p>
            </div>
            <div>
              <h2>Agent Delegability Index</h2>
              <ul><li><Link href="/adi">Overview</Link></li><li><Link href="/adi/occupations">Occupations</Link></li><li><Link href="/adi/countries">Countries</Link></li><li><Link href="/adi/compare">Compare</Link></li><li><Link href="/adi/methodology">Methodology</Link></li></ul>
            </div>
            <div>
              <h2>Cite and reuse</h2>
              <ul><li><Link href="/adi/report">Report 2026.1</Link></li><li><Link href="/adi/data">Data and API</Link></li>
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
