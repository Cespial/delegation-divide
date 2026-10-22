import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Barra } from "@/components/Barra";
import { Cita } from "@/components/Cita";
import { JsonLd } from "@/components/JsonLd";
import { Mapa } from "@/components/Mapa";
import { N_PAISES, SITE, colombia, ordinal, pais, paises } from "@/lib/datos";
import { citaRegistro } from "@/lib/citar";

export const dynamicParams = false;
export function generateStaticParams() {
  return paises.map((p) => ({ iso3: p.iso3 }));
}

export async function generateMetadata({ params }: { params: Promise<{ iso3: string }> }): Promise<Metadata> {
  const p = pais((await params).iso3);
  if (!p) return {};
  return {
    title: { absolute: `${p.nombre}: ${p.l2.toFixed(1)}% of work delegable to AI agents · ADI` },
    description: `${p.perfil.hallazgo} Agent Delegability Index, ${p.nombre} ranks ${p.rk} of ${N_PAISES} countries.`,
    alternates: { canonical: `/countries/${p.iso3}` },
  };
}

const NOM_GEIH: Record<string, string> = { "total|todos": "All workers", "sexo|mujeres": "Women", "sexo|hombres": "Men", "edad|15_24": "Aged 15–24",
  "edad|25_54": "Aged 25–54", "edad|55_mas": "Aged 55 and over", "informal|no": "Formal", "informal|si": "Informal" };
const TEMA_GEIH: Record<string, string> = { total: "", sexo: "Sex", edad: "Age", informal: "Formality" };

export default async function Pais({ params }: { params: Promise<{ iso3: string }> }) {
  const p = pais((await params).iso3);
  if (!p) notFound();
  const url = `${SITE}/countries/${p.iso3}`;
  const cita = citaRegistro(`${p.nombre} (${p.iso3})`, url);
  const regionL2 = Number(p.perfil.region_l2);
  const temas = [...new Set(p.perfil.filas.map((f) => f.tema))];
  const orden = ["total|todos", "sexo|mujeres", "sexo|hombres", "edad|15_24", "edad|25_54", "edad|55_mas", "informal|no", "informal|si"];
  return (
    <>
      <section className="seccion">
        <div className="envoltura">
          <nav className="miga" aria-label="Breadcrumb"><Link href="/countries">Countries</Link><span aria-hidden>/</span>
            <Link href={`/countries?region=${encodeURIComponent(p.region_nombre)}`}>{p.region_nombre}</Link><span aria-hidden>/</span><span>{p.iso3}</span></nav>
          <div className="ficha-cab">
            <div><span className="codigo-grande">{p.iso3} · {p.ingreso_nombre} · ILOSTAT {p.anio}, ISCO-08 at {p.res === 2 ? "two digits" : "one digit"}</span><h1 className="titulo">{p.nombre}</h1></div>
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
                  <td>{iso === p.iso3 ? <b>{nom}</b> : <Link href={`/countries/${iso}`}>{nom}</Link>}</td>
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
            <div className="botones"><Link className="boton" href={`/compare?type=country&a=${p.iso3}`}>Compare with another country</Link></div>
          </div>
        </div>
      </section>
      <JsonLd datos={{
        "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [
          { "@type": "ListItem", position: 1, name: "Countries", item: `${SITE}/countries` },
          { "@type": "ListItem", position: 2, name: p.nombre, item: url },
        ],
      }} />
    </>
  );
}
