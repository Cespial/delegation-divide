import type { Metadata } from "next";
import Link from "next/link";
import { Nivel } from "@/components/Barra";
import { JsonLd } from "@/components/JsonLd";
import { NIVELES, SITE, cifra, resumen } from "@/lib/datos";

export const metadata: Metadata = {
  title: "Methodology",
  description: `How the Agent Delegability Index is built: a frozen, preregistered rubric of four delegation levels and four barriers, two rating models over ${cifra("cobertura.tareas")} O*NET task statements, a crosswalk to ISCO-08 and employment weights for ${cifra("cobertura.paises")} countries.`,
  alternates: { canonical: "/adi/methodology" },
};

const DEF = [
  "The agent cannot perform or materially speed up any substantial part of the task.",
  "A human performs the task while the AI assists step by step with drafts, searches or suggestions; the human produces the output.",
  "An agent executes substantial sub-steps end to end from a goal, while a human still performs at least one essential step or reviews the work before use.",
  "An agent completes the whole task end to end, to the quality a competent worker would accept, given only the goal and access.",
];
const BAR = [
  ["Physical presence", "the task needs presence or manipulation of objects, people or places."],
  ["Accountability", "law, licence or liability requires a human to perform or sign."],
  ["Trust and care", "the task depends on in-person trust, care or persuasion."],
  ["Access to systems", "the task depends on systems, data or places an agent would normally not reach."],
];
const SECC = [["motivation", "Motivation"], ["measures", "What it measures"], ["results", "Results"], ["takeaways", "Key takeaways"],
  ["method", "Method"], ["validation", "Validation"], ["limits", "Limits"], ["updates", "Updates"]];

