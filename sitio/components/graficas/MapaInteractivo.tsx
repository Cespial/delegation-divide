"use client";
// Choropleth of any country metric with the five-step teal ramp of the static map (validated), cut at the metric's
// quintiles so each class holds about the same number of countries. Ctrl/Cmd + wheel or + − to zoom, drag to pan.
// Filters grey out the rest; hover or focus shows the country card; click opens the profile.
import { select } from "d3-selection";
import { zoom as d3zoom, zoomIdentity, type ZoomBehavior, type ZoomTransform } from "d3-zoom";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { GRIS, fmt, metrica, type ClaveMetrica, type Punto } from "@/lib/graficas";
import { TarjetaPais } from "./TarjetaPais";

const RAMPA = ["#7cbcb5", "#4d9f97", "#2b847b", "#15645c", "#08403c"];
type Trazos = { ancho: number; alto: number; paises: { iso3: string; nombre: string; d: string }[]; puntos: { iso3: string; x: number; y: number }[] };

export function MapaInteractivo({ trazos, puntos, y, region, ingresos, activo, resaltado, onResaltar, titulo }: {
  trazos: Trazos; puntos: Punto[]; y: ClaveMetrica; region?: string; ingresos?: string[]; activo?: string;
  resaltado?: string | null; onResaltar?: (iso3: string | null) => void; titulo: string;
}) {
  const lienzo = useRef<SVGSVGElement>(null), marco = useRef<HTMLDivElement>(null);
  const zoomRef = useRef<ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const [t, setT] = useState<ZoomTransform>(zoomIdentity);
  const [foco, setFoco] = useState<{ iso3: string; x: number; y: number } | null>(null);
  const m = metrica(y);
  const por = useMemo(() => new Map(puntos.map((p) => [p.iso3, p])), [puntos]);
  const cortes = useMemo(() => {
    const vs = puntos.map((p) => p[y]).filter((v): v is number => v !== null).sort((a, b) => a - b);
    return [1, 2, 3, 4].map((k) => vs[Math.floor((k * vs.length) / 5)]);
  }, [puntos, y]);
  const clase = (v: number) => cortes.filter((c) => v >= c).length;
  const tenue = (p: Punto) => (region && p.region !== region) || (ingresos && ingresos.length > 0 && !ingresos.includes(p.ingreso));

  useEffect(() => {
    const svg = lienzo.current; if (!svg) return;
    const z = d3zoom<SVGSVGElement, unknown>().scaleExtent([1, 12]).translateExtent([[0, 0], [trazos.ancho, trazos.alto]])
      .filter((e: Event) => (e.type === "wheel" ? (e as WheelEvent).ctrlKey || (e as WheelEvent).metaKey : !(e as MouseEvent).button))
      .on("zoom", (e) => setT(e.transform));
    zoomRef.current = z; select(svg).call(z).on("dblclick.zoom", null);
    return () => { select(svg).on(".zoom", null); };
  }, [trazos]);
  const acercar = (k: number) => lienzo.current && zoomRef.current && zoomRef.current.scaleBy(select(lienzo.current), k);
  const restablecer = () => lienzo.current && zoomRef.current && zoomRef.current.transform(select(lienzo.current), zoomIdentity);

  const entrar = (iso3: string) => (e: React.PointerEvent | React.FocusEvent) => {
    const r = marco.current!.getBoundingClientRect();
    const b = (e.currentTarget as Element).getBoundingClientRect();
    setFoco({ iso3, x: ("clientX" in e ? e.clientX : b.left + b.width / 2) - r.left, y: ("clientY" in e ? e.clientY : b.top + b.height / 2) - r.top });
    onResaltar?.(iso3);
  };
  const salir = () => { setFoco(null); onResaltar?.(null); };
  const sobre = foco?.iso3 ?? resaltado ?? null;
  const ps = foco ? por.get(foco.iso3) : undefined;
  const ancho = marco.current?.clientWidth ?? 1000;
  const color = (p: Punto | undefined) => (!p || p[y] === null ? "#e7e5e1" : tenue(p) ? GRIS : RAMPA[clase(p[y]!)]);
  const marcar = [activo, sobre].filter(Boolean) as string[];

  return (
    <div className="dispersion" ref={marco}>
      <div className="dispersion-barra">
        <span className="nota">Ctrl/⌘ + scroll to zoom · drag to pan</span>
        <div className="zoom-botones" role="group" aria-label="Zoom">
          <button type="button" onClick={() => acercar(1.6)} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => acercar(1 / 1.6)} aria-label="Zoom out" disabled={t.k <= 1}>−</button>
          <button type="button" onClick={restablecer} aria-label="Reset zoom" disabled={t.k === 1}>⟲</button>
        </div>
      </div>
      <svg ref={lienzo} className={`mapa lienzo${t.k > 1 ? " ampliado" : ""}`} viewBox={`0 0 ${trazos.ancho} ${trazos.alto}`} role="group" aria-label={titulo}>
        <title>{titulo}</title>
        <g transform={t.toString()}>
          {trazos.paises.map((f) => {
            const p = por.get(f.iso3);
            if (!p) return <path key={f.iso3} d={f.d} fill="#e7e5e1" />;
            return (
              <Link key={f.iso3} href={`/adi/countries/${p.iso3}`} aria-label={`${p.nombre}: ${m.corto} ${fmt(p[y], m)}`}
                onPointerMove={entrar(p.iso3)} onPointerLeave={salir} onFocus={entrar(p.iso3)} onBlur={salir}>
                <path d={f.d} fill={color(p)} style={{ strokeWidth: 0.5 / t.k }} />
              </Link>
            );
          })}
          {trazos.puntos.map((q) => {
            const p = por.get(q.iso3); if (!p) return null;
            return (
              <Link key={q.iso3} href={`/adi/countries/${p.iso3}`} aria-label={`${p.nombre}: ${m.corto} ${fmt(p[y], m)}`}
                onPointerMove={entrar(p.iso3)} onPointerLeave={salir} onFocus={entrar(p.iso3)} onBlur={salir}>
                <circle cx={q.x} cy={q.y} r={4 / Math.sqrt(t.k)} fill={color(p)} style={{ strokeWidth: 0.8 / t.k }} />
              </Link>
            );
          })}
          {trazos.paises.filter((f) => marcar.includes(f.iso3)).map((f) => (
            <g key={`m${f.iso3}`} className="mapa-marca" fill="none" pointerEvents="none" strokeLinejoin="round">
              <path d={f.d} style={{ stroke: "#1a1918", strokeWidth: 3 / t.k }} /><path d={f.d} style={{ stroke: "#f8f8f7", strokeWidth: 1 / t.k }} />
            </g>
          ))}
        </g>
      </svg>
      <div className="escala ancha" aria-label={`Legend: ${m.corto}, quintiles`}>
        {RAMPA.map((c, i) => (
          <span key={c}><i style={{ background: c }} />{i === 0 ? `< ${fmt(cortes[0], m)}` : i === 4 ? `≥ ${fmt(cortes[3], m)}` : `${fmt(cortes[i - 1], m)}–${fmt(cortes[i], m)}`}</span>
        ))}
        <span><i style={{ background: "#e7e5e1" }} />No data</span>
      </div>
      {ps && foco && (
        <TarjetaPais p={ps} y={y} m={m} total={puntos.length}
          style={{ left: foco.x + (foco.x > ancho - 300 ? -16 : 16), top: Math.max(0, foco.y - 20), transform: foco.x > ancho - 300 ? "translateX(-100%)" : undefined }} />
      )}
      <p className="fuente-grafico">Balam Labs · Agent Delegability Index v2026.1 · balamlabs.org/adi · Boundaries: Natural Earth 1:110m</p>
    </div>
  );
}
