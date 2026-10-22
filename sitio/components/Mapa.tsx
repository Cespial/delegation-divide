import Link from "next/link";
import { mapa, paises } from "@/lib/datos";

// Choropleth of ADI by country (share of task time at L2 or L3). Sequential single-hue ramp, five classes; grey = no data.
export const CLASES = [
  { hasta: 25, color: "#7cbcb5", rotulo: "< 25" }, { hasta: 30, color: "#4d9f97", rotulo: "25–30" }, { hasta: 35, color: "#2b847b", rotulo: "30–35" },
  { hasta: 45, color: "#15645c", rotulo: "35–45" }, { hasta: 101, color: "#08403c", rotulo: "≥ 45" },
];
const color = (v: number) => CLASES.find((c) => v < c.hasta)!.color;

export function Mapa({ resaltar }: { resaltar?: string }) {
  const valor = new Map(paises.map((p) => [p.iso3, p]));
  return (
    <figure style={{ margin: 0 }}>
      <svg className="mapa" viewBox={`0 0 ${mapa.ancho} ${mapa.alto}`} role="img" aria-labelledby="mapa-titulo">
        <title id="mapa-titulo">Map of the Agent Delegability Index by country</title>
        {mapa.paises.map((f) => {
          const p = valor.get(f.iso3);
          if (!p) return <path key={f.iso3} d={f.d} fill="#e7e5e1"><title>{`${f.nombre}: no occupation data`}</title></path>;
          return (
            <Link key={f.iso3} href={`/countries/${p.iso3}`} aria-label={`${p.nombre}: ${p.l2.toFixed(1)}%`}>
              <path d={f.d} fill={color(p.l2)}>
                <title>{`${p.nombre}: ${p.l2.toFixed(1)}% (rank ${p.rk} of ${paises.length})`}</title>
              </path>
            </Link>
          );
        })}
        {mapa.puntos.map((q) => {
          const p = valor.get(q.iso3);
          if (!p) return null;
          return (
            <Link key={q.iso3} href={`/countries/${p.iso3}`} aria-label={`${p.nombre}: ${p.l2.toFixed(1)}%`}>
              <circle cx={q.x} cy={q.y} r={4} fill={color(p.l2)}><title>{`${p.nombre}: ${p.l2.toFixed(1)}%`}</title></circle>
            </Link>
          );
        })}
        {resaltar && mapa.paises.filter((f) => f.iso3 === resaltar).map((f) => (
          <g key="resaltado" fill="none" pointerEvents="none" strokeLinejoin="round">
            <path d={f.d} stroke="#1a1918" strokeWidth={3.2} /><path d={f.d} stroke="#f8f8f7" strokeWidth={1.1} />
          </g>
        ))}
      </svg>
      <figcaption className="escala" aria-label="Legend">
        {CLASES.map((c) => <span key={c.rotulo}><i style={{ background: c.color }} />{c.rotulo}%</span>)}
        <span><i style={{ background: "#e7e5e1" }} />No data</span>
      </figcaption>
    </figure>
  );
}
