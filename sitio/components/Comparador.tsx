"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { bandera } from "@/lib/graficas";
import { Barra } from "./Barra";
import { Descomposicion, type Bloque } from "./graficas/Descomposicion";

export type Item = { id: string; nombre: string; filas: [string, number, number | null, number | null, number][]; nota: string; iso2?: string; posicion?: string; grupos?: Bloque[] };
// filas: [label, value, interval low, interval high, scale max]

export function Comparador({ ocupaciones, paises, nombresGG }: { ocupaciones: Item[]; paises: Item[]; nombresGG: Record<string, string> }) {
  const [tipo, setTipo] = useState<"occupation" | "country">("occupation");
  const [a, setA] = useState("2512");
  const [b, setB] = useState("2411");
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
  const ia = lista.find((x) => x.id === a) ?? lista[0], ib = lista.find((x) => x.id === b) ?? lista[1];
  const actualizar = (t: string, na: string, nb: string) => {
    const u = new URL(window.location.href); u.searchParams.set("type", t); u.searchParams.set("a", na); u.searchParams.set("b", nb);
    window.history.replaceState(null, "", u);
  };
  const ruta = tipo === "country" ? "/adi/countries/" : "/adi/occupations/";
  const selector = (v: string, set: (x: string) => void, lado: "a" | "b") => (
    <select className="campo" style={{ width: "100%" }} aria-label={lado === "a" ? "First" : "Second"} value={v} onChange={(e) => {
      set(e.target.value); actualizar(tipo, lado === "a" ? e.target.value : a, lado === "b" ? e.target.value : b);
    }}>
      {lista.map((x) => <option key={x.id} value={x.id}>{tipo === "occupation" ? `${x.id} · ${x.nombre}` : x.nombre}</option>)}
    </select>
  );
  return (
    <div>
      <div className="pestanas" role="tablist" style={{ marginBottom: 20 }}>
        {(["occupation", "country"] as const).map((t) => (
          <button key={t} role="tab" aria-selected={tipo === t} onClick={() => {
            const na = t === "country" ? "COL" : "2512", nb = t === "country" ? "MEX" : "2411";
            setTipo(t); setA(na); setB(nb); actualizar(t, na, nb);
          }}>{t === "occupation" ? "Two occupations" : "Two countries"}</button>
        ))}
      </div>
      <div className="comparar">
        {[{ it: ia, v: a, set: setA, lado: "a" as const }, { it: ib, v: b, set: setB, lado: "b" as const }].map(({ it, v, set, lado }) => (
          <div key={lado}>
            {selector(v, set, lado)}
            <h2 className="titulo-2" style={{ margin: "20px 0 4px" }}><Link href={`${ruta}${it.id}`} className="comp-nombre">{it.iso2 && <img src={bandera(it.iso2)} alt="" width={36} height={27} />}{it.nombre}</Link></h2>
            <p className="nota">{it.nota}</p>
            {it.posicion && <p className="comp-posicion">{it.posicion}</p>}
            {it.filas.map(([et, val, lo, hi, max]) => (
              <div className="fila-comp" key={et}>
                <div><span className="rotulo">{et}</span><div style={{ marginTop: 8 }}><Barra v={val} lo={lo ?? undefined} hi={hi ?? undefined} max={max} fuerte={et.startsWith("ADI ")} /></div></div>
                <span className="cifra" style={{ fontSize: 34 }}>{val.toFixed(1)}</span>
              </div>
            ))}
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
