"use client";
// Dot strip (beeswarm): one row per region or income group, each country a flag on the metric's axis, packed so none
// overlap. The employment-weighted mean of each row is a tick. Shows how wide each group spreads, which a ranked list hides.
import { scaleLinear } from "d3-scale";
import Link from "next/link";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { COLOR_INGRESO, GRIS, bandera, fmt, metrica, type ClaveMetrica, type Punto } from "@/lib/graficas";
import { TarjetaPais } from "./TarjetaPais";

type Fila = { k: string; nombre: string };
type Props = { puntos: Punto[]; y: ClaveMetrica; por: "region" | "ingreso"; filas: Fila[]; activo?: string; q?: string;
  resaltado?: string | null; onResaltar?: (iso3: string | null) => void; titulo: string; total?: number };

const IZQ = 190, DER = 24, R = 9;

// Greedy swarm: points sorted by x take the closest free vertical slot (0, +1, −1, +2, …) at 2R + 1 spacing.
function enjambre(xs: number[]) {
  const orden = xs.map((x, i) => [x, i] as const).sort((a, b) => a[0] - b[0]);
  const dy = new Array<number>(xs.length).fill(0), puestos: [number, number][] = [];
  for (const [x, i] of orden) {
    for (let k = 0; ; k++) {
      const off = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * (2 * R + 1);
      if (!puestos.some(([px, py]) => Math.abs(px - x) < 2 * R + 1 && py === off)) { dy[i] = off; puestos.push([x, off]); break; }
    }
  }
  return dy;
}

export function Franja({ puntos, y, por, filas, activo, q, resaltado, onResaltar, titulo, total }: Props) {
  const id = useId().replace(/:/g, "");
  const marco = useRef<HTMLDivElement>(null);
  const [ancho, setAncho] = useState(1000);
  const [foco, setFoco] = useState<string | null>(null);
  const m = metrica(y);
  useEffect(() => {
    const el = marco.current; if (!el) return;
    const ro = new ResizeObserver(([e]) => setAncho(Math.max(320, Math.round(e.contentRect.width))));
    ro.observe(el); return () => ro.disconnect();
  }, []);
  const estrecho = ancho < 640, izq = estrecho ? 0 : IZQ;
  const vivos = puntos.filter((p) => p[y] !== null);
  const sx = useMemo(() => {
    const vs = vivos.map((p) => p[y]!);
    const lo = y === "residuo" ? Math.min(...vs) - 1 : 0, hi = Math.max(...vs) * 1.04;
    return scaleLinear().domain([lo, hi]).nice().range([izq + R, ancho - DER - R]);
  }, [vivos, y, izq, ancho]);
  const bloques = useMemo(() => {
    let top = 8;
    return filas.map((f) => {
      const ps = vivos.filter((p) => (por === "region" ? p.region : p.ingreso) === f.k);
      const dy = enjambre(ps.map((p) => sx(p[y]!)));
      const alto = Math.max(2 * R + 14, 2 * (Math.max(0, ...dy.map(Math.abs)) + R) + 14) + (estrecho ? 22 : 0);
      const pe = ps.reduce((a, p) => a + p.emp, 0), media = ps.length ? ps.reduce((a, p) => a + p.emp * p[y]!, 0) / pe : null;
      const b = { ...f, ps, dy, top, alto, media }; top += alto; return b;
    });
  }, [filas, vivos, por, sx, y, estrecho]);
  const H = bloques.reduce((a, b) => a + b.alto, 8) + 30;
  const texto = q?.trim().toLowerCase() ?? "";
  const sobre = foco ?? resaltado ?? null;
  const ubicar = (iso: string) => {
    for (const b of bloques) { const i = b.ps.findIndex((p) => p.iso3 === iso); if (i >= 0) return { p: b.ps[i], x: sx(b.ps[i][y]!), y: b.top + b.alto / 2 + (estrecho ? 11 : 0) + b.dy[i] }; }
    return null;
  };
  const u = sobre ? ubicar(sobre) : null;
  return (
    <div className="dispersion" ref={marco}>
      <svg width={ancho} height={H} viewBox={`0 0 ${ancho} ${H}`} role="group" aria-label={titulo} className="lienzo fijo">
        <title>{titulo}</title>
        <defs><clipPath id={`c-${id}`} clipPathUnits="objectBoundingBox"><circle cx={0.5} cy={0.5} r={0.5} /></clipPath></defs>
        {sx.ticks(estrecho ? 5 : 8).map((v) => (
          <g key={v} className={`tick${v === 0 ? " cero" : ""}`} transform={`translate(${sx(v)},0)`}>
            <line y1={8} y2={H - 30} /><text y={H - 12} textAnchor="middle">{`${v > 0 && y === "residuo" ? "+" : ""}${v}`}</text>
          </g>
        ))}
        {bloques.map((b) => {
          const cy = b.top + b.alto / 2 + (estrecho ? 11 : 0);
          return (
            <g key={b.k}>
              <line className="franja-sep" x1={0} x2={ancho - DER} y1={b.top + b.alto} y2={b.top + b.alto} />
              <text className="franja-nombre" x={0} y={estrecho ? b.top + 14 : cy} dy={estrecho ? 0 : "0.32em"}>
                {b.nombre.charAt(0).toUpperCase() + b.nombre.slice(1)}<tspan className="franja-n"> {b.ps.length}</tspan>
              </text>
              {b.media !== null && <g className="franja-media" transform={`translate(${sx(b.media)},${cy})`}><line y1={-b.alto / 2 + 6} y2={b.alto / 2 - 6} /></g>}
              {b.ps.map((p, i) => {
                const es = p.iso3 === activo || p.iso3 === sobre, apagado = texto.length > 1 && !p.nombre.toLowerCase().includes(texto);
                return (
                  <Link key={p.iso3} href={`/adi/countries/${p.iso3}`} className={`pt${apagado ? " apagado" : ""}${es ? " activo" : ""}`}
                    style={{ transform: `translate(${sx(p[y]!)}px,${cy + b.dy[i]}px)` }} aria-label={`${p.nombre}: ${m.corto} ${fmt(p[y], m)}`}
                    onPointerEnter={() => { setFoco(p.iso3); onResaltar?.(p.iso3); }} onPointerLeave={() => { setFoco(null); onResaltar?.(null); }}
                    onFocus={() => { setFoco(p.iso3); onResaltar?.(p.iso3); }} onBlur={() => { setFoco(null); onResaltar?.(null); }}>
                    <circle r={R + 1.5} fill="#fff" stroke={apagado ? GRIS : COLOR_INGRESO[p.ingreso]} strokeWidth={es ? 3.5 : 2} />
                    <image href={bandera(p.iso2)} x={-R} y={-R} width={2 * R} height={2 * R} preserveAspectRatio="xMidYMid slice" clipPath={`url(#c-${id})`} />
                  </Link>
                );
              })}
            </g>
          );
        })}
        {activo && (() => { const a = ubicar(activo); return a && <text className="etiqueta fuerte" x={a.x} y={a.y - R - 7} textAnchor="middle">{a.p.nombre}</text>; })()}
      </svg>
      {u && (
        <TarjetaPais p={u.p} y={y} m={m} total={total ?? puntos.length}
          style={{ left: u.x + (u.x > ancho - 300 ? -16 : 16), top: Math.max(0, u.y - 20), transform: u.x > ancho - 300 ? "translateX(-100%)" : undefined }} />
      )}
      <p className="nota" style={{ marginTop: 6 }}>Ring colour: income group. Vertical tick: employment-weighted mean of the row.</p>
    </div>
  );
}
