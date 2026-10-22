import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Barra } from "@/components/Barra";
import { Cita } from "@/components/Cita";
import { JsonLd } from "@/components/JsonLd";
import { Mapa } from "@/components/Mapa";
import { Descomposicion } from "@/components/graficas/Descomposicion";
import { Dispersion } from "@/components/graficas/Dispersion";
import { Franja } from "@/components/graficas/Franja";
import { GG, N_PAISES, SITE, colombia, ordinal, pais, paises } from "@/lib/datos";
import { INGRESO_ORDEN, bandera, posicion } from "@/lib/graficas";
import { PUNTOS, divide } from "@/lib/graficas-datos";
import { citaRegistro } from "@/lib/citar";

export const dynamicParams = false;
export function generateStaticParams() {
  return paises.map((p) => ({ iso3: p.iso3 }));
}

export async function generateMetadata({ params }: { params: Promise<{ iso3: string }> }): Promise<Metadata> {
  const p = pais((await params).iso3);
  if (!p) return {};
  return {
    title: { absolute: `${p.nombre}: ${p.l2.toFixed(1)}% of work delegable to AI agents · ADI · Balam Labs` },
    description: `${p.perfil.hallazgo} Agent Delegability Index, ${p.nombre} ranks ${p.rk} of ${N_PAISES} countries.`,
    alternates: { canonical: `/adi/countries/${p.iso3}` },
  };
}

const NOM_GEIH: Record<string, string> = { "total|todos": "All workers", "sexo|mujeres": "Women", "sexo|hombres": "Men", "edad|15_24": "Aged 15–24",
  "edad|25_54": "Aged 25–54", "edad|55_mas": "Aged 55 and over", "informal|no": "Formal", "informal|si": "Informal" };
const BARRERAS = [["Physical presence", "var(--b-fisica)"], ["Accountability", "var(--b-resp)"], ["Trust and care", "var(--b-conf)"], ["Access to systems", "var(--b-acceso)"]];
const unir = (xs: string[]) => (xs.length < 2 ? xs.join("") : `${xs.slice(0, -1).join(", ")} and ${xs[xs.length - 1]}`);

// Sentences written from the numbers, so each profile reads on its own (same idea as informe/perfil.py).
function motor(p: NonNullable<ReturnType<typeof pais>>) {
  const top = p.grupos.filter((g) => g.adi !== null).sort((a, b) => b.contrib - a.contrib).slice(0, 2);
  const parte = (100 * top.reduce((a, g) => a + g.contrib, 0)) / p.l2, emp = top.reduce((a, g) => a + g.share, 0);
  const nombres = top.map((g) => GG[g.gg].toLowerCase());
  return `${nombres[0].charAt(0).toUpperCase() + nombres[0].slice(1)} and ${nombres[1]} supply ${parte.toFixed(0)}% of ${p.nombre}’s delegable task time while employing ${emp.toFixed(0)}% of its workers.`;
}
function frenos(p: NonNullable<ReturnType<typeof pais>>) {
  const d = p.b.map((v, i) => ({ i, d: v - divide.b_mundo[i] })).sort((a, b) => Math.abs(b.d) - Math.abs(a.d))[0];
  const nom = BARRERAS[d.i][0].toLowerCase();
  return Math.abs(d.d) < 3 ? `Its barriers sit close to the world’s: the work mix weighs about the same as everywhere else.`
    : `The largest gap with the world is ${nom}: ${p.b[d.i].toFixed(0)}% of task weight against ${divide.b_mundo[d.i].toFixed(0)}% worldwide, ${d.d > 0 ? "a heavier brake on agents" : "a lighter brake on agents"}.`;
}
function lecturaUso(p: NonNullable<ReturnType<typeof pais>>) {
  if (p.brecha === null || p.uso === null) return null;
  const tono = p.brecha > 0.5 ? "has more delegable work than its AI use would suggest" : p.brecha < -0.5 ? "uses AI more than its delegable work alone would suggest" : "uses AI about as much as its delegable work would suggest";
  return `With ${p.uso.toFixed(2)}× the world’s Claude use per working-age person, ${p.nombre} ${tono} (gap ${p.brecha > 0 ? "+" : ""}${p.brecha.toFixed(2)} standard deviations).`;
}

const TEMA_GEIH: Record<string, string> = { total: "", sexo: "Sex", edad: "Age", informal: "Formality" };

