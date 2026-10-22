"use client";
// H4 chart: probability of full delegation (L3) as a function of the minutes a competent person needs for one instance
// of the task (log scale). Curve = preregistered quadratic logistic fit over 18,796 O*NET tasks; dots = observed share
// of tasks rated L3 across twentieths of task duration (~940 tasks per bin).
import { scaleLinear } from "d3-scale";
import { useEffect, useRef, useState } from "react";
import { Descargar } from "./Descargar";

export type DatosH4 = { curva: [number, number][]; puntos: [number, number][]; pico_lmin: number };

const M = { arriba: 22, derecha: 24, abajo: 46, izquierda: 48 };
const TICKS_MIN: [number, string][] = [
  [1, "1 min"], [5, "5 min"], [15, "15 min"], [60, "1 h"], [240, "4 h"], [960, "16 h"], [4800, "80 h"],
];

function fmtDuracion(lm: number) {
  const min = Math.exp(lm);
  if (min < 60) return `${min < 10 ? min.toFixed(1) : Math.round(min)} min`;
  const h = min / 60;
  return `${h < 10 ? h.toFixed(1) : Math.round(h)} h`;
}

export function CurvaDuracion({ datos, picoTxt }: { datos: DatosH4; picoTxt: string }) {
  const marco = useRef<HTMLDivElement>(null);
  const [ancho, setAncho] = useState(1000);
  const [activo, setActivo] = useState<number | null>(null);

  useEffect(() => {
    const el = marco.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setAncho(Math.max(320, Math.round(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const estrecho = ancho < 640;
  const H = estrecho ? 300 : 340;
  const iw = ancho - M.izquierda - M.derecha;
  const ih = H - M.arriba - M.abajo;

  const xmax = Math.log(4800);
  const ymax = Math.max(...datos.puntos.map((p) => p[1]), ...datos.curva.map((c) => c[1])) * 1.18;
  const sx = scaleLinear().domain([0, xmax]).range([0, iw]);
  const sy = scaleLinear().domain([0, ymax]).nice().range([ih, 0]);

  const trazoCurva = datos.curva.map(([x, y], i) => `${i ? "L" : "M"}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join("");
  const trazoArea = `${trazoCurva}L${sx(datos.curva[datos.curva.length - 1][0]).toFixed(1)},${sy(0).toFixed(1)}L${sx(datos.curva[0][0]).toFixed(1)},${sy(0).toFixed(1)}Z`;

  const xpico = sx(datos.pico_lmin);
  const ypicoVal = datos.curva.reduce((mejor, c) => (Math.abs(c[0] - datos.pico_lmin) < Math.abs(mejor[0] - datos.pico_lmin) ? c : mejor), datos.curva[0])[1];
  const ypico = sy(ypicoVal);

  const pt = activo !== null ? datos.puntos[activo] : null;
  const predEnPt = pt
    ? datos.curva.reduce((mejor, c) => (Math.abs(c[0] - pt[0]) < Math.abs(mejor[0] - pt[0]) ? c : mejor), datos.curva[0])[1]
    : null;

  const csv = () => [
    ["bin_twentieth", "median_log_minutes", "median_minutes", "observed_l3_pct", "modeled_l3_pct"],
    ...datos.puntos.map(([lm, obs], i) => {
      const mod = datos.curva.reduce((mejor, c) => (Math.abs(c[0] - lm) < Math.abs(mejor[0] - lm) ? c : mejor), datos.curva[0])[1];
      return [i + 1, lm, Number(Math.exp(lm).toFixed(1)), obs, mod];
    }),
  ];

  const ticksY = sy.ticks(estrecho ? 4 : 6);

  return (
    <div className="dispersion" ref={marco}>
      <div className="leyenda-ingreso" style={{ marginBottom: 8 }}>
        <span><i style={{ borderColor: "var(--teal-osc)", background: "var(--teal-medio)" }} />Observed share at L3 (20 task-duration bins)</span>
        <span><i className="leyenda-recta" />Preregistered quadratic logit fit (H4)</span>
      </div>
      <svg width={ancho} height={H} viewBox={`0 0 ${ancho} ${H}`} role="group" aria-label={`Full delegation by task duration, peaking at ${picoTxt} minutes`} className="lienzo fijo">
        <title>{`Tasks rated L3 (full delegation) by human task duration, peaking at ${picoTxt} minutes`}</title>
        <g transform={`translate(${M.izquierda},${M.arriba})`}>
          <rect className="fondo-plot" width={iw} height={ih} />
          {ticksY.map((v) => (
            <g key={`y${v}`} className={`tick${v === 0 ? " cero" : ""}`} transform={`translate(0,${sy(v)})`}>
              <line x2={iw} />
              <text x={-8} dy="0.32em" textAnchor="end">{v}%</text>
            </g>
          ))}
          {TICKS_MIN.map(([min, etq]) => {
            const x = sx(Math.log(min));
            return (
              <g key={etq} className="tick" transform={`translate(${x},0)`}>
                <line y2={ih} />
                <text y={ih + 18} textAnchor="middle">{etq}</text>
              </g>
            );
          })}
          <text className="eje-titulo" x={iw} y={ih + 38} textAnchor="end">
            Minutes a competent person needs for one instance of the task (log scale)
          </text>
          <text className="eje-titulo" x={0} y={-6}>Tasks rated L3 (full delegation), %</text>

          <path d={trazoArea} fill="var(--teal-tinte)" opacity={0.55} />
          <line x1={xpico} x2={xpico} y1={0} y2={ih} stroke="var(--teal)" strokeWidth={1.2} strokeDasharray="4 3" />
          <path d={trazoCurva} fill="none" stroke="var(--teal-osc)" strokeWidth={2.2} />

          <circle cx={xpico} cy={ypico} r={4} fill="var(--teal-osc)" />
          <text className="recta-nota" x={xpico + 8} y={Math.max(16, ypico - 6)}>
            {estrecho ? `Peak: ${picoTxt} min (${ypicoVal.toFixed(1)}%)` : `Model peak at ${picoTxt} min (${ypicoVal.toFixed(1)}% of tasks at L3)`}
          </text>

          {datos.puntos.map(([lm, obs], i) => {
            const cx = sx(lm), cy = sy(obs), es = activo === i;
            return (
              <g key={i} className={`pt${es ? " activo" : ""}`} transform={`translate(${cx},${cy})`}
                tabIndex={0} role="button"
                aria-label={`Bin ${i + 1} of 20 (median ${fmtDuracion(lm)}): ${obs.toFixed(2)}% of tasks rated L3`}
                onPointerEnter={() => setActivo(i)} onPointerLeave={() => setActivo(null)}
                onFocus={() => setActivo(i)} onBlur={() => setActivo(null)}>
                <circle r={12} className="pt-blanco" />
                <circle r={es ? 6.5 : 5} fill="var(--n2)" stroke="var(--teal-osc)" strokeWidth={es ? 2.2 : 1.4} />
              </g>
            );
          })}
        </g>
      </svg>
      <div className="explorador-pie" style={{ marginTop: 10 }}>
        <p className="nota" aria-live="polite" style={{ margin: 0 }}>
          {pt && activo !== null ? (
            <><b>Bin {activo + 1} of 20 · median human time {fmtDuracion(pt[0])}</b>: <b>{pt[1].toFixed(2)}%</b> of tasks are rated L3 (full delegation), compared with <b>{predEnPt!.toFixed(2)}%</b> on the fitted curve.</>
          ) : (
            <>Hover or focus a dot to inspect one of the 20 task-duration bins. Very short tasks are often physical or interpersonal moments; long tasks bundle steps that still need human review.</>
          )}
        </p>
        <Descargar objetivo={marco} nombre="adi-h4-task-duration" csv={csv} />
      </div>
      <p className="fuente-grafico">Balam Labs · Agent Delegability Index v2026.1 · balamlabs.org/adi</p>
    </div>
  );
}
