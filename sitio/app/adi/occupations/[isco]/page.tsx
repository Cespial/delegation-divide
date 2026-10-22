import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Barra, Barreras, Nivel } from "@/components/Barra";
import { Cita } from "@/components/Cita";
import { JsonLd } from "@/components/JsonLd";
import { TablaTareas } from "@/components/TablaTareas";
import { GG, N_OCUP, NIVELES, SITE, comparadores, ocupacion, ocupaciones, ordinal, tareas } from "@/lib/datos";
import { citaRegistro } from "@/lib/citar";

export const dynamicParams = false;
export function generateStaticParams() {
  return ocupaciones.map((o) => ({ isco: o.isco }));
}

export async function generateMetadata({ params }: { params: Promise<{ isco: string }> }): Promise<Metadata> {
  const o = ocupacion((await params).isco);
  if (!o) return {};
  return {
    title: { absolute: `${o.titulo}: ${o.l2.toFixed(1)}% delegable to AI agents · ADI · Balam Labs` },
    description: `${o.titulo}: ${o.l2.toFixed(1)}% of task time is at least partly delegable to AI agents (95% interval ${o.l2_lo.toFixed(1)}–${o.l2_hi.toFixed(1)}%), ${o.l3.toFixed(1)}% in full. Ranked ${o.rk} of ${N_OCUP} occupations in the Agent Delegability Index.`,
    alternates: { canonical: `/adi/occupations/${o.isco}` },
  };
}

