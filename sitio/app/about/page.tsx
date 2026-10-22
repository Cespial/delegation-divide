import type { Metadata } from "next";
import Link from "next/link";
import { JsonLd } from "@/components/JsonLd";
import { AUTORES, REPO, SITE, resumen } from "@/lib/datos";

export const metadata: Metadata = {
  title: "About",
  description: "Who builds the Agent Delegability Index, how releases are versioned, how AI was used, and the licences for data, text and code.",
  alternates: { canonical: "/about" },
};

export default function Acerca() {
  return (
    <section className="seccion">
      <div className="envoltura doc">
        <aside><span className="rotulo">About</span></aside>
        <article className="prosa">
          <h1 className="titulo" style={{ marginBottom: 20 }}>An open index, versioned and citable</h1>
          <p className="entrada">The Agent Delegability Index is an open research project. It measures how much of the world’s work AI agents can take over,
            task by task, and publishes every rating, score and line of code behind the numbers.</p>

          <h2 className="titulo-2">Authors</h2>
          <ul className="autores">
            {AUTORES.map((a) => <li key={a.orcid}><b>{a.nombre}</b><span>{a.afil}</span><a href={`https://orcid.org/${a.orcid}`}>ORCID {a.orcid}</a></li>)}
          </ul>
          <p style={{ marginTop: 16 }}>Produced with the support of INPLUX S.A.S., Medellín.</p>

          <h2 className="titulo-2">Releases</h2>
          <p>Each release has a version (this one is v{resumen.version}), a DOI and versioned paths: <code>/adi/v{resumen.version}/…</code> will always return
            these numbers, and a new edition gets new paths and a new DOI. Changes to the preregistered design are dated and listed under{" "}
            <Link href="/methodology#updates">Updates</Link>.</p>

          <h2 className="titulo-2">Use of AI</h2>
          <p>Language models are the instrument of this index: Claude Sonnet 5.5 and Claude Haiku 5.5 rate the tasks, and Claude Opus 5.5 serves as an agentic
            validation panel. Every call is logged with the interface version, the model identifier, the prompt hash and the outcome. The human check was a blind
            rating led by a coauthor with student raters, who did not use AI tools while rating.</p>

          <h2 className="titulo-2">Licences</h2>
          <ul>
            <li>Data, report and site text: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Cite the dataset, doi:<a href={`https://doi.org/${resumen.doi_datos}`}>{resumen.doi_datos}</a>.</li>
            <li>Code, Python package and MCP server: MIT, on <a href={REPO}>GitHub</a>.</li>
            <li>O*NET 30.2 task statements: U.S. Department of Labor, Employment and Training Administration, CC BY 4.0. ILOSTAT and World Bank data: CC BY 4.0.</li>
            <li>Typefaces: Barlow and JetBrains Mono, SIL Open Font License.</li>
          </ul>

          <h2 className="titulo-2">Corrections and questions</h2>
          <p>Open an issue on <a href={`${REPO}/issues`}>GitHub</a>. Corrections to published numbers are made in a new release and noted under Updates;
            published versions are never edited in place.</p>
        </article>
      </div>
      <JsonLd datos={{ "@context": "https://schema.org", "@type": "AboutPage", url: `${SITE}/about`, name: "About the Agent Delegability Index",
        mainEntity: AUTORES.map((a) => ({ "@type": "Person", name: a.nombre, affiliation: { "@type": "Organization", name: a.afil }, sameAs: `https://orcid.org/${a.orcid}` })) }} />
    </section>
  );
}
