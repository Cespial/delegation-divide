"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { bandera } from "@/lib/graficas";
import { Barra } from "./Barra";
import { Descomposicion, type Bloque } from "./graficas/Descomposicion";

export type Item = {
  id: string;
  nombre: string;
  grupo?: string;
  filas: [string, number, number | null, number | null, number][];
  nota: string;
  iso2?: string;
  posicion?: string;
  grupos?: Bloque[];
};
// filas: [label, value, interval low, interval high, scale max]

const PARES_OCUP: [string, string, string][] = [
  ["Software devs vs Economists", "2512", "2631"],
  ["Coding clerks vs Receptionists", "4413", "4226"],
  ["Lawyers vs General medical doctors", "2611", "2211"],
  ["Accountants vs Primary teachers", "2411", "2341"],
];

const PARES_PAIS: [string, string, string][] = [
  ["Colombia vs United States", "COL", "USA"],
  ["Singapore vs Burundi", "SGP", "BDI"],
  ["Colombia vs Mexico", "COL", "MEX"],
  ["Germany vs India", "DEU", "IND"],
];

function resumenComparacion(ia: Item, ib: Item) {
  if (ia.id === ib.id) return `Choose a different second record to compare with ${ia.nombre}.`;
  const dL2 = ia.filas[0][1] - ib.filas[0][1];
  const dL3 = ia.filas[1][1] - ib.filas[1][1];
  const dS = ia.filas[2][1] - ib.filas[2][1];
  const mas = dL2 >= 0 ? ia : ib;
  const menos = dL2 >= 0 ? ib : ia;
  const gap = Math.abs(dL2).toFixed(1);
  const parteL2 = Math.abs(dL2) < 0.05
    ? `${ia.nombre} and ${ib.nombre} tie on ADI at ${ia.filas[0][1].toFixed(1)}%`
    : `${mas.nombre} (${mas.filas[0][1].toFixed(1)}%) sits ${gap} percentage points above ${menos.nombre} (${menos.filas[0][1].toFixed(1)}%) on ADI`;
  const parteS = Math.abs(dS) < 0.05
    ? "with the same expected share of working time"
    : `and ${Math.abs(dS).toFixed(1)} points ${ (dL2 >= 0 ? dS : -dS) >= 0 ? "higher" : "lower" } on expected share of working time (${mas.filas[2][1].toFixed(1)}% vs ${menos.filas[2][1].toFixed(1)}%)`;
  const parteL3 = Math.abs(dL3) >= 0.1
    ? ` Full delegation is ${ia.filas[1][1].toFixed(1)}% vs ${ib.filas[1][1].toFixed(1)}%.`
    : "";
  return `${parteL2}, ${parteS}.${parteL3}`;
}

