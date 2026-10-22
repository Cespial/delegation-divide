"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Barra } from "./Barra";

export type FilaOcup = { isco: string; titulo: string; gg: string; l2: number; lo: number; hi: number; l3: number; s: number; n: number; rk: number; b: number[] };
type Clave = "rk" | "titulo" | "l2" | "l3" | "s" | "n" | "isco" | "barrera";

const BARRERAS_INFO = [
  { k: "physical", idx: 0, corto: "Physical", nombre: "Physical presence", color: "var(--b-fisica)" },
  { k: "accountability", idx: 1, corto: "Accountability", nombre: "Accountability", color: "var(--b-resp)" },
  { k: "trust", idx: 2, corto: "Trust", nombre: "Trust and care", color: "var(--b-conf)" },
  { k: "access", idx: 3, corto: "Access", nombre: "Access to systems", color: "var(--b-acceso)" },
] as const;

function barreraMax(b: number[]) {
  let maxI = 0;
  for (let i = 1; i < b.length; i++) if (b[i] > b[maxI]) maxI = i;
  return { ...BARRERAS_INFO[maxI], v: b[maxI] ?? 0 };
}

// Full list is rendered on the server (every row is in the HTML); filters and sorting act after hydration.
export function TablaOcupaciones({ filas, grupos }: { filas: FilaOcup[]; grupos: Record<string, string> }) {
  const [q, setQ] = useState("");
  const [gg, setGg] = useState("");
  const [barrera, setBarrera] = useState("");
  const [orden, setOrden] = useState<{ k: Clave; asc: boolean }>({ k: "rk", asc: true });
  const [listo, setListo] = useState(false);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const g = p.get("group"); if (g && grupos[g]) setGg(g);
    const b = p.get("barrier"); if (b && BARRERAS_INFO.some((x) => x.k === b)) setBarrera(b);
    const sq = p.get("q"); if (sq) setQ(sq);
    setListo(true);
  }, [grupos]);

  useEffect(() => {
    if (!listo) return;
    const u = new URL(window.location.href);
    const fijar = (k: string, v: string) => (v ? u.searchParams.set(k, v) : u.searchParams.delete(k));
    fijar("group", gg); fijar("barrier", barrera); fijar("q", q.trim());
    window.history.replaceState(null, "", u);
  }, [listo, gg, barrera, q]);

  const bInfo = BARRERAS_INFO.find((x) => x.k === barrera);
  const vista = useMemo(() => {
    const t = q.trim().toLowerCase();
    const r = filas.filter((f) =>
      (!gg || f.gg === gg)
      && (!bInfo || (f.b[bInfo.idx] ?? 0) >= 50)
      && (!t || f.titulo.toLowerCase().includes(t) || f.isco.startsWith(t))
    );
    const s = orden.asc ? 1 : -1;
    return [...r].sort((a, b) => {
      if (orden.k === "titulo" || orden.k === "isco") return a[orden.k].localeCompare(b[orden.k]) * s;
      if (orden.k === "barrera") {
        const va = bInfo ? a.b[bInfo.idx] : barreraMax(a.b).v;
        const vb = bInfo ? b.b[bInfo.idx] : barreraMax(b.b).v;
        return (va - vb) * s || (b.l2 - a.l2);
      }
      if (orden.k === "rk") return (a.rk - b.rk) * s || (b.s - a.s) * s || (b.l3 - a.l3) * s;
      if (orden.k === "l2") return (a.l2 - b.l2) * s || (a.s - b.s) * s || (a.l3 - b.l3) * s;
      return ((a[orden.k] as number) - (b[orden.k] as number)) * s;
    });
  }, [filas, q, gg, bInfo, orden]);

  const cab = (k: Clave, txt: string, cls = "", inicioAsc = false) => (
    <th className={cls} aria-sort={orden.k === k ? (orden.asc ? "ascending" : "descending") : "none"}>
      <button className="orden" type="button" onClick={() => setOrden({ k, asc: orden.k === k ? !orden.asc : inicioAsc })}>{txt}</button>
    </th>
  );

  const descCsv = () => {
    const esc = (v: string | number) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
    const rows = [
      ["rank", "isco08", "occupation", "major_group", "adi_l2", "adi_l2_lo", "adi_l2_hi", "adi_l3", "adi_s", "tasks", "barrier_physical", "barrier_accountability", "barrier_trust", "barrier_access"],
      ...vista.map((f) => [f.rk, f.isco, f.titulo, f.gg, f.l2, f.lo, f.hi, f.l3, f.s, f.n, f.b[0], f.b[1], f.b[2], f.b[3]]),
    ];
    const blob = new Blob([rows.map((r) => r.map(esc).join(",")).join("\n") + "\n"], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "adi-occupations.csv";
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };

  return (
    <div>
      <div className="controles">
        <input className="campo" type="search" placeholder="Search by title or ISCO-08 code" aria-label="Search occupations" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="campo" aria-label="Major group" value={gg} onChange={(e) => setGg(e.target.value)}>
          <option value="">All major groups</option>
          {Object.entries(grupos).map(([k, v]) => <option key={k} value={k}>{k} · {v}</option>)}
        </select>
        <select className="campo" aria-label="Barrier filter" value={barrera} onChange={(e) => setBarrera(e.target.value)}>
          <option value="">All barriers</option>
          {BARRERAS_INFO.map((b) => <option key={b.k} value={b.k}>{b.nombre} ≥ 50%</option>)}
        </select>
        {(q || gg || barrera) && (
          <button type="button" className="limpiar" onClick={() => { setQ(""); setGg(""); setBarrera(""); }}>Clear filters</button>
        )}
        <span className="contador" aria-live="polite" style={{ marginLeft: "auto" }}>{vista.length} of {filas.length}</span>
        <div className="descargar"><button type="button" onClick={descCsv} aria-label="Download filtered occupations as CSV">CSV</button></div>
      </div>
      <div className="tabla-marco">
        <table className="tabla">
          <thead><tr>
            {cab("rk", "Rank", "", true)}{cab("isco", "ISCO", "", true)}{cab("titulo", "Occupation", "", true)}
            <th className="barra-celda">ADI with 95% interval</th>{cab("l2", "ADI", "n")}{cab("l3", "ADI3", "n")}{cab("s", "ADIs", "n")}
            {cab("barrera", "Top barrier", "")}{cab("n", "Tasks", "n")}
          </tr></thead>
          <tbody>
            {vista.map((f) => {
              const bm = bInfo ? { ...bInfo, v: f.b[bInfo.idx] ?? 0 } : barreraMax(f.b);
              return (
                <tr key={f.isco}>
                  <td className="puesto">{f.rk}</td><td className="codigo">{f.isco}</td>
                  <td><Link href={`/adi/occupations/${f.isco}`}>{f.titulo}</Link></td>
                  <td className="barra-celda"><Barra v={f.l2} lo={f.lo} hi={f.hi} /></td>
                  <td className="n valor">{f.l2.toFixed(1)}<span className="ic"> ±{((f.hi - f.lo) / 2).toFixed(1)}</span></td>
                  <td className="n num">{f.l3.toFixed(1)}</td><td className="n num">{f.s.toFixed(1)}</td>
                  <td className="nota" style={{ whiteSpace: "nowrap" }}>
                    {bm.v > 0 ? <><i className="desc-muestra" style={{ background: bm.color }} />{bm.corto} <span className="num">{bm.v.toFixed(0)}%</span></> : "–"}
                  </td>
                  <td className="n num">{f.n}</td>
                </tr>
              );
            })}
            {vista.length === 0 && <tr><td colSpan={9} className="nota">No occupation matches. Clear the search or choose all major groups and barriers.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
