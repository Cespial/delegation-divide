"use client";
// Country scatter, the atlas's lead chart (as the accuracy × cost plot is on a vals.ai benchmark page): x is GDP per
// capita or AI use (log), y is the chosen metric. Each country is its flag ringed in its income colour, or a plain dot.
// Ctrl/Cmd + wheel zooms, drag pans, Shift + drag zooms to a box; + − 0 and arrows from the keyboard. Every point is a
// link with an aria-label, and focus shows the same card as hover. The table under the chart is the text version.
import { scaleLinear, scaleLog } from "d3-scale";
import { select } from "d3-selection";
import { zoom as d3zoom, zoomIdentity, type ZoomBehavior, type ZoomTransform } from "d3-zoom";
import Link from "next/link";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { TarjetaPais } from "./TarjetaPais";
import { COLOR_INGRESO, GRIS, bandera, fmt, metrica, type ClaveEjeX, type ClaveMetrica, type Divide, type Punto } from "@/lib/graficas";

type Props = {
  puntos: Punto[]; y: ClaveMetrica; x: ClaveEjeX; divide?: Divide; modo?: "banderas" | "puntos"; alto?: number;
  activo?: string; region?: string; ingresos?: string[]; q?: string; resaltado?: string | null;
  onResaltar?: (iso3: string | null) => void; etiquetas?: number; titulo: string;
};

const M = { arriba: 18, derecha: 24, abajo: 46, izquierda: 52 };
const TICKS_PIB = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000];
const TICKS_USO = [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10];
const dinero = (v: number) => (v >= 1000 ? `$${v / 1000}k` : `$${v}`);

