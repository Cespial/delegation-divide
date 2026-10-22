import type { Metadata } from "next";
import Link from "next/link";
import { Cita } from "@/components/Cita";
import { JsonLd } from "@/components/JsonLd";
import { AUTORES, PDF_INFORME, REPO, SITE, TITULO_PAPER, cifra, informe, resumen } from "@/lib/datos";
import { citaInforme } from "@/lib/citar";

const TITULO = "The Delegation Divide";
const SUBTITULO = "An Open Index of AI-Agent Delegability across Occupations and Countries";
const RESUMEN = `${cifra("titular.global.l2")}% of task time in world employment is at least partly delegable to AI agents in 2026, and only ${cifra("titular.global.l3")}% can be handed over in full. `
  + `The Agent Delegability Index rates all ${cifra("cobertura.tareas")} O*NET task statements on a frozen, preregistered rubric of delegation levels and barriers, maps them to `
  + `${cifra("cobertura.isco")} ISCO-08 occupations and weights them by employment in ${cifra("cobertura.paises")} countries. Delegable work rises with income, from `
  + `${cifra("titular.ingreso.bajo.l2")}% in low-income to ${cifra("titular.ingreso.alto.l2")}% in high-income countries, because the physical barrier dominates the jobs poorer countries employ most. `
  + `Full delegation peaks for tasks that take a person about ${cifra("h4.pico.minutos")} minutes. A blind human rating of ${cifra("n.humano")} tasks agrees with the models at κ = ${cifra("agree.kappa.humano.modelo")}.`;

