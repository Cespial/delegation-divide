"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
import { bandera, type Punto } from "@/lib/graficas";
import { Barra } from "./Barra";

type Clave = "rk" | "nombre" | "l2" | "l3" | "s" | "residuo" | "fisica" | "uso" | "pib" | "inf";

// Leaderboard under the country charts. Filtering happens in the explorer (the same filters drive the chart); this
// sorts, and lights the row of the country hovered in the chart, and the other way round.
export function TablaPaises({ filas, total, resaltado, onResaltar }: { filas: Punto[]; total: number; resaltado?: string | null; onResaltar?: (iso3: string | null) => void }) {
  const [orden, setOrden] = useState<{ k: Clave; asc: boolean }>({ k: "rk", asc: true });
  const vista = useMemo(() => {
    const s = orden.asc ? 1 : -1;
    return [...filas].sort((a, b) => (orden.k === "nombre" ? a.nombre.localeCompare(b.nombre) * s
      : a[orden.k] === null ? 1 : b[orden.k] === null ? -1 : ((a[orden.k] as number) - (b[orden.k] as number)) * s));
  }, [filas, orden]);
  const cab = (k: Clave, txt: string, cls = "", inicioAsc = false) => (
    <th className={cls} aria-sort={orden.k === k ? (orden.asc ? "ascending" : "descending") : "none"}>
      <button className="orden" type="button" onClick={() => setOrden({ k, asc: orden.k === k ? !orden.asc : inicioAsc })}>{txt}</button>
    </th>
  );
  const n = (v: number | null, d = 1) => (v === null ? "–" : v.toFixed(d));
  return (
    <div className="tabla-marco">
      <table className="tabla tabla-paises">
        <caption className="contador" aria-live="polite">{filas.length} of {total} countries</caption>
        <thead><tr>
          {cab("rk", "Rank", "", true)}{cab("nombre", "Country", "", true)}<th className="barra-celda">ADI with 95% interval</th>
          {cab("l2", "ADI", "n")}{cab("l3", "ADI3", "n")}{cab("s", "ADIs", "n")}{cab("residuo", "vs income", "n")}
          {cab("fisica", "Physical", "n")}{cab("uso", "AI use", "n")}{cab("pib", "GDP pc", "n")}{cab("inf", "Informal", "n")}
        </tr></thead>
        <tbody>
          {vista.map((f) => (
            <tr key={f.iso3} className={resaltado === f.iso3 ? "destacada" : undefined} onPointerEnter={() => onResaltar?.(f.iso3)} onPointerLeave={() => onResaltar?.(null)}>
              <td className="puesto">{f.rk}</td>
              <td className="pais-celda"><img src={bandera(f.iso2)} alt="" width={24} height={18} loading="lazy" /><Link href={`/adi/countries/${f.iso3}`}>{f.nombre}</Link>
                <span className="nota">{f.ingreso_nombre}</span></td>
              <td className="barra-celda"><Barra v={f.l2} lo={f.lo} hi={f.hi} max={70} /></td>
              <td className="n valor">{f.l2.toFixed(1)}<span className="ic"> ±{((f.hi - f.lo) / 2).toFixed(1)}</span></td>
              <td className="n num">{f.l3.toFixed(1)}</td><td className="n num">{f.s.toFixed(1)}</td>
              <td className={`n num residuo${f.residuo === null ? "" : f.residuo >= 1.5 ? " arriba" : f.residuo <= -1.5 ? " abajo" : ""}`}>{f.residuo === null ? "–" : `${f.residuo > 0 ? "+" : ""}${f.residuo.toFixed(1)}`}</td>
              <td className="n num">{n(f.fisica, 0)}</td><td className="n num">{n(f.uso, 2)}</td>
              <td className="n num">{f.pib === null ? "–" : `$${(f.pib / 1000).toFixed(f.pib < 10000 ? 1 : 0)}k`}</td><td className="n num">{f.inf === null ? "–" : `${f.inf.toFixed(0)}%`}</td>
            </tr>
          ))}
          {vista.length === 0 && <tr><td colSpan={11} className="nota">No country matches. Clear the search or the filters.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