export default async function Ocupacion({ params }: { params: Promise<{ isco: string }> }) {
  const o = ocupacion((await params).isco);
  if (!o) notFound();
  const ts = tareas(o.isco);
  const porNivel = [0, 1, 2, 3].map((n) => ts.filter((t) => t.n === n).reduce((a, t) => a + t.w, 0));
  const vecinos = ocupaciones.filter((x) => x.sub === o.sub && x.isco !== o.isco).sort((a, b) => b.l2 - a.l2);
  const porRk = [...ocupaciones].sort((a, b) => a.rk - b.rk || b.s - a.s || b.l3 - a.l3);
  const idxRk = porRk.findIndex((x) => x.isco === o.isco);
  const [antes, despues] = [porRk[idxRk - 1], porRk[idxRk + 1]];
  const url = `${SITE}/adi/occupations/${o.isco}`;
  const cita = citaRegistro(`${o.titulo} (ISCO-08 ${o.isco})`, url);
  const pctAdi = Math.round(100 * (1 - (o.rk - 1) / N_OCUP));
  return (
    <>
      <section className="seccion">
        <div className="envoltura">
          <nav className="miga" aria-label="Breadcrumb"><Link href="/adi/occupations">Occupations</Link><span aria-hidden>/</span>
            <Link href={`/adi/occupations?group=${o.gg}`}>{o.gg} · {GG[o.gg]}</Link><span aria-hidden>/</span><span>{o.isco}</span></nav>
          <div className="ficha-cab">
            <div>
              <span className="codigo-grande">ISCO-08 {o.isco}{o.imp ? " · imputed from its three-digit group" : ""}</span>
              <h1 className="titulo">{o.titulo}</h1>
              <nav className="vecinos" aria-label="Neighbours in the ranking">
                {antes && <Link href={`/adi/occupations/${antes.isco}`}>← {ordinal(antes.rk)} {antes.titulo}</Link>}
                {despues && <Link href={`/adi/occupations/${despues.isco}`}>{ordinal(despues.rk)} {despues.titulo} →</Link>}
              </nav>
            </div>
            <div className="titular" style={{ borderLeft: 0, paddingLeft: 0 }}>
              <span className="cifra" style={{ fontSize: "clamp(72px, 10vw, 120px)" }}>{o.l2.toFixed(1)}<small>%</small></span>
              <div className="intervalo">ADI · {ordinal(o.rk)} of {N_OCUP} · 95% interval {o.l2_lo.toFixed(1)}–{o.l2_hi.toFixed(1)}</div>
            </div>
          </div>
          <p className="hallazgo" style={{ marginTop: 28 }}>
            An AI agent can at least partly carry out {o.l2.toFixed(1)}% of the task time of {o.titulo.toLowerCase()}, and finish {o.l3.toFixed(1)}% alone.
            {o.b[3] >= 50 ? " The barrier that holds most of the rest back is access to the systems the work runs on." : o.b[0] >= 50 ? " Most of the rest requires physical presence." : ""}
          </p>
          <div className="baldosas">
            <div className="baldosa"><span className="rotulo">ADI · partial or full</span><span className="cifra">{o.l2.toFixed(1)}%</span>
              <Barra v={o.l2} lo={o.l2_lo} hi={o.l2_hi} fuerte /><p style={{ marginTop: 10 }}>{ordinal(o.rk)} of {N_OCUP} · interval {o.l2_lo.toFixed(1)}–{o.l2_hi.toFixed(1)}</p></div>
            <div className="baldosa"><span className="rotulo">ADI3 · full delegation</span><span className="cifra">{o.l3.toFixed(1)}%</span>
              <Barra v={o.l3} lo={o.l3_lo} hi={o.l3_hi} /><p style={{ marginTop: 10 }}>{ordinal(o.rk3)} of {N_OCUP} · interval {o.l3_lo.toFixed(1)}–{o.l3_hi.toFixed(1)}</p></div>
            <div className="baldosa"><span className="rotulo">ADIs · share of time</span><span className="cifra">{o.s.toFixed(1)}%</span>
              <Barra v={o.s} lo={o.s_lo} hi={o.s_hi} /><p style={{ marginTop: 10 }}>{ordinal(o.rks)} of {N_OCUP} · interval {o.s_lo.toFixed(1)}–{o.s_hi.toFixed(1)}</p></div>
            <div className="baldosa"><span className="rotulo">Evidence</span><span className="cifra">{o.n}</span>
              <p>task statements rated by two models and weighted by importance and frequency. World employment: {o.emp.toFixed(1)} million.</p></div>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div>
            <span className="rotulo">Task weight by level</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 20px" }}>How the tasks rate</h2>
            <div style={{ display: "flex", height: 28, borderRadius: 3, overflow: "hidden", gap: 2 }} role="img"
              aria-label={NIVELES.map((n, i) => `${n.k} ${porNivel[i].toFixed(0)}%`).join(", ")}>
              {porNivel.map((v, i) => v > 0 && <div key={i} className={`nivel n${i}`} style={{ width: `${v}%`, height: "100%", borderRadius: 0, minWidth: 0, padding: 0 }}>{v >= 8 ? `${v.toFixed(0)}%` : ""}</div>)}
            </div>
            <div className="leyenda" style={{ marginTop: 12 }}>
              {NIVELES.map((n, i) => <span key={n.k}><Nivel n={i} />{n.nombre} · {porNivel[i].toFixed(1)}%</span>)}
            </div>
          </div>
          <div>
            <span className="rotulo">Barriers</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 20px" }}>What stops the agent</h2>
            <Barreras b={o.b} />
            <p className="nota" style={{ marginTop: 10 }}>Share of task weight flagged by each barrier; a task can carry several.</p>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">{ts.length} task statements, heaviest first</span>
          <TablaTareas ts={ts} />
          <p className="nota" style={{ marginTop: 12 }}>Level: consensus of the two models (the lower level when they disagree). Share: part of the task’s working time an
            agent could take over. Human time: minutes a competent person needs for one instance, as estimated by the models.</p>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div>
            <span className="rotulo">Against other measures</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 18px" }}>Exposure is not delegation</h2>
            <div className="tabla-marco"><table className="tabla"><thead><tr><th>Measure</th><th className="n">Value</th><th className="barra-celda">Percentile</th><th className="n">Pct</th></tr></thead>
              <tbody>
                <tr className="destacada"><td>ADI (this index)</td><td className="n valor">{o.l2.toFixed(1)}%</td><td className="barra-celda"><Barra v={pctAdi} fuerte /></td><td className="n num">{pctAdi}</td></tr>
                {Object.entries(comparadores).map(([k, nom]) => (
                  <tr key={k}><td>{nom}</td><td className="n num">{o.comp[k] ? o.comp[k]!.v : "–"}</td>
                    <td className="barra-celda">{o.comp[k] ? <Barra v={o.comp[k]!.p} marca={pctAdi} /> : <span className="nota">–</span>}</td>
                    <td className="n num">{o.comp[k] ? o.comp[k]!.p : "–"}</td></tr>
                ))}
              </tbody></table></div>
            <p className="nota" style={{ marginTop: 10 }}>Earlier indices measure whether AI can touch a task; ADI measures how much of it an agent can carry out from a goal. – : the source does not cover this occupation.</p>
          </div>
          <div>
            <span className="rotulo">Same sub-major group ({o.sub})</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 18px" }}>Neighbouring occupations</h2>
            <div className="tabla-marco"><table className="tabla"><thead><tr><th>Occupation</th><th className="barra-celda">ADI</th><th className="n">%</th></tr></thead>
              <tbody>{vecinos.slice(0, 12).map((x) => (
                <tr key={x.isco}><td><Link href={`/adi/occupations/${x.isco}`}>{x.titulo}</Link> <span className="codigo">{x.isco}</span></td>
                  <td className="barra-celda"><Barra v={x.l2} marca={o.l2} /></td><td className="n valor">{x.l2.toFixed(1)}</td></tr>
              ))}{vecinos.length === 0 && <tr><td colSpan={3} className="nota">This is the only unit group in its sub-major group.</td></tr>}</tbody></table></div>
            {vecinos.length > 0 && <p className="nota" style={{ marginTop: 10 }}>Dashed line: {o.titulo.toLowerCase()} ({o.l2.toFixed(1)}%).</p>}
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div><span className="rotulo">Cite this record</span><div style={{ marginTop: 14 }}><Cita titulo="Text" cita={cita} /></div></div>
          <div><span className="rotulo">Machine-readable</span>
            <p style={{ marginTop: 14 }}>The same record as static JSON, with its citation: <a href={`/adi/v2026.1/isco/${o.isco}.json`}><code>/adi/v2026.1/isco/{o.isco}.json</code></a>.</p>
            <div className="botones"><Link className="boton" href={`/adi/compare?a=${o.isco}`}>Compare with another occupation</Link><Link className="boton" href="/adi/methodology">How it is measured</Link></div>
          </div>
        </div>
      </section>
      <JsonLd datos={{
        "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [
          { "@type": "ListItem", position: 1, name: "Occupations", item: `${SITE}/adi/occupations` },
          { "@type": "ListItem", position: 2, name: GG[o.gg], item: `${SITE}/adi/occupations?group=${o.gg}` },
          { "@type": "ListItem", position: 3, name: o.titulo, item: url },
        ],
      }} />
    </>
  );
}