export default function Metodologia() {
  return (
    <section className="seccion">
      <div className="envoltura doc">
        <aside>
          <span className="rotulo">Methodology · v{resumen.version}</span>
          <nav aria-label="On this page"><ol>{SECC.map(([id, t]) => <li key={id}><a href={`#${id}`}>{t}</a></li>)}</ol></nav>
        </aside>
        <article className="prosa">
          <h1 className="titulo" style={{ marginBottom: 20 }}>How the index is built</h1>
          <p className="entrada">The index asks one question of every task a worker does: how much of it could a current AI agent carry out on its own,
            given only the goal and access? It answers on a fixed scale, for every task statement in O*NET, and adds the answers up for
            occupations and countries.</p>

          <h2 className="titulo-2" id="motivation">Motivation</h2>
          <p>Existing measures score exposure: whether a language model could make a task faster for the person who does it. Agents change the
            question. A system that runs software, reads and writes files and calls other systems can take a task over, not just assist with it.
            Delegation is a change of owner, and exposure indices do not measure it. They also cover mostly the United States, while most of the
            world’s workers live elsewhere, in countries whose jobs look very different.</p>

          <h2 className="titulo-2" id="measures">What it measures</h2>
          <p>Each task gets one of four levels. The levels form a ladder: at L1 the machine contributes, at L2 it executes, at L3 it finishes.</p>
          <dl className="niveles">
            {NIVELES.map((n, i) => (
              <div key={n.k}><dt><Nivel n={i} /> {n.nombre}</dt><dd>{DEF[i]} <span className="nota">{cifra(`tareas.nivel${i}.pct`)}% of task statements.</span></dd></div>
            ))}
          </dl>
          <p>Alongside the level, the rubric flags four barriers that keep a task from moving up the ladder:</p>
          <ul>{BAR.map(([t, d]) => <li key={t}><b>{t}</b>: {d}</li>)}</ul>
          <p>It also records the share of the task’s working time an agent could take over and the minutes a competent person needs for one instance.
            Three indices follow, each a weighted share of an occupation’s task time:</p>
          <div className="tabla-marco"><table className="tabla"><thead><tr><th>Index</th><th>What it counts</th><th className="n">World, 2026</th></tr></thead><tbody>
            <tr className="destacada"><td><b>ADI</b></td><td>Task time at partial or full delegation (L2–L3). The headline index.</td><td className="n valor">{cifra("titular.global.l2")}%</td></tr>
            <tr><td><b>ADI3</b></td><td>Task time at full delegation (L3).</td><td className="n valor">{cifra("titular.global.l3")}%</td></tr>
            <tr><td><b>ADIs</b></td><td>Expected share of working time an agent could take over.</td><td className="n valor">{cifra("titular.global.share")}%</td></tr>
          </tbody></table></div>

          <h2 className="titulo-2" id="results">Results</h2>
          <p>{cifra("titular.global.l2")}% of task time in world employment is at least partly delegable to AI agents in 2026 (95% interval {cifra("titular.global.l2.lo")}–{cifra("titular.global.l2.hi")}%),
            across {cifra("cobertura.empleo_millones")} million workers in {cifra("cobertura.paises")} countries. Only {cifra("titular.global.l3")}% can be handed over in full.
            The index goes from {cifra("titular.ingreso.bajo.l2")}% in low-income countries to {cifra("titular.ingreso.alto.l2")}% in high-income countries, and from {cifra("extremo.pais.bot1.l2")}%
            in {cifra("extremo.pais.bot1.nombre")} to {cifra("extremo.pais.top1.l2")}% in {cifra("extremo.pais.top1.nombre")}. Explore it by <Link href="/adi/occupations">occupation</Link> and
            by <Link href="/adi/countries">country</Link>.</p>

          <h2 className="titulo-2" id="takeaways">Key takeaways</h2>
          <ul className="claves">
            <li><b>A delegation divide.</b> Each log point of GDP per capita adds {cifra("h1.pendiente")} percentage points of delegable work (95% interval {cifra("h1.pendiente.lo")}–{cifra("h1.pendiente.hi")}, R² = {cifra("h1.r2")}, {cifra("h1.n")} countries).</li>
            <li><b>The divide is compositional.</b> Poorer countries employ more people in farming, crafts and elementary jobs, where the physical barrier is flagged on {cifra("gg.9.barrera_fisica.pct")}% of task weight, against {cifra("gg.1.barrera_fisica.pct")}% for managers.</li>
            <li><b>Delegation tracks exposure.</b> Across occupations the index correlates with Eloundou et al. at r = {cifra("h3.r.eloundou")} and with Felten et al. at r = {cifra("h3.r.felten")}, above the preregistered bound of 0.80. What it adds is how far delegation goes, what stops it, and global reach.</li>
            <li><b>Full delegation peaks for tasks of about {cifra("h4.pico.minutos")} minutes</b> of human time and falls for longer ones.</li>
            <li><b>Use follows delegability.</b> Across {cifra("h2.n")} countries observed AI use correlates with the index at r = {cifra("h2.r.adi_uso")}; the preregistered adoption gap in middle-income countries is not supported.</li>
          </ul>

          <h2 className="titulo-2" id="method">Method</h2>
          <h3 className="titulo-3">Rubric and raters</h3>
          <p>A single rubric, frozen and hashed at registration, asks for one JSON object per task: level, share, human minutes, four barrier flags and a confidence
            label. It contains no example tasks, so no task can anchor another. Two models rate all {cifra("cobertura.tareas")} O*NET 30.2 task statements, one task per call:
            Claude Sonnet 5.5 as primary rater and Claude Haiku 5.5 as secondary, in a neutral configuration with no tools. The consensus level is the level both give when
            they agree and the lower one when they do not.</p>
          <h3 className="titulo-3">Aggregation</h3>
          <p>Task weights are importance times frequency, normalised within each O*NET occupation and carried through a SOC-to-ISCO-08 bridge to {cifra("cobertura.isco")} unit
            groups. A country’s index is the employment-weighted mean over the occupational groups it reports to ILOSTAT, at two digits for {cifra("cobertura.paises.2d")} countries and
            one digit for {cifra("cobertura.paises.1d")}. Within a reported group, unit groups are weighted with microdata: United States OES for high-income countries, Colombia’s
            GEIH for the rest, a stated loan.</p>
          <h3 className="titulo-3" id="countries">Country decomposition and position relative to income</h3>
          <p>Country pages split the index into the nine ISCO-08 major groups: each group’s share of employment, its index with that country’s mix of unit groups,
            and its contribution in points, which sum to the country’s ADI. The “vs income” figure is the country’s ADI minus the delegation-divide line
            (ADI regressed on log GDP per capita, slope {cifra("h1.pendiente")}) at its GDP per capita; within ±1.5 points it reads as in line with income. Barriers are
            the employment-weighted share of task weight carrying each flag. These are site calculations from the published v2026.1 figures and are not part of the
            dataset on Zenodo or the API.</p>
          <h3 className="titulo-3">Uncertainty</h3>
          <p>Every interval is a 95% percentile interval from 1,000 bootstrap draws over tasks, resampled within occupation, that recompute the indices, the headline and
            the regressions. A placebo that shuffles ratings across occupations confirms that the index carries occupation-specific information.</p>

          <h2 className="titulo-2" id="validation">Validation</h2>
          <div className="tabla-marco"><table className="tabla"><thead><tr><th>Check</th><th className="n">Agreement (quadratic κ)</th></tr></thead><tbody>
            <tr><td>Sonnet against Haiku, all tasks</td><td className="n valor">{cifra("agree.kappa.sonnet_haiku")}</td></tr>
            <tr><td>Blind human rating of {cifra("n.humano")} tasks, led by a coauthor with student raters, against the model consensus</td><td className="n valor">{cifra("agree.kappa.humano.modelo")}</td></tr>
            <tr><td>Agentic panel with web search, {cifra("n.panel")} tasks, against the model consensus (not human validation)</td><td className="n valor">{cifra("agree.kappa.panel.modelo")}</td></tr>
            <tr><td>Test–retest, Sonnet</td><td className="n valor">{cifra("agree.testretest.sonnet.kappa")}</td></tr>
          </tbody></table></div>
          <p className="nota" style={{ marginTop: 10 }}>Values above 0.80 indicate strong agreement.</p>

          <h2 className="titulo-2" id="limits">Limits</h2>
          <p>The ratings are judgements by language models about what agents can do, checked against people on a sample; they are not observations of agents at work.
            The human rating was led by a coauthor, and because individual contributions were not recorded it is analysed as one rating. O*NET describes United States jobs,
            and the same occupation may be organised differently elsewhere. The within-group weights for middle- and low-income countries come from one country. The
            breakdowns by sex, age and formality exist only for Colombia and are exploratory.</p>

          <h2 className="titulo-2" id="updates">Updates</h2>
          <ul className="feed">
            <li><span className="codigo">22 Oct 2026</span><div><h3 className="titulo-3">v2026.1 · first release</h3>
              <p>Index, atlas, report and dataset (doi:{resumen.doi_datos}). Hypotheses, rubric and analysis plan were preregistered on OSF (doi:{resumen.doi_prerregistro}) before the main scoring run.</p></div></li>
            <li><span className="codigo">D4 · 22 Oct</span><div><h3 className="titulo-3">Household microdata: Colombia only</h3>
              <p>Breakdowns by sex, age and formality are computed only for Colombia with GEIH 2024–2026. Mexico’s ENOE codes occupation at one digit; Brazil’s PNADC and Peru’s ENAHO are not yet processed. The comparisons with the ILO 2025 index and the Agentic Adoption Index are deferred.</p></div></li>
            <li><span className="codigo">D3 · 21 Oct</span><div><h3 className="titulo-3">Four country-years excluded for data quality</h3>
              <p>Suriname, Senegal, Comoros and Hong Kong report occupations covering less than 75% of employment or fewer than six major groups. The rule was added after seeing results; with all 150 countries the headline is {Number(cifra("d3.titular.l2.150")).toFixed(1)}% and the slope {cifra("d3.h1.pendiente.150")}, against {cifra("h1.pendiente")}.</p></div></li>
            <li><span className="codigo">D2 · 21 Oct</span><div><h3 className="titulo-3">Validation redesigned before any result was opened</h3>
              <p>Three human raters on 1,500 tasks became a blind rating of {cifra("n.humano")} tasks, led by a coauthor with student raters, plus an agentic panel reported as non-human validation.</p></div></li>
            <li><span className="codigo">D1 · 20 Oct</span><div><h3 className="titulo-3">Within-group employment weights</h3>
              <p>No country publishes four-digit employment in ILOSTAT, so unit groups are weighted with US OES for high-income countries and Colombia’s GEIH for the rest. Equal weights give {cifra("titular.global.l2.iguales")}%.</p></div></li>
          </ul>
          <p className="nota" style={{ marginTop: 14 }}>Full record of deviations: <a href="https://github.com/Cespial/delegation-divide/blob/main/docs/DESVIACIONES.md">docs/DESVIACIONES.md</a> (Spanish).
            The rubric is reproduced in Annex A of the <Link href="/adi/report">report</Link>.</p>
        </article>
      </div>
      <JsonLd datos={{ "@context": "https://schema.org", "@type": "TechArticle", headline: "How the Agent Delegability Index is built", url: `${SITE}/adi/methodology`,
        isPartOf: { "@type": "WebSite", url: SITE }, about: { "@type": "Dataset", identifier: `https://doi.org/${resumen.doi_datos}` } }} />
    </section>
  );
}
