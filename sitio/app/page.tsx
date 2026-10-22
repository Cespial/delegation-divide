import Link from "next/link";
import { Barra } from "@/components/Barra";
import { Buscador } from "@/components/Buscador";
import { JsonLd } from "@/components/JsonLd";
import { Pestanas } from "@/components/Pestanas";
import { jsonDataset } from "@/lib/jsonld";
import { ENLACE_INFORME, INGRESOS, INSTALAR, N_OCUP, REPO, cifra, grupos, informe, ocupaciones, resumen } from "@/lib/datos";

export default function Inicio() {
  const porL2 = [...grupos].sort((a, b) => b.l2 - a.l2);
  const porL3 = [...grupos].sort((a, b) => b.l3 - a.l3);
  const top = [...ocupaciones].sort((a, b) => a.rk - b.rk);
  const items = ocupaciones.map((o) => ({ href: `/occupations/${o.isco}`, nombre: o.titulo, codigo: o.isco, valor: `${o.l2.toFixed(1)}%` }));
  const dataset = jsonDataset();
  return (
    <>
      <section className="portada">
        <div className="envoltura">
          <div className="portada-rejilla">
            <div>
              <span className="rotulo">Agent Delegability Index · <b>v{resumen.version}</b> · updated October 2026</span>
              <h1 className="titulo">How much of the world’s work can AI agents take over?</h1>
              <p className="entrada" style={{ marginTop: 24 }}>
                The index rates every one of {cifra("cobertura.tareas")} occupational task statements for how much of it a current AI agent could carry out,
                from helping a person to finishing the job alone, and carries the ratings to {cifra("cobertura.isco")} occupations and {cifra("cobertura.paises")} countries.
              </p>
            </div>
            <div className="titular">
              <span className="cifra">{cifra("titular.global.l2")}<small>%</small></span>
              <p>of task time in world employment is at least partly delegable to AI agents in 2026. Only {cifra("titular.global.l3")}% can be handed over in full.</p>
              <div className="intervalo">95% interval {cifra("titular.global.l2.lo")}–{cifra("titular.global.l2.hi")}% · employment-weighted</div>
            </div>
          </div>
          <div className="escalera" aria-label="ADI by country income group">
            {INGRESOS.map((g, i) => (
              <Link key={g.k} href={`/countries?income=${g.k}`} className="escalon" style={{ minHeight: 120 + 34 * i }}>
                <span className="rotulo">{g.nombre}</span>
                <div><span className="cifra">{cifra(`titular.ingreso.${g.id}.l2`)}<small>%</small></span>
                  <div className="paises">{cifra(`cobertura.ingreso.${g.id}.paises`)} countries</div></div>
              </Link>
            ))}
          </div>
          <div className="pie-escalera">
            <span><b>The delegation divide.</b> Each log point of GDP per capita adds {cifra("h1.pendiente")} percentage points of delegable work.</span>
            <Link href="/countries">Open the country atlas</Link>
          </div>
        </div>
      </section>

      <section className="seccion" style={{ borderTop: 0 }}>
        <div className="envoltura">
          <div className="baldosas">
            <div className="baldosa"><span className="rotulo">Full delegation</span><span className="cifra">{cifra("titular.global.l3")}%</span>
              <p>of task time can be handed over to an agent in full, given only the goal and access.</p></div>
            <div className="baldosa"><span className="rotulo">Most likely to be handed over</span><span className="cifra">{cifra("h4.pico.minutos")} min</span>
              <p>Full delegation is most likely for tasks that take a person about twelve minutes.</p></div>
            <div className="baldosa"><span className="rotulo">Human check</span><span className="cifra">κ {cifra("agree.kappa.humano.modelo")}</span>
              <p>agreement of a blind human rating of {cifra("n.humano")} tasks, led by a coauthor with student raters, with the models.</p></div>
            <div className="baldosa"><span className="rotulo">Observed use</span><span className="cifra">r {cifra("h2.r.adi_uso")}</span>
              <p>correlation between delegability and AI use across {cifra("h2.n")} countries (Anthropic Economic Index).</p></div>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado">
            <div><span className="rotulo">Leaderboard · ISCO-08 major groups</span>
              <h2 className="titulo-2" style={{ marginTop: 10 }}>Office work is the most delegable; manual work the least</h2>
              <p>Share of task weight an agent can at least partly take over, averaged over unit groups with world employment weights. Whiskers: 95% bootstrap interval.</p></div>
            <Link className="boton" href="/occupations">All {N_OCUP} occupations</Link>
          </div>
          <Pestanas etiquetas={["Delegability (ADI)", "Full delegation (ADI3)", "Barriers"]}>
            {[
              <div className="tabla-marco" key="l2"><table className="tabla"><thead><tr><th>#</th><th>Major group</th><th className="barra-celda">ADI, % of task time at L2–L3</th><th className="n">ADI</th><th className="n">95% interval</th></tr></thead>
                <tbody>{porL2.map((g, i) => (
                  <tr key={g.gg}><td className="puesto">{i + 1} of 9</td><td><Link href={`/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
                    <td className="barra-celda"><Barra v={g.l2} lo={g.lo} hi={g.hi} fuerte={i === 0} /></td><td className="n valor">{g.l2.toFixed(1)}</td><td className="n ic">{g.lo.toFixed(1)}–{g.hi.toFixed(1)}</td></tr>
                ))}</tbody></table></div>,
              <div className="tabla-marco" key="l3"><table className="tabla"><thead><tr><th>#</th><th>Major group</th><th className="barra-celda">ADI3, % of task time at L3 (scale 0–10)</th><th className="n">ADI3</th></tr></thead>
                <tbody>{porL3.map((g, i) => (
                  <tr key={g.gg}><td className="puesto">{i + 1} of 9</td><td><Link href={`/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
                    <td className="barra-celda"><Barra v={g.l3} max={10} fuerte={i === 0} /></td><td className="n valor">{g.l3.toFixed(1)}</td></tr>
                ))}</tbody></table></div>,
              <div className="tabla-marco" key="b"><table className="tabla"><thead><tr><th>Major group</th><th className="n">Physical presence</th><th className="n">Accountability</th><th className="n">Trust and care</th><th className="n">Access to systems</th></tr></thead>
                <tbody>{[...grupos].sort((a, b) => Number(a.gg) - Number(b.gg)).map((g) => (
                  <tr key={g.gg}><td><Link href={`/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
                    {g.b.map((v, j) => <td className="n valor" key={j} style={{ color: v >= 60 ? "var(--tinta)" : "var(--tinta-2)", fontWeight: v >= 60 ? 700 : 500 }}>{v.toFixed(0)}%</td>)}</tr>
                ))}</tbody></table>
                <p className="nota" style={{ marginTop: 10 }}>Share of task weight flagged by each barrier. Barriers are not exclusive. Bold: 60% or more.</p></div>,
            ]}
          </Pestanas>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div>
            <span className="rotulo">Look up an occupation</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 18px" }}>Find your job in the index</h2>
            <Buscador items={items} placeholder="Occupation title or ISCO-08 code, e.g. accountant or 2411" />
          </div>
          <div>
            <span className="rotulo">At the extremes</span>
            <div className="tabla-marco" style={{ marginTop: 18 }}><table className="tabla"><thead><tr><th>Most delegable</th><th className="n">ADI</th></tr></thead>
              <tbody>{top.slice(0, 5).map((o) => <tr key={o.isco}><td><Link href={`/occupations/${o.isco}`}>{o.titulo}</Link> <span className="codigo">{o.isco}</span></td><td className="n valor">{o.l2.toFixed(1)}</td></tr>)}</tbody>
              <thead><tr><th>Least delegable</th><th className="n">ADI</th></tr></thead>
              <tbody>{top.slice(-5).reverse().map((o) => <tr key={o.isco}><td><Link href={`/occupations/${o.isco}`}>{o.titulo}</Link> <span className="codigo">{o.isco}</span></td><td className="n valor">{o.l2.toFixed(1)}</td></tr>)}</tbody>
            </table></div>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">Latest</span>
          <ul className="feed">
            <li><span className="codigo">22 Oct 2026</span><div><h3 className="titulo-3"><Link href="/report">The Delegation Divide: ADI Report 2026.1</Link></h3>
              <p>The results in {informe.paginas} pages for policy and general readers, with a profile of Colombia by sex, age and formality.</p></div><a className="boton" href={ENLACE_INFORME}>{informe.pdf ? "PDF" : "Report"}</a></li>
            <li><span className="codigo">22 Oct 2026</span><div><h3 className="titulo-3"><a href={`https://doi.org/${resumen.doi_datos}`}>Dataset v2026.1 on Zenodo</a></h3>
              <p>Ratings for every task, scores for every occupation and country, the rubric, and the code that builds them. doi:{resumen.doi_datos}</p></div><Link className="boton" href="/data">Data</Link></li>
            <li><span className="codigo">Oct 2026</span><div><h3 className="titulo-3"><a href={`https://doi.org/${resumen.doi_prerregistro}`}>Preregistration on OSF</a></h3>
              <p>Hypotheses, rubric and analysis plan were registered before the main scoring run. Deviations are listed in the methodology.</p></div><Link className="boton" href="/methodology#updates">Changes</Link></li>
          </ul>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado"><div><span className="rotulo">For AI agents and scripts</span>
            <h2 className="titulo-2" style={{ marginTop: 10 }}>Query and cite the index from code</h2>
            <p>Every record carries its citation. No key, no rate limit.</p></div></div>
          <div className="agentes">
            <div><span className="rotulo">JSON</span><code>/adi/v2026.1/isco/2512.json</code><p>One static file per occupation and per country.</p></div>
            <div><span className="rotulo">Python</span><code>{INSTALAR}</code><p>Then <code style={{ display: "inline" }}>adi lookup 2512</code>.</p></div>
            <div><span className="rotulo">MCP server</span><code>claude mcp add adi -- adi-mcp</code><p>Four tools: lookup, country profile, top occupations, cite.</p></div>
            <div><span className="rotulo">llms.txt</span><code>/llms.txt</code><p>A plain-text map of the index for language models. <a href={REPO}>Source on GitHub</a>.</p></div>
          </div>
        </div>
      </section>
      <JsonLd datos={dataset} />
    </>
  );
}
