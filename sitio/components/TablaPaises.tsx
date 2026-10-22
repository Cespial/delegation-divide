"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Barra } from "./Barra";

export type FilaPais = { iso3: string; nombre: string; region: string; ingreso: string; ingreso_nombre: string; l2: number; lo: number; hi: number; l3: number; s: number; pib: number | null; rk: number };
type Clave = "rk" | "nombre" | "l2" | "l3" | "s" | "pib";

export function TablaPaises({ filas, regiones, ingresos }: { filas: FilaPais[]; regiones: string[]; ingresos: { k: string; nombre: string }[] }) {
  const [q, setQ] = useState("");
  const [reg, setReg] = useState("");
  const [ing, setIng] = useState("");
  const [orden, setOrden] = useState<{ k: Clave; asc: boolean }>({ k: "rk", asc: true });
  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const i = p.get("income"); if (i && ingresos.some((x) => x.k === i)) setIng(i);
    const r = p.get("region"); if (r && regiones.includes(r)) setReg(r);
  }, [ingresos, regiones]);
  const vista = useMemo(() => {
    const t = q.trim().toLowerCase();
    const r = filas.filter((f) => (!reg || f.region === reg) && (!ing || f.ingreso === ing) && (!t || f.nombre.toLowerCase().includes(t) || f.iso3.toLowerCase() === t));
    const s = orden.asc ? 1 : -1;
    return [...r].sort((a, b) => (orden.k === "nombre" ? a.nombre.localeCompare(b.nombre) : ((a[orden.k] ?? -1) as number) - ((b[orden.k] ?? -1) as number)) * s);
  }, [filas, q, reg, ing, orden]);
  const cab = (k: Clave, txt: string, cls = "", inicioAsc = false) => (
    <th className={cls} aria-sort={orden.k === k ? (orden.asc ? "ascending" : "descending") : "none"}>
      <button className="orden" type="button" onClick={() => setOrden({ k, asc: orden.k === k ? !orden.asc : inicioAsc })}>{txt}</button>
    </th>
  );
  return (
    <div>
      <div className="controles">
        <input className="campo" type="search" placeholder="Search a country or ISO3 code" aria-label="Search countries" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="campo" aria-label="Region" value={reg} onChange={(e) => setReg(e.target.value)}>
          <option value="">All regions</option>{regiones.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <select className="campo" aria-label="Income group" value={ing} onChange={(e) => setIng(e.target.value)}>
          <option value="">All income groups</option>{ingresos.map((x) => <option key={x.k} value={x.k}>{x.nombre}</option>)}
        </select>
        <span className="contador" aria-live="polite">{vista.length} of {filas.length}</span>
      </div>
      <div className="tabla-marco">
        <table className="tabla">
          <thead><tr>{cab("rk", "Rank", "", true)}{cab("nombre", "Country", "", true)}<th>Income group</th><th className="barra-celda">ADI with 95% interval</th>
            {cab("l2", "ADI", "n")}{cab("l3", "ADI3", "n")}{cab("s", "ADIs", "n")}{cab("pib", "GDP pc, PPP", "n")}</tr></thead>
          <tbody>
            {vista.map((f) => (
              <tr key={f.iso3}>
                <td className="puesto">{f.rk}</td><td><Link href={`/adi/countries/${f.iso3}`}>{f.nombre}</Link> <span className="codigo">{f.iso3}</span></td>
                <td className="nota">{f.ingreso_nombre}</td><td className="barra-celda"><Barra v={f.l2} lo={f.lo} hi={f.hi} max={70} /></td>
                <td className="n valor">{f.l2.toFixed(1)}</td><td className="n num">{f.l3.toFixed(1)}</td><td className="n num">{f.s.toFixed(1)}</td>
                <td className="n num">{f.pib === null ? "–" : f.pib.toLocaleString("en-US")}</td>
              </tr>
            ))}
            {vista.length === 0 && <tr><td colSpan={8} className="nota">No country matches. Clear the search or the filters.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