export const metadata: Metadata = {
  title: `${TITULO}: ADI Report 2026.1`,
  description: RESUMEN.slice(0, 300).replace(/\s\S*$/, "…"),
  alternates: { canonical: "/report" },
  openGraph: { type: "article", title: `${TITULO}: ADI Report 2026.1`, publishedTime: resumen.fecha, authors: AUTORES.map((a) => a.nombre) },
  // Highwire Press tags: what Google Scholar and reference managers read on a landing page.
  other: {
    citation_title: `${TITULO}: ${SUBTITULO}`,
    citation_author: AUTORES.map((a) => a.bib.replace(/\{\\'e\}/g, "é").replace(/\{\\~n\}/g, "ñ")),
    citation_publication_date: resumen.fecha.replaceAll("-", "/"),
    citation_technical_report_institution: "Agent Delegability Index",
    citation_technical_report_number: "ADI Report 2026.1",
    citation_language: "en",
    citation_abstract_html_url: `${SITE}/report`,
    citation_keywords: "AI agents; delegation; labour markets; ISCO-08; O*NET; delegation divide",
    ...(informe.pdf ? { citation_pdf_url: `${SITE}${PDF_INFORME}` } : {}),
    ...(resumen.doi_informe ? { citation_doi: resumen.doi_informe } : {}),
  },
};

const DIEZ: [string, string][] = [
  ["About a third of the world’s working time is at least partly delegable to AI agents.", `${cifra("titular.global.l2")}% of task time in world employment (95% interval ${cifra("titular.global.l2.lo")}–${cifra("titular.global.l2.hi")}%), across ${cifra("cobertura.empleo_millones")} million workers.`],
  ["Full delegation is rare.", `Only ${cifra("titular.global.l3")}% of task time can be handed over in full. Partial delegation is the most common rating of a task (${cifra("tareas.nivel2.pct")}% of statements).`],
  ["Delegable work rises with income: the delegation divide.", `From ${cifra("titular.ingreso.bajo.l2")}% in low-income countries to ${cifra("titular.ingreso.alto.l2")}% in high-income countries, ${cifra("h1.pendiente")} points per log point of GDP per capita.`],
  ["The divide comes from what people do, not from where they do it.", `The physical barrier is flagged on ${cifra("gg.9.barrera_fisica.pct")}% of task weight in elementary occupations against ${cifra("gg.1.barrera_fisica.pct")}% for managers.`],
  ["Office work is the most delegable.", `Managers reach ${cifra("gg.1.l2")}% and clerical support workers ${cifra("gg.4.l2")}%; elementary occupations ${cifra("gg.9.l2")}%.`],
  ["Countries range from Burundi to Singapore.", `From ${cifra("extremo.pais.bot1.l2")}% to ${cifra("extremo.pais.top1.l2")}%. Colombia ${cifra("pais.COL.l2")}%, Mexico ${cifra("pais.MEX.l2")}%, Brazil ${cifra("pais.BRA.l2")}%, the United States ${cifra("pais.USA.l2")}%.`],
  ["Delegation tracks exposure, and adds levels and barriers to it.", `r = ${cifra("h3.r.eloundou")} with Eloundou et al. and ${cifra("h3.r.felten")} with Felten et al., above the preregistered bound of 0.80.`],
  ["Full delegation peaks for tasks of about twelve minutes.", `The chance that an agent finishes a task alone rises with its length up to about ${cifra("h4.pico.minutos")} minutes of human time and falls after it.`],
  ["Use follows delegability.", `Across ${cifra("h2.n")} countries, observed AI use correlates with the index at r = ${cifra("h2.r.adi_uso")}. The preregistered adoption gap is not supported.`],
  ["The ratings hold up against people and agents.", `Models agree at κ = ${cifra("agree.kappa.sonnet_haiku")}; a blind human rating at κ = ${cifra("agree.kappa.humano.modelo")}; an agentic panel with web search at κ = ${cifra("agree.kappa.panel.modelo")}.`],
];
const CONTENIDO: [string, string[]][] = [
  ["Part I · Measuring delegation", ["1 From exposure to delegation", "2 Data", "3 Method"]],
  ["Part II · The delegation divide", ["4 The index", "5 The atlas: a delegation divide"]],
  ["Part III · Testing the index", ["6 Validation, convergence and adoption", "7 Limitations and ethics", "8 Conclusion"]],
  ["Annexes", ["A Scoring rubric", "B Crosswalk O*NET to ISCO-08", "C How to cite and use ADI"]],
];

export default function Informe() {
  const cita = citaInforme();
  return (
    <>
      <section className="seccion">
        <div className="envoltura informe-cab">
          <img src="/report/cover.webp" width={900} height={1165} alt={`Cover of the report ${TITULO}`} className="portada-informe" />
          <div>
            <span className="rotulo">ADI Report 2026.1 · {new Date(resumen.fecha).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })} · {informe.paginas} pages</span>
            <h1 className="titulo" style={{ margin: "14px 0 10px" }}>{TITULO}</h1>
            <p className="entrada" style={{ marginTop: 0 }}>{SUBTITULO}</p>
            <ul className="autores">
              {AUTORES.map((a) => <li key={a.orcid}><b>{a.nombre}</b><span>{a.afil}</span><a href={`https://orcid.org/${a.orcid}`}>ORCID {a.orcid}</a></li>)}
            </ul>
            {resumen.doi_informe && <p className="codigo" style={{ marginTop: 14 }}>doi:<a href={`https://doi.org/${resumen.doi_informe}`}>{resumen.doi_informe}</a></p>}
            <div className="botones">
              {informe.pdf
                ? <a className="boton lleno" href={PDF_INFORME} download>Download the PDF · {informe.mb} MB</a>
                : <span className="boton" aria-disabled="true">PDF on publication</span>}
              <a className="boton" href="#cite">Cite</a>
              <Link className="boton" href="/data">Data and code</Link>
            </div>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos-1-2">
          <div><span className="rotulo">Abstract</span></div>
          <div className="prosa"><p className="entrada" style={{ marginTop: 0 }}>{RESUMEN}</p>
            <p>The report is written for policy and general readers. The peer-review version is the paper, <i>{TITULO_PAPER}</i>, with the same data and numbers;
              every figure in both is drawn from one file of claims checked against the published outputs.</p></div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos-1-2">
          <div><span className="rotulo">Ten things to know</span></div>
          <ol className="diez">{DIEZ.map(([t, d]) => <li key={t}><p><b>{t}</b> {d}</p></li>)}</ol>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos-1-2">
          <div><span className="rotulo">Contents</span></div>
          <div className="contenido">{CONTENIDO.map(([p, caps]) => (
            <div key={p}><h2 className="titulo-3">{p}</h2><ul>{caps.map((c) => <li key={c}>{c}</li>)}</ul></div>
          ))}</div>
        </div>
      </section>

      <section className="seccion" id="cite">
        <div className="envoltura dos">
          <div><span className="rotulo">How to cite this report</span><div style={{ marginTop: 14 }}><Cita titulo="Text" cita={cita} /></div></div>
          <div><span className="rotulo">Licence and sources</span>
            <p style={{ marginTop: 14 }}>Text and figures: CC BY 4.0. Data: CC BY 4.0, doi:<a href={`https://doi.org/${resumen.doi_datos}`}>{resumen.doi_datos}</a>.
              Code: MIT, <a href={REPO}>GitHub</a>. Preregistration: doi:<a href={`https://doi.org/${resumen.doi_prerregistro}`}>{resumen.doi_prerregistro}</a>.</p>
            <p>To cite a single occupation or country, use the citation on its page; it names the record and the dataset version.</p>
          </div>
        </div>
      </section>
      <JsonLd datos={{
        "@context": "https://schema.org", "@type": ["Report", "ScholarlyArticle"], name: `${TITULO}: ${SUBTITULO}`, headline: TITULO, alternativeHeadline: SUBTITULO,
        abstract: RESUMEN, url: `${SITE}/report`, datePublished: resumen.fecha, inLanguage: "en", reportNumber: "ADI Report 2026.1", numberOfPages: informe.paginas,
        image: `${SITE}/report/cover.webp`, license: "https://creativecommons.org/licenses/by/4.0/", isAccessibleForFree: true,
        author: AUTORES.map((a) => ({ "@type": "Person", name: a.nombre, affiliation: { "@type": "Organization", name: a.afil }, sameAs: `https://orcid.org/${a.orcid}` })),
        publisher: { "@type": "Organization", name: "Agent Delegability Index", url: SITE },
        isBasedOn: { "@type": "Dataset", name: "Agent Delegability Index (ADI) v2026.1", identifier: `https://doi.org/${resumen.doi_datos}` },
        ...(resumen.doi_informe ? { identifier: `https://doi.org/${resumen.doi_informe}`, sameAs: `https://doi.org/${resumen.doi_informe}` } : {}),
        ...(informe.pdf ? { encoding: { "@type": "MediaObject", contentUrl: `${SITE}${PDF_INFORME}`, encodingFormat: "application/pdf" } } : {}),
      }} />
    </>
  );
}
