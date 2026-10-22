"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Barra } from "./Barra";

export type FilaOcup = { isco: string; titulo: string; gg: string; l2: number; lo: number; hi: number; l3: number; s: number; n: number; rk: number };
type Clave = "rk" | "titulo" | "l2" | "l3" | "s" | "n" | "isco";

// Full list is rendered on the server (every row is in the HTML); filters and sorting act after hydration.
export function TablaOcupaciones({ filas, grupos }: { filas: FilaOcup[]; grupos: Record<string, string> }) {
  const [q, setQ] = useState("");
  const [gg, setGg] = useState("");
  const [orden, setOrden] = useState<{ k: Clave; asc: boolean }>({ k: "rk", asc: true });
  useEffect(() => {
    const g = new URLSearchParams(window.location.search).get("group");
    if (g && grupos[g]) setGg(g);
  }, [grupos]);
  const vista = useMemo(() => {
    const t = q.trim().toLowerCase();
    const r = filas.filter((f) => (!gg || f.gg === gg) && (!t || f.titulo.toLowerCase().includes(t) || f.isco.startsWith(t)));
    const s = orden.asc ? 1 : -1;
    return [...r].sort((a, b) => (orden.k === "titulo" || orden.k === "isco" ? a[orden.k].localeCompare(b[orden.k]) : (a[orden.k] as number) - (b[orden.k] as number)) * s);
  }, [filas, q, gg, orden]);
  const cab = (k: Clave, txt: string, cls = "", inicioAsc = false) => (
    <th className={cls} aria-sort={orden.k === k ? (orden.asc ? "ascending" : "descending") : "none"}>
      <button className="orden" type="button" onClick={() => setOrden({ k, asc: orden.k === k ? !orden.asc : inicioAsc })}>{txt}</button>
    </th>
  );
  return (
    <div>
      <div className="controles">
        <input className="campo" type="search" placeholder="Search by title or ISCO-08 code" aria-label="Search occupations" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="campo" aria-label="Major group" value={gg} onChange={(e) => {
          setGg(e.target.value);
          const u = new URL(window.location.href); if (e.target.value) u.searchParams.set("group", e.target.value); else u.searchParams.delete("group");
          window.history.replaceState(null, "", u);
        }}>
          <option value="">All major groups</option>
          {Object.entries(grupos).map(([k, v]) => <option key={k} value={k}>{k} · {v}</option>)}
        </select>
        <span className="contador" aria-live="polite">{vista.length} of {filas.length}</span>
      </div>
      <div className="tabla-marco">
        <table className="tabla">
          <thead><tr>
            {cab("rk", "Rank", "", true)}{cab("isco", "ISCO", "", true)}{cab("titulo", "Occupation", "", true)}
            <th className="barra-celda">ADI with 95% interval</th>{cab("l2", "ADI", "n")}{cab("l3", "ADI3", "n")}{cab("s", "ADIs", "n")}{cab("n", "Tasks", "n")}
          </tr></thead>
          <tbody>
            {vista.map((f) => (
              <tr key={f.isco}>
                <td className="puesto">{f.rk}</td><td className="codigo">{f.isco}</td>
                <td><Link href={`/adi/occupations/${f.isco}`}>{f.titulo}</Link></td>
                <td className="barra-celda"><Barra v={f.l2} lo={f.lo} hi={f.hi} /></td>
                <td className="n valor">{f.l2.toFixed(1)}</td><td className="n num">{f.l3.toFixed(1)}</td><td className="n num">{f.s.toFixed(1)}</td><td className="n num">{f.n}</td>
              </tr>
            ))}
            {vista.length === 0 && <tr><td colSpan={8} className="nota">No occupation matches. Clear the search or choose all major groups.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
