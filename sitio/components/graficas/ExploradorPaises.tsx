"use client";
// The country explorer on /adi/countries, laid out like a vals.ai benchmark page: one lead chart with three views
// (Divide scatter, Map, Distribution), metric and axis selectors, filters shared by the chart and the table, a sentence
// written from the numbers on screen, and the leaderboard. State lives in the URL (?view=&metric=&x=&region=&income=&q=)
// so any view can be linked. The map's outlines load only when that view opens.
import { useEffect, useMemo, useRef, useState } from "react";
import { INGRESO_ORDEN, METRICAS, fmt, metrica, type ClaveEjeX, type ClaveMetrica, type Divide, type Punto } from "@/lib/graficas";
import { TablaPaises } from "../TablaPaises";
import { Descargar } from "./Descargar";
import { Dispersion } from "./Dispersion";
import { Franja } from "./Franja";
import { MapaInteractivo } from "./MapaInteractivo";

type Vista = "divide" | "map" | "distribution";
type Trazos = Parameters<typeof MapaInteractivo>[0]["trazos"];
const VISTAS: { k: Vista; nombre: string }[] = [{ k: "divide", nombre: "Divide" }, { k: "map", nombre: "Map" }, { k: "distribution", nombre: "Distribution" }];

function frase(ps: Punto[], y: ClaveMetrica, vista: Vista, x: ClaveEjeX, divide: Divide, todos: number) {
  const m = metrica(y), vs = ps.filter((p) => p[y] !== null).sort((a, b) => b[y]! - a[y]!);
  if (vs.length === 0) return "No country matches these filters.";
  const ambito = vs.length === todos ? `Of ${vs.length} countries` : `Of the ${vs.length} countries shown`;
  const [a, z] = [vs[0], vs[vs.length - 1]];
  let t = y === "residuo"
    ? `${ambito}, ${a.nombre} sits furthest above what its income predicts (${fmt(a.residuo, m)}) and ${z.nombre} furthest below (${fmt(z.residuo, m)}).`
    : `${ambito}, ${a.nombre} ranks first on ${m.corto} with ${fmt(a[y], m)} and ${z.nombre} last with ${fmt(z[y], m)}.`;
  if (vista === "divide" && y === "l2" && x === "pib")
    t += ` Each log point of GDP per capita adds ${divide.pendiente.toFixed(1)} points (95% ${divide.pendiente_lo.toFixed(1)}–${divide.pendiente_hi.toFixed(1)}); income alone explains ${Math.round(divide.r2 * 100)}% of the spread.`;
  else if (vista === "divide" && x === "uso") t += " The x axis covers the 101 countries with Anthropic Economic Index data.";
  return t;
}