export function Dispersion({ puntos, y, x, divide, modo = "banderas", alto = 560, activo, region, ingresos, q, resaltado, onResaltar, etiquetas = 3, titulo }: Props) {
  const id = useId().replace(/:/g, "");
  const marco = useRef<HTMLDivElement>(null);
  const lienzo = useRef<SVGSVGElement>(null);
  const zoomRef = useRef<ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const [ancho, setAncho] = useState(1000);
  const [t, setT] = useState<ZoomTransform>(zoomIdentity);
  const [moviendo, setMoviendo] = useState(false);
  const [caja, setCaja] = useState<[number, number, number, number] | null>(null);
  const [foco, setFoco] = useState<string | null>(null);
  const m = metrica(y);

  useEffect(() => {
    const el = marco.current; if (!el) return;
    const ro = new ResizeObserver(([e]) => setAncho(Math.max(320, Math.round(e.contentRect.width))));
    ro.observe(el); return () => ro.disconnect();
  }, []);
  const estrecho = ancho < 640;
  const H = estrecho ? Math.min(alto, 440) : alto;
  const iw = ancho - M.izquierda - M.derecha, ih = H - M.arriba - M.abajo;

  const visibles = useMemo(() => puntos.filter((p) => p[y] !== null && (x === "pib" ? p.pib !== null : p.uso !== null)), [puntos, x, y]);
  const base = useMemo(() => {
    const xs = visibles.map((p) => (x === "pib" ? p.pib! : p.uso!)), ys = visibles.map((p) => p[y]!);
    const sx = scaleLog().domain([Math.min(...xs) * 0.8, Math.max(...xs) * 1.25]).range([0, iw]);
    const ymax = Math.max(...ys), ymin = Math.min(...ys);
    const dom: [number, number] = y === "residuo" ? [-Math.max(-ymin, ymax) * 1.12, Math.max(-ymin, ymax) * 1.12] : [0, ymax * 1.08];
    const sy = (m.log ? scaleLog().domain([ymin * 0.8, ymax * 1.25]) : scaleLinear().domain(dom)).range([ih, 0]);
    return { sx, sy };
  }, [visibles, x, y, iw, ih, m.log]);
  const sx = t.rescaleX(base.sx), sy = t.rescaleY(base.sy);

  // zoom: wheel only with Ctrl/Cmd (the page keeps scrolling), drag pans, Shift + drag is the box zoom below
  useEffect(() => {
    const svg = lienzo.current; if (!svg) return;
    const z = d3zoom<SVGSVGElement, unknown>().scaleExtent([1, 24])
      .extent([[M.izquierda, M.arriba], [M.izquierda + iw, M.arriba + ih]])
      .translateExtent([[-iw * 0.1, -ih * 0.1], [iw * 1.1, ih * 1.1]])
      .filter((e: Event) => (e.type === "wheel" ? (e as WheelEvent).ctrlKey || (e as WheelEvent).metaKey : !(e as MouseEvent).shiftKey && !(e as MouseEvent).button))
      .on("start", () => setMoviendo(true)).on("end", () => setMoviendo(false))
      .on("zoom", (e) => setT(e.transform));
    zoomRef.current = z;
    select(svg).call(z).on("dblclick.zoom", null);
    return () => { select(svg).on(".zoom", null); };
  }, [iw, ih]);
  useEffect(() => { if (lienzo.current && zoomRef.current) select(lienzo.current).call(zoomRef.current.transform, zoomIdentity); }, [x, y]);
  const aplicar = (f: (s: ReturnType<typeof select<SVGSVGElement, unknown>>, z: ZoomBehavior<SVGSVGElement, unknown>) => void) => {
    if (lienzo.current && zoomRef.current) f(select(lienzo.current), zoomRef.current);
  };
  const acercar = (k: number) => aplicar((s, z) => z.scaleBy(s, k));
  const restablecer = () => aplicar((s, z) => z.transform(s, zoomIdentity));

  // Shift + drag: draw a box, then zoom so the box fills the plot
  const enPlot = (e: React.PointerEvent) => {
    const r = lienzo.current!.getBoundingClientRect();
    return [e.clientX - r.left - M.izquierda, e.clientY - r.top - M.arriba] as const;
  };
  const inicioCaja = useRef<[number, number] | null>(null);
  const abajo = (e: React.PointerEvent) => { if (!e.shiftKey) return; inicioCaja.current = [...enPlot(e)]; (e.target as Element).setPointerCapture?.(e.pointerId); };
  const mover = (e: React.PointerEvent) => {
    if (!inicioCaja.current) return; const [a, b] = inicioCaja.current, [c, d] = enPlot(e);
    setCaja([Math.min(a, c), Math.min(b, d), Math.abs(c - a), Math.abs(d - b)]);
  };
  const soltar = () => {
    const c = caja; inicioCaja.current = null; setCaja(null);
    if (!c || c[2] < 8 || c[3] < 8) return;
    const [x0, y0] = t.invert([c[0], c[1]]), [x1, y1] = t.invert([c[0] + c[2], c[1] + c[3]]);
    const k = Math.min(24, Math.min(iw / (x1 - x0), ih / (y1 - y0)));
    aplicar((s, z) => z.transform(s, zoomIdentity.translate(iw / 2, ih / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2)));
  };
  const teclado = (e: React.KeyboardEvent) => {
    const paso = 40;
    const acciones: Record<string, () => void> = {
      "+": () => acercar(1.5), "=": () => acercar(1.5), "-": () => acercar(1 / 1.5), "0": restablecer,
      ArrowLeft: () => aplicar((s, z) => z.translateBy(s, paso / t.k, 0)), ArrowRight: () => aplicar((s, z) => z.translateBy(s, -paso / t.k, 0)),
      ArrowUp: () => aplicar((s, z) => z.translateBy(s, 0, paso / t.k)), ArrowDown: () => aplicar((s, z) => z.translateBy(s, 0, -paso / t.k)),
    };
    if (e.target === e.currentTarget && acciones[e.key]) { e.preventDefault(); acciones[e.key](); }
  };

  const tenue = (p: Punto) => (region && p.region !== region) || (ingresos && ingresos.length > 0 && !ingresos.includes(p.ingreso));
  const texto = q?.trim().toLowerCase() ?? "";
  const coincide = (p: Punto) => texto.length > 1 && (p.nombre.toLowerCase().includes(texto) || p.iso3.toLowerCase() === texto);
  const marcados = useMemo(() => {
    const s = new Set<string>();
    const vivos = visibles.filter((p) => !tenue(p)).sort((a, b) => b[y]! - a[y]!);
    vivos.slice(0, etiquetas).forEach((p) => s.add(p.iso3)); vivos.slice(-etiquetas).forEach((p) => s.add(p.iso3));
    visibles.filter(coincide).slice(0, 8).forEach((p) => s.add(p.iso3));
    if (activo) s.add(activo); if (resaltado) s.add(resaltado);
    return s;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visibles, y, region, ingresos, texto, activo, resaltado, etiquetas]);

  const pos = (p: Punto) => [sx(x === "pib" ? p.pib! : p.uso!), sy(p[y]!)] as const;
  const orden = [...visibles].sort((a, b) => Number(!tenue(a)) - Number(!tenue(b)) || Number(marcados.has(a.iso3)) - Number(marcados.has(b.iso3)));
  const sobre = foco ?? resaltado ?? null;
  const ps = sobre ? visibles.find((p) => p.iso3 === sobre) : undefined;

  // delegation-divide line (H1a) and the band of its 95% slope interval, through the means as OLS lines are
  const recta = useMemo(() => {
    if (!divide || y !== "l2" || x !== "pib") return null;
    const lx = visibles.map((p) => Math.log(p.pib!)), mx = lx.reduce((a, b) => a + b, 0) / lx.length;
    const my = divide.const + divide.pendiente * mx;
    const [d0, d1] = base.sx.domain(), pasos = 40;
    const xs = Array.from({ length: pasos + 1 }, (_, i) => Math.exp(Math.log(d0) + ((Math.log(d1) - Math.log(d0)) * i) / pasos));
    return { xs, f: (v: number, b: number) => my + b * (Math.log(v) - mx) };
  }, [divide, x, y, visibles, base]);
  const linea = (b: number) => recta!.xs.map((v, i) => `${i ? "L" : "M"}${sx(v).toFixed(1)},${sy(recta!.f(v, b)).toFixed(1)}`).join("");
  const banda = recta ? `${linea(divide!.pendiente_lo)}${[...recta.xs].reverse().map((v) => `L${sx(v).toFixed(1)},${sy(recta.f(v, divide!.pendiente_hi)).toFixed(1)}`).join("")}Z` : "";

  const [dx0, dx1] = sx.domain();
  const ticksX = (x === "pib" ? TICKS_PIB : TICKS_USO).filter((v) => v >= dx0 && v <= dx1);
  const ticksY = m.log ? TICKS_USO.filter((v) => v >= sy.domain()[0] && v <= sy.domain()[1]) : (sy as ReturnType<typeof scaleLinear>).ticks(estrecho ? 5 : 7);
  const r = modo === "banderas" ? (estrecho ? 8 : 10) : estrecho ? 4.5 : 5.5;

  return (
    <div className="dispersion" ref={marco}>
      <div className="dispersion-barra">
        <span className="nota">{estrecho ? "Pinch or use + − to zoom" : "Ctrl/⌘ + scroll to zoom · drag to pan · Shift + drag to zoom to a box"}</span>
        <div className="zoom-botones" role="group" aria-label="Zoom">
          <button type="button" onClick={() => acercar(1.5)} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => acercar(1 / 1.5)} aria-label="Zoom out" disabled={t.k <= 1}>−</button>
          <button type="button" onClick={restablecer} aria-label="Reset zoom" disabled={t.k === 1 && t.x === 0 && t.y === 0}>⟲</button>
        </div>
      </div>
      <svg ref={lienzo} className={`lienzo${moviendo ? " moviendo" : ""}${t.k > 1 ? " ampliado" : ""}`} width={ancho} height={H} viewBox={`0 0 ${ancho} ${H}`}
        role="group" aria-label={titulo} tabIndex={0} onKeyDown={teclado} onPointerDown={abajo} onPointerMove={mover} onPointerUp={soltar}>
        <title>{titulo}</title>
        <defs>
          <clipPath id={`area-${id}`}><rect x={0} y={0} width={iw} height={ih} /></clipPath>
          <clipPath id={`circulo-${id}`} clipPathUnits="objectBoundingBox"><circle cx={0.5} cy={0.5} r={0.5} /></clipPath>
        </defs>
        <g transform={`translate(${M.izquierda},${M.arriba})`}>
          <rect className="fondo-plot" width={iw} height={ih} />
          {ticksY.map((v) => (
            <g key={`y${v}`} className={`tick${v === 0 ? " cero" : ""}`} transform={`translate(0,${sy(v)})`}>
              <line x2={iw} /><text x={-8} dy="0.32em" textAnchor="end">{m.log ? v : `${v > 0 && y === "residuo" ? "+" : ""}${v}`}</text>
            </g>
          ))}
          {ticksX.map((v) => (
            <g key={`x${v}`} className="tick" transform={`translate(${sx(v)},0)`}>
              <line y2={ih} /><text y={ih + 18} textAnchor="middle">{x === "pib" ? dinero(v) : v}</text>
            </g>
          ))}
          <text className="eje-titulo" x={iw} y={ih + 38} textAnchor="end">{x === "pib" ? "GDP per capita, PPP (log scale)" : "Claude use per working-age person, world = 1 (log scale)"}</text>
          <text className="eje-titulo" x={0} y={-6}>{m.nombre}{m.unidad === "%" ? ", %" : ""}</text>
          <g clipPath={`url(#area-${id})`}>
            {recta && (
              <g className="recta" aria-hidden>
                <path d={banda} className="recta-banda" />
                <path d={linea(divide!.pendiente)} className="recta-linea" />
              </g>
            )}
            {orden.map((p) => {
              const [px, py] = pos(p), apagado = tenue(p), es = p.iso3 === activo || p.iso3 === sobre;
              const color = apagado ? GRIS : COLOR_INGRESO[p.ingreso];
              return (
                <Link key={p.iso3} href={`/adi/countries/${p.iso3}`} className={`pt${apagado ? " apagado" : ""}${es ? " activo" : ""}`}
                  style={{ transform: `translate(${px}px,${py}px)` }}
                  aria-label={`${p.nombre}: ${m.corto} ${fmt(p[y], m)}${p.pib ? `, GDP per capita $${p.pib.toLocaleString("en-US")}` : ""}`}
                  onPointerEnter={() => { setFoco(p.iso3); onResaltar?.(p.iso3); }} onPointerLeave={() => { setFoco(null); onResaltar?.(null); }}
                  onFocus={() => { setFoco(p.iso3); onResaltar?.(p.iso3); }} onBlur={() => { setFoco(null); onResaltar?.(null); }}>
                  <circle r={r + 6} className="pt-blanco" />
                  {modo === "banderas" ? (
                    <>
                      <circle r={r + 1.5} fill="#fff" stroke={color} strokeWidth={es ? 3.5 : 2.5} />
                      <image href={bandera(p.iso2)} x={-r} y={-r} width={2 * r} height={2 * r} preserveAspectRatio="xMidYMid slice" clipPath={`url(#circulo-${id})`} />
                    </>
                  ) : (
                    <circle r={es ? r + 2 : r} fill={color} stroke={es ? "#1a1918" : "#fff"} strokeWidth={es ? 2 : 1.5} />
                  )}
                </Link>
              );
            })}
            {(() => {
              // greedy placement: strongest labels first; a label that would overlap one already placed moves down, then up
              const puestas: [number, number, number, number][] = [];
              const lista = [...marcados].map((iso) => visibles.find((z) => z.iso3 === iso)).filter((p): p is Punto => !!p)
                .sort((a, b) => Number(b.iso3 === activo || b.iso3 === sobre) - Number(a.iso3 === activo || a.iso3 === sobre));
              return lista.map((p) => {
                const [px, py] = pos(p); if (px < 0 || px > iw || py < 0 || py > ih) return null;
                const izq = px > iw - 140, w = p.nombre.length * 6.6 + 4, x0 = izq ? px - r - 6 - w : px + r + 6;
                let dy = 0;
                for (const d of [0, 14, -14, 28, -28, 42]) {
                  const y0 = py + d - 7;
                  if (!puestas.some(([a, b, c, e]) => x0 < c && x0 + w > a && y0 < e && y0 + 14 > b)) { dy = d; break; }
                  dy = d;
                }
                puestas.push([x0, py + dy - 7, x0 + w, py + dy + 7]);
                return <text key={`e${p.iso3}`} className={`etiqueta${p.iso3 === activo || p.iso3 === sobre ? " fuerte" : ""}`} x={px + (izq ? -(r + 6) : r + 6)} y={py + dy} dy="0.32em"
                  textAnchor={izq ? "end" : "start"}>{p.nombre}</text>;
              });
            })()}
          </g>
          {recta && (
            <text className="recta-nota" x={iw - 8} y={ih - 12} textAnchor="end">
              {estrecho ? `Dashed line: +${divide!.pendiente.toFixed(1)} pts per log point of GDP pc` : `Dashed line, the delegation divide: +${divide!.pendiente.toFixed(1)} pts per log point of GDP pc (R² ${divide!.r2.toFixed(2)})`}
            </text>
          )}
          {caja && <rect className="caja-zoom" x={caja[0]} y={caja[1]} width={caja[2]} height={caja[3]} />}
        </g>
      </svg>
      {ps && (() => {
        const [px, py] = pos(ps), izquierda = px + M.izquierda > ancho - 300;
        return (
          <TarjetaPais p={ps} y={y} m={m} total={puntos.length}
            style={{ left: px + M.izquierda + (izquierda ? -16 : 16), top: Math.max(0, py + M.arriba - 20 + (lienzo.current && marco.current ? lienzo.current.getBoundingClientRect().top - marco.current.getBoundingClientRect().top : 40)), transform: izquierda ? "translateX(-100%)" : undefined }} />
        );
      })()}
      <p className="fuente-grafico">Balam Labs · Agent Delegability Index v2026.1 · balamlabs.org/adi</p>
    </div>
  );
}
