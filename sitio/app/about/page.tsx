import type { Metadata } from "next";
import Link from "next/link";
import { JsonLd } from "@/components/JsonLd";
import { APOYO, AUTORES, LAB, REPO, SITE, cifra, resumen } from "@/lib/datos";
import { NOVEDADES, fechaCorta } from "@/lib/novedades";

export const metadata: Metadata = {
  title: "About",
  description: "Who is behind Balam Labs, the indices it publishes, how releases are versioned, how AI is used, and the licences for data, text and code.",
  alternates: { canonical: "/about" },
};

export default function Acerca() {
  return (
    <section className="seccion" style={{ borderTop: 0 }}>
      <div className="envoltura doc">
        <aside><span className="rotulo">About</span></aside>
        <article className="prosa">
          <h1 className="titulo" style={{ marginBottom: 20 }}>Open indices of what AI agents can do</h1>
          <p className="entrada">{LAB} (blabs) measures what AI agents can take over in real work, and publishes every rating, score and line of code
            behind its numbers. {LAB} is a name, not yet a company: the work is signed by its authors.</p>

          <h2 className="titulo-2">People</h2>
          <ul className="autores">
            {AUTORES.map((a) => <li key={a.orcid}><b>{a.nombre}</b><span>{a.afil}</span><a href={`https://orcid.org/${a.orcid}`}>ORCID {a.orcid}</a></li>)}
          </ul>
          <p style={{ marginTop: 16 }}>{APOYO}</p>

          <h2 className="titulo-2">Products</h2>
          <p><Link href="/adi">Agent Delegability Index</Link> (ADI): how much of each of {cifra("cobertura.tareas")} occupational tasks a current AI agent
            can carry out, carried to occupations and countries. First release v{resumen.version}, October 2026.</p>

          <h2 className="titulo-2">Releases</h2>
          <p>Each release has a version, a DOI and versioned paths: <code>/adi/v{resumen.version}/…</code> will always return these numbers, and a new edition
            gets new paths and a new DOI. Changes to a preregistered design are dated and listed under <Link href="/adi/methodology#updates">Updates</Link>.</p>
          <ul>{NOVEDADES.map((n) => <li key={n.titulo}>{fechaCorta(n.fecha)} · {n.href.startsWith("http") ? <a href={n.href}>{n.titulo}</a> : <Link href={n.href}>{n.titulo}</Link>}</li>)}</ul>

          <h2 className="titulo-2">Use of AI</h2>
          <p>Language models are the instrument of the ADI: Claude Sonnet 5.5 and Claude Haiku 5.5 rate the tasks, and Claude Opus 5.5 serves as an agentic
            validation panel. Every call is logged with the interface version, the model identifier, the prompt hash and the outcome. The human check was a blind
            rating led by a coauthor with student raters, who did not use AI tools while rating.</p>

          <h2 className="titulo-2">Licences</h2>
          <ul>
            <li>Data, reports and site text: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Cite the dataset, doi:<a href={`https://doi.org/${resumen.doi_datos}`}>{resumen.doi_datos}</a>.</li>
            <li>Code, Python package and MCP server: MIT, on <a href={REPO}>GitHub</a>.</li>
            <li>O*NET 30.2 task statements: U.S. Department of Labor, Employment and Training Administration, CC BY 4.0. ILOSTAT and World Bank data: CC BY 4.0.</li>
            <li>Typefaces: Barlow and JetBrains Mono, SIL Open Font License.</li>
            <li>Flags: <a href="https://github.com/lipis/flag-icons">flag-icons</a> 7.6.0 by Panayiotis Lipiridis, MIT. Map boundaries: Natural Earth 1:110m, public domain.</li>
          </ul>

          <h2 className="titulo-2">Corrections and questions</h2>
          <p>Open an issue on <a href={`${REPO}/issues`}>GitHub</a>. Corrections to published numbers are made in a new release and noted under Updates;
            published versions are never edited in place.</p>
        </article>
      </div>
      <JsonLd datos={{ "@context": "https://schema.org", "@type": "AboutPage", url: `${SITE}/about`, name: `About ${LAB}`,
        mainEntity: { "@type": "Organization", "@id": `${SITE}/#org`, name: LAB, alternateName: "blabs", url: SITE,
          member: AUTORES.map((a) => ({ "@type": "Person", name: a.nombre, affiliation: { "@type": "Organization", name: a.afil }, sameAs: `https://orcid.org/${a.orcid}` })) } }} />
    </section>
  );
}