export function ExploradorPaises({ puntos, divide, regiones }: { puntos: Punto[]; divide: Divide; regiones: string[] }) {
  const [vista, setVista] = useState<Vista>("divide");
  const [y, setY] = useState<ClaveMetrica>("l2");
  const [x, setX] = useState<ClaveEjeX>("pib");
  const [region, setRegion] = useState("");
  const [ingreso, setIngreso] = useState("");
  const [q, setQ] = useState("");
  const [modo, setModo] = useState<"banderas" | "puntos">("banderas");
  const [resaltado, setResaltado] = useState<string | null>(null);
  const [trazos, setTrazos] = useState<Trazos | null>(null);
  const [listo, setListo] = useState(false);
  const grafico = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const u = new URLSearchParams(window.location.search);
    const v = u.get("view"); if (VISTAS.some((z) => z.k === v)) setVista(v as Vista);
    const mt = u.get("metric"); if (METRICAS.some((z) => z.k === mt)) setY(mt as ClaveMetrica);
    if (u.get("x") === "uso") setX("uso");
    const r = u.get("region"); if (r && regiones.includes(r)) setRegion(r);
    const i = u.get("income"); if (i && INGRESO_ORDEN.some((z) => z.k === i)) setIngreso(i);
    setQ(u.get("q") ?? ""); setListo(true);
  }, [regiones]);
  useEffect(() => {
    if (!listo) return;
    const u = new URL(window.location.href);
    const fijar = (k: string, v: string, def = "") => (v && v !== def ? u.searchParams.set(k, v) : u.searchParams.delete(k));
    fijar("view", vista, "divide"); fijar("metric", y, "l2"); fijar("x", x, "pib"); fijar("region", region); fijar("income", ingreso); fijar("q", q.trim());
    window.history.replaceState(null, "", u);
  }, [listo, vista, y, x, region, ingreso, q]);
  useEffect(() => {
    if (vista === "map" && !trazos) import("@/datos/mapa.json").then((m) => setTrazos(m.default as Trazos));
  }, [vista, trazos]);

  const ingresos = ingreso ? [ingreso] : [];
  const texto = q.trim().toLowerCase();
  const filas = useMemo(() => puntos.filter((p) => (!region || p.region === region) && (!ingreso || p.ingreso === ingreso)
    && (texto.length < 2 || p.nombre.toLowerCase().includes(texto) || p.iso3.toLowerCase() === texto)), [puntos, region, ingreso, texto]);
  const enFiltro = useMemo(() => puntos.filter((p) => (!region || p.region === region) && (!ingreso || p.ingreso === ingreso)), [puntos, region, ingreso]);
  const m = metrica(y);
  const yDisp: ClaveMetrica = y === "uso" && x === "uso" ? "l2" : y;
  const titulo = `${m.nombre} by country`;
  const csv = () => [["iso3", "country", "region", "income_group", "adi_l2", "adi_l2_lo", "adi_l2_hi", "adi_l3", "adi_s", "vs_income_pts", "physical_barrier", "ai_use_index", "gdp_pc_ppp", "informality_pct"],
    ...filas.map((p) => [p.iso3, p.nombre, p.region, p.ingreso_nombre, p.l2, p.lo, p.hi, p.l3, p.s, p.residuo, p.fisica, p.uso, p.pib, p.inf])];

  return (
    <div className="explorador">
      <div className="explorador-cab">
        <div className="pestanas" role="tablist" aria-label="Chart view">
          {VISTAS.map((v) => (
            <button key={v.k} type="button" role="tab" id={`tab-${v.k}`} aria-selected={vista === v.k} aria-controls="panel-paises" onClick={() => setVista(v.k)}>{v.nombre}</button>
          ))}
        </div>
        <div className="selectores">
          <label><span className="rotulo">Metric</span>
            <select className="campo" value={y} onChange={(e) => setY(e.target.value as ClaveMetrica)}>
              {METRICAS.map((z) => <option key={z.k} value={z.k}>{z.corto}</option>)}
            </select></label>
          {vista === "divide" && <label><span className="rotulo">Against</span>
            <select className="campo" value={x} onChange={(e) => setX(e.target.value as ClaveEjeX)}>
              <option value="pib">GDP per capita</option><option value="uso">AI use</option>
            </select></label>}
          {vista === "divide" && <label><span className="rotulo">Marks</span>
            <select className="campo" value={modo} onChange={(e) => setModo(e.target.value as "banderas" | "puntos")}>
              <option value="banderas">Flags</option><option value="puntos">Dots</option>
            </select></label>}
        </div>
      </div>
      <div className="controles filtros">
        <input className="campo" type="search" placeholder="Find a country or ISO3 code" aria-label="Find a country" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="campo" aria-label="Region" value={region} onChange={(e) => setRegion(e.target.value)}>
          <option value="">All regions</option>{regiones.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <select className="campo" aria-label="Income group" value={ingreso} onChange={(e) => setIngreso(e.target.value)}>
          <option value="">All income groups</option>{INGRESO_ORDEN.map((z) => <option key={z.k} value={z.k}>{z.nombre}</option>)}
        </select>
        {(region || ingreso || q) && <button type="button" className="limpiar" onClick={() => { setRegion(""); setIngreso(""); setQ(""); }}>Clear filters</button>}
      </div>
      {vista !== "map" && <div className="leyenda-ingreso" aria-label="Ring colour: income group">
        {INGRESO_ORDEN.map((z) => <span key={z.k}><i style={{ borderColor: `var(--ing-${z.k})` }} />{z.nombre}</span>)}
        {vista === "divide" && y === "l2" && x === "pib" && <span><i className="leyenda-recta" />Delegation divide (95% band)</span>}
      </div>}
      <div id="panel-paises" role="tabpanel" aria-labelledby={`tab-${vista}`} ref={grafico} className="explorador-panel">
        {vista === "divide" && (
          <Dispersion puntos={puntos} y={yDisp} x={x} divide={divide} modo={modo} region={region || undefined} ingresos={ingresos} q={q}
            resaltado={resaltado} onResaltar={setResaltado} titulo={`${metrica(yDisp).nombre} against ${x === "pib" ? "GDP per capita" : "AI use"}`} />
        )}
        {vista === "map" && (trazos
          ? <MapaInteractivo trazos={trazos} puntos={puntos} y={y} region={region || undefined} ingresos={ingresos} resaltado={resaltado} onResaltar={setResaltado} titulo={`Map: ${titulo}`} />
          : <div className="cargando" aria-busy="true">Loading map…</div>)}
        {vista === "distribution" && (
          <Franja puntos={enFiltro} y={y} por={region ? "ingreso" : "region"} q={q} resaltado={resaltado} onResaltar={setResaltado} total={puntos.length}
            filas={region ? INGRESO_ORDEN.map((z) => ({ k: z.k, nombre: z.nombre })) : regiones.map((r) => ({ k: r, nombre: r }))} titulo={`Distribution: ${titulo}`} />
        )}
      </div>
      <div className="explorador-pie">
        <p className="lectura" aria-live="polite">{frase(vista === "divide" ? enFiltro.filter((p) => (x === "pib" ? p.pib : p.uso) !== null) : enFiltro, vista === "divide" ? yDisp : y, vista, x, divide, puntos.length)}</p>
        <Descargar objetivo={grafico} nombre={`adi-countries-${vista}-${vista === "divide" ? yDisp : y}`} csv={csv} />
      </div>
      <p className="nota">{metrica(vista === "divide" ? yDisp : y).nota}{y === "uso" && vista === "divide" && x === "uso" ? " AI use is on the x axis, so the y axis shows the ADI." : ""}</p>
      <div style={{ marginTop: 36 }}>
        <TablaPaises filas={filas} total={puntos.length} resaltado={resaltado} onResaltar={setResaltado} />
      </div>
    </div>
  );
}