export function Comparador({ ocupaciones, paises, nombresGG }: { ocupaciones: Item[]; paises: Item[]; nombresGG: Record<string, string> }) {
  const [tipo, setTipo] = useState<"occupation" | "country">("occupation");
  const [a, setA] = useState("2512");
  const [b, setB] = useState("2411");
  const [copiado, setCopiado] = useState(false);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const t = p.get("type") === "country" ? "country" : "occupation";
    const lista = t === "country" ? paises : ocupaciones;
    setTipo(t);
    const pa = p.get("a"), pb = p.get("b");
    setA(pa && lista.some((x) => x.id === pa) ? pa : t === "country" ? "COL" : "2512");
    setB(pb && lista.some((x) => x.id === pb) ? pb : t === "country" ? "MEX" : "2411");
  }, [ocupaciones, paises]);

  const lista = tipo === "country" ? paises : ocupaciones;
  const ia = lista.find((x) => x.id === a) ?? lista[0];
  const ib = lista.find((x) => x.id === b) ?? lista[1];

  const gruposLista = useMemo(() => {
    const m = new Map<string, Item[]>();
    for (const x of lista) {
      const g = x.grupo ?? "";
      if (!m.has(g)) m.set(g, []);
      m.get(g)!.push(x);
    }
    return [...m.entries()];
  }, [lista]);

  const actualizar = (t: string, na: string, nb: string) => {
    const u = new URL(window.location.href);
    u.searchParams.set("type", t);
    u.searchParams.set("a", na);
    u.searchParams.set("b", nb);
    window.history.replaceState(null, "", u);
  };

  const ruta = tipo === "country" ? "/adi/countries/" : "/adi/occupations/";
  const selector = (v: string, set: (x: string) => void, lado: "a" | "b") => (
    <select className="campo" style={{ width: "100%" }} aria-label={lado === "a" ? "First" : "Second"} value={v} onChange={(e) => {
      set(e.target.value);
      actualizar(tipo, lado === "a" ? e.target.value : a, lado === "b" ? e.target.value : b);
    }}>
      {gruposLista.length > 1
        ? gruposLista.map(([g, xs]) => (
            <optgroup key={g} label={g}>
              {xs.map((x) => <option key={x.id} value={x.id}>{tipo === "occupation" ? `${x.id} · ${x.nombre}` : `${x.nombre} (${x.id})`}</option>)}
            </optgroup>
          ))
        : lista.map((x) => <option key={x.id} value={x.id}>{tipo === "occupation" ? `${x.id} · ${x.nombre}` : x.nombre}</option>)}
    </select>
  );

  const pares = tipo === "country" ? PARES_PAIS : PARES_OCUP;

  return (
    <div>
      <div className="explorador-cab" style={{ marginBottom: 14 }}>
        <div className="pestanas" role="tablist">
          {(["occupation", "country"] as const).map((t) => (
            <button key={t} role="tab" aria-selected={tipo === t} onClick={() => {
              const na = t === "country" ? "COL" : "2512", nb = t === "country" ? "MEX" : "2411";
              setTipo(t); setA(na); setB(nb); actualizar(t, na, nb);
            }}>{t === "occupation" ? "Two occupations" : "Two countries"}</button>
          ))}
        </div>
        <div className="descargar" style={{ paddingBottom: 8 }}>
          <button type="button" onClick={() => { setA(b); setB(a); actualizar(tipo, b, a); }} aria-label="Swap left and right">⇄ Swap</button>
          <button type="button" onClick={async () => {
            try { await navigator.clipboard.writeText(window.location.href); setCopiado(true); setTimeout(() => setCopiado(false), 1600); } catch { /* noop */ }
          }} aria-live="polite">{copiado ? "Link copied" : "Copy link"}</button>
        </div>
      </div>

      <div className="chips" style={{ marginBottom: 18 }}>
        <span className="rotulo">Presets:</span>
        {pares.map(([etq, pa, pb]) => (
          <button key={etq} type="button" className={`chip${a === pa && b === pb ? " activo" : ""}`} onClick={() => {
            setA(pa); setB(pb); actualizar(tipo, pa, pb);
          }}>{etq}</button>
        ))}
      </div>

      <p className="hallazgo" style={{ marginBottom: 22 }} aria-live="polite">{resumenComparacion(ia, ib)}</p>

      <div className="comparar">
        {[{ it: ia, otro: ib, v: a, set: setA, lado: "a" as const }, { it: ib, otro: ia, v: b, set: setB, lado: "b" as const }].map(({ it, otro, v, set, lado }) => (
          <div key={lado}>
            {selector(v, set, lado)}
            <h2 className="titulo-2" style={{ margin: "20px 0 4px" }}><Link href={`${ruta}${it.id}`} className="comp-nombre">{it.iso2 && <img src={bandera(it.iso2)} alt="" width={36} height={27} />}{it.nombre}</Link></h2>
            <p className="nota">{it.nota}</p>
            {it.posicion && <p className="comp-posicion">{it.posicion}</p>}
            {it.filas.map(([et, val, lo, hi, max]) => {
              const otraFila = otro.filas.find(([k]) => k === et);
              const refVal = otraFila && otro.id !== it.id ? otraFila[1] : undefined;
              return (
                <div className="fila-comp" key={et}>
                  <div>
                    <span className="rotulo">{et}</span>
                    <div style={{ marginTop: 8 }}>
                      <Barra v={val} lo={lo ?? undefined} hi={hi ?? undefined} max={max} marca={refVal} fuerte={et.startsWith("ADI ")} />
                    </div>
                  </div>
                  <span className="cifra" style={{ fontSize: 34 }}>{val.toFixed(1)}</span>
                </div>
              );
            })}
          </div>
        ))}
      </div>
      {tipo === "country" && ia.grupos && ib.grupos && ia.id !== ib.id && (
        <div style={{ marginTop: 40 }}>
          <span className="rotulo">Who works where</span>
          <h2 className="titulo-2" style={{ margin: "10px 0 18px" }}>{ia.nombre} and {ib.nombre} by major occupational group</h2>
          <Descomposicion pais={ia.grupos} mundo={ib.grupos} nombre={ia.nombre} referencia={ib.nombre} nombres={nombresGG} />
        </div>
      )}
    </div>
  );
}