export default async function Pais({ params }: { params: Promise<{ iso3: string }> }) {
  const p = pais((await params).iso3);
  if (!p) notFound();
  const url = `${SITE}/adi/countries/${p.iso3}`;
  const cita = citaRegistro(`${p.nombre} (${p.iso3})`, url);
  const regionL2 = Number(p.perfil.region_l2);
  const temas = [...new Set(p.perfil.filas.map((f) => f.tema))];
  const porRk = [...paises].sort((a, b) => a.rk - b.rk), i = porRk.findIndex((x) => x.iso3 === p.iso3);
  const [antes, despues] = [porRk[i - 1], porRk[i + 1]];
  const gemelos = p.gemelos.map((g) => pais(g)!).filter(Boolean);
  const uso = lecturaUso(p);
  const regionCap = p.region_nombre.charAt(0).toUpperCase() + p.region_nombre.slice(1);
  const orden = ["total|todos", "sexo|mujeres", "sexo|hombres", "edad|15_24", "edad|25_54", "edad|55_mas", "informal|no", "informal|si"];
  return (
    <>
      <section className="seccion">
        <div className="envoltura">
          <nav className="miga" aria-label="Breadcrumb"><Link href="/adi/countries">Countries</Link><span aria-hidden>/</span>
            <Link href={`/adi/countries?region=${encodeURIComponent(regionCap)}`}>{regionCap}</Link><span aria-hidden>/</span><span>{p.iso3}</span></nav>
          <div className="ficha-cab">
            <div><span className="codigo-grande">{p.iso3} · {p.ingreso_nombre} · ILOSTAT {p.anio}, ISCO-08 at {p.res === 2 ? "two digits" : "one digit"}</span><h1 className="titulo titulo-pais"><img src={bandera(p.iso2, true)} alt={`Flag of ${p.nombre}`} width={96} height={72} />{p.nombre}</h1>
              {p.residuo !== null && <p className={`etiqueta-posicion${Math.abs(p.residuo) < 1.5 ? "" : p.residuo > 0 ? " arriba" : " abajo"}`}>{posicion(p.residuo).replace(/^./, (c) => c.toUpperCase())}
                <span> · expected {p.esperado!.toFixed(1)}% at its GDP per capita</span></p>}
              <nav className="vecinos" aria-label="Neighbours in the ranking">
                {antes && <Link href={`/adi/countries/${antes.iso3}`}>← {ordinal(antes.rk)} {antes.nombre}</Link>}
                {despues && <Link href={`/adi/countries/${despues.iso3}`}>{ordinal(despues.rk)} {despues.nombre} →</Link>}
              </nav></div>
            <div className="titular" style={{ borderLeft: 0, paddingLeft: 0 }}>
              <span className="cifra" style={{ fontSize: "clamp(72px, 10vw, 120px)" }}>{p.l2.toFixed(1)}<small>%</small></span>
              <div className="intervalo">ADI · {ordinal(p.rk)} of {N_PAISES} · 95% interval {p.lo.toFixed(1)}–{p.hi.toFixed(1)}</div>
            </div>
          </div>
          <p className="hallazgo" style={{ marginTop: 28 }}>{p.perfil.hallazgo}</p>
          <div className="tabla-marco">
            <table className="tabla">
              <thead><tr><th>Indicator</th><th className="n">{p.nombre}</th><th className="n">Rank in region</th><th>Highest in region</th><th className="n">Region</th><th className="n">High income</th><th className="n">World</th><th>Source</th></tr></thead>
              {temas.map((t) => (
                <tbody key={t}>
                  <tr><td colSpan={8} className="rotulo" style={{ background: "var(--papel)", paddingTop: 12 }}>{t}</td></tr>
                  {p.perfil.filas.filter((f) => f.tema === t).map((f) => (
                    <tr key={f.nombre}><td>{f.nombre.replace(/[ᵃᵇ]/g, "").trim()}</td><td className="n valor" style={{ color: "var(--teal-osc)" }}>{f.col}</td><td className="n num">{f.puesto}</td>
                      <td className="nota">{f.mejor}</td><td className="n num">{f.region}</td><td className="n num">{f.alto}</td><td className="n num">{f.mundo}</td><td className="nota">{f.fuente}</td></tr>
                  ))}
                </tbody>
              ))}
            </table>
          </div>
          <p className="nota" style={{ marginTop: 10 }}>Region: the {p.perfil.n_region} countries of {p.region_nombre} in the atlas (World Bank regions). Delegability rows are employment-weighted means;
            adoption and context rows are simple means over countries with data. For informality, rank 1 is the lowest. With equal weights inside reported groups, the
            preregistered sensitivity check, {p.nombre}’s ADI is {p.l2_iguales.toFixed(1)}%.</p>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">Where it sits</span>
          <h2 className="titulo-2" style={{ margin: "10px 0 8px" }}>{p.nombre} against the delegation divide</h2>
          <p className="nota" style={{ maxWidth: "70ch", marginBottom: 16 }}>Each flag is a country; the dashed line is what GDP per capita alone predicts. {regionCap} keeps its colours, the rest is grey.
            {p.residuo !== null && ` ${p.nombre} is ${posicion(p.residuo)}.`}</p>
          <Dispersion puntos={PUNTOS} y="l2" x="pib" divide={divide} activo={p.iso3} region={regionCap} alto={480} etiquetas={2}
            titulo={`${p.nombre} and the other ${N_PAISES - 1} countries: ADI against GDP per capita`} />
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">What drives the number</span>
          <h2 className="titulo-2" style={{ margin: "10px 0 8px" }}>Who works in {p.nombre}, and how delegable their tasks are</h2>
          <p className="hallazgo" style={{ marginTop: 12 }}>{motor(p)}</p>
          <Descomposicion pais={p.grupos.filter((g): g is { gg: string; share: number; adi: number; contrib: number } => g.adi !== null)} mundo={divide.grupos_mundo} nombre={p.nombre} nombres={GG} />
          {p.grupos.some((g) => g.adi === null) && <p className="nota" style={{ marginTop: 10 }}>{p.nombre} reports no separate employment for {unir(p.grupos.filter((g) => g.adi === null).map((g) => GG[g.gg].toLowerCase()))}; ILOSTAT counts those workers in other groups.</p>}
          {p.res === 1 && <p className="nota" style={{ marginTop: 10 }}>{p.nombre} reports employment at one ISCO digit, so occupations inside each major group carry equal weight.</p>}
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div>
            <span className="rotulo">What stops the agent here</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 12px" }}>Barriers, weighted by its jobs</h2>
            <p>{frenos(p)}</p>
            <div className="tabla-marco"><table className="tabla"><thead><tr><th>Barrier</th><th className="barra-celda">Share of task weight</th><th className="n">{p.iso3}</th><th className="n">World</th></tr></thead>
              <tbody>{BARRERAS.map(([nom, color], k) => (
                <tr key={nom}><td><i className="desc-muestra" style={{ background: color }} />{nom}</td>
                  <td className="barra-celda"><div style={{ ["--relleno" as string]: color }} className="barra-color"><Barra v={p.b[k]} max={100} marca={divide.b_mundo[k]} etiqueta={`${nom}: ${p.b[k].toFixed(0)}%, world ${divide.b_mundo[k].toFixed(0)}%`} /></div></td>
                  <td className="n valor">{p.b[k].toFixed(0)}%</td><td className="n num">{divide.b_mundo[k].toFixed(0)}%</td></tr>
              ))}</tbody></table></div>
            <p className="nota" style={{ marginTop: 10 }}>Dashed tick: world, weighting the same tasks by world employment. A task can carry more than one barrier.</p>
          </div>
          <div>
            <span className="rotulo">AI use</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 12px" }}>Delegable work and actual AI use</h2>
            {uso ? <>
              <p>{uso}</p>
              <Dispersion puntos={PUNTOS} y="l2" x="uso" activo={p.iso3} modo="puntos" alto={340} etiquetas={1} titulo={`ADI against Claude use per working-age person, ${p.nombre} highlighted`} />
            </> : <p className="nota">The Anthropic Economic Index has no usage figure for {p.nombre}; it covers 101 of the {N_PAISES} countries.</p>}
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">Peers</span>
          <h2 className="titulo-2" style={{ margin: "10px 0 8px" }}>{p.nombre} among the four income groups</h2>
          <Franja puntos={PUNTOS} y="l2" por="ingreso" filas={INGRESO_ORDEN} activo={p.iso3} titulo={`ADI by income group, ${p.nombre} highlighted`} total={N_PAISES} />
          {gemelos.length > 0 && <div className="gemelos">
            <span className="rotulo">Same ADI, different income</span>
            <ul>{gemelos.map((g) => (
              <li key={g.iso3}><img src={bandera(g.iso2)} alt="" width={28} height={21} /><Link href={`/adi/countries/${g.iso3}`}>{g.nombre}</Link>
                <span className="num">{g.l2.toFixed(1)}%</span><span className="nota">{g.ingreso_nombre}</span>
                <Link className="comparar" href={`/adi/compare?type=country&a=${p.iso3}&b=${g.iso3}`}>Compare</Link></li>
            ))}</ul>
          </div>}
        </div>
      </section>

      {p.iso3 === "COL" && (
        <section className="seccion">
          <div className="envoltura dos-1-2">
            <div>
              <span className="rotulo">Household survey · exploratory</span>
              <h2 className="titulo-2" style={{ margin: "10px 0 16px" }}>Formal workers hold the more delegable jobs</h2>
              <p>Weighting each occupation by its employment in Colombia’s monthly household survey (GEIH, January 2024 to August 2026), formal workers’ task time is far more
                delegable than informal workers’. The differences come only from the occupations each group holds, since the index rates tasks, not people.</p>
              <p className="nota">Informal: does not contribute to a pension. Intervals carry the uncertainty of the ratings, not of the survey sample. Source: DANE, GEIH.</p>
            </div>
            <div className="tabla-marco"><table className="tabla"><thead><tr><th>Group</th><th className="barra-celda">ADI with 95% interval</th><th className="n">ADI</th><th className="n">Share of employment</th></tr></thead>
              <tbody>{orden.map((k) => {
                const f = colombia.find((x) => `${x.grupo}|${x.cat}` === k)!;
                return (
                  <tr key={k} className={f.grupo === "total" ? "destacada" : undefined}>
                    <td>{TEMA_GEIH[f.grupo] && <span className="codigo">{TEMA_GEIH[f.grupo]} · </span>}{NOM_GEIH[k]}</td>
                    <td className="barra-celda"><Barra v={f.l2} lo={f.lo} hi={f.hi} max={70} fuerte={f.grupo === "total"} /></td>
                    <td className="n valor">{f.l2.toFixed(1)}</td><td className="n num">{f.grupo === "total" ? "100%" : `${f.emp.toFixed(0)}%`}</td>
                  </tr>
                );
              })}</tbody></table></div>
          </div>
        </section>
      )}

      <section className="seccion">
        <div className="envoltura dos">
          <div>
            <span className="rotulo">{p.region_nombre}</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 16px" }}>{p.perfil.n_region > 1 ? "Within its region" : "Its region"}</h2>
            <p className="nota" style={{ marginBottom: 14 }}>{p.perfil.hallazgo_fig}</p>
            <div className="tabla-marco"><table className="tabla"><thead><tr><th>Country</th><th className="barra-celda">ADI</th><th className="n">%</th></tr></thead>
              <tbody>{p.perfil.barras.map(([iso, nom, v]) => (
                <tr key={iso} className={iso === p.iso3 ? "destacada" : undefined}>
                  <td>{iso === p.iso3 ? <b>{nom}</b> : <Link href={`/adi/countries/${iso}`}>{nom}</Link>}</td>
                  <td className="barra-celda"><Barra v={v} max={70} marca={regionL2} fuerte={iso === p.iso3} /></td><td className="n valor">{v.toFixed(1)}</td>
                </tr>
              ))}</tbody></table></div>
            <p className="nota" style={{ marginTop: 10 }}>Dashed line: regional employment-weighted mean, {p.perfil.region_l2}%. World: {p.perfil.mundo_l2}%.</p>
          </div>
          <div>
            <span className="rotulo">In the atlas</span>
            <div style={{ marginTop: 14 }}><Mapa resaltar={p.iso3} /></div>
            <div style={{ marginTop: 36 }}><span className="rotulo">Cite this record</span><div style={{ marginTop: 14 }}><Cita titulo="Text" cita={cita} /></div></div>
            <p style={{ marginTop: 18 }}>Static JSON: <a href={`/adi/v2026.1/country/${p.iso3}.json`}><code>/adi/v2026.1/country/{p.iso3}.json</code></a></p>
            <div className="botones"><Link className="boton" href={`/adi/compare?type=country&a=${p.iso3}`}>Compare with another country</Link></div>
          </div>
        </div>
      </section>
      <JsonLd datos={{
        "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [
          { "@type": "ListItem", position: 1, name: "Countries", item: `${SITE}/adi/countries` },
          { "@type": "ListItem", position: 2, name: p.nombre, item: url },
        ],
      }} />
    </>
  );
}
