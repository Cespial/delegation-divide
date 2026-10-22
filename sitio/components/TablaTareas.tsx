"use client";
import { useMemo, useState } from "react";
import { Nivel } from "./Barra";

export type FilaTarea = {
  id: number;
  t: string;
  o: string;
  w: number;
  n: number;
  s: number;
  m: number | null;
  h: number | null;
  so: number | null;
  b: (number | null)[];
  core: boolean;
};

type Clave = "w" | "n" | "s" | "m";
const TEXTO_B = ["Physical presence", "Accountability", "Trust and care", "Access to systems"];
const ETIQ_NIVEL: [number | null, string][] = [
  [null, "All"],
  [3, "L3 · Full"],
  [2, "L2 · Partial"],
  [1, "L1 · Augment"],
  [0, "L0 · No role"],
];

function fmtMinutos(m: number | null) {
  if (m === null) return "–";
  if (m < 60) return `${Math.round(m)} min`;
  const h = m / 60;
  return h < 10 ? `${h.toFixed(1)} h` : `${Math.round(h)} h`;
}

export function TablaTareas({ ts, mostrar = 15 }: { ts: FilaTarea[]; mostrar?: number }) {
  const [nivel, setNivel] = useState<number | null>(null);
  const [q, setQ] = useState("");
  const [orden, setOrden] = useState<{ k: Clave; asc: boolean }>({ k: "w", asc: false });

  const conteos = useMemo(() => {
    const c = [0, 0, 0, 0];
    for (const t of ts) if (t.n >= 0 && t.n <= 3) c[t.n]++;
    return c;
  }, [ts]);

  const filtrado = nivel !== null || q.trim().length > 0 || orden.k !== "w" || orden.asc;

  const vista = useMemo(() => {
    const txt = q.trim().toLowerCase();
    const r = ts.filter((t) =>
      (nivel === null || t.n === nivel)
      && (!txt || t.t.toLowerCase().includes(txt) || t.o.toLowerCase().includes(txt))
    );
    const s = orden.asc ? 1 : -1;
    return [...r].sort((a, b) => {
      const va = a[orden.k];
      const vb = b[orden.k];
      if (va === null) return 1;
      if (vb === null) return -1;
      return (va - vb) * s || b.w - a.w;
    });
  }, [ts, nivel, q, orden]);

  const cab = (k: Clave, txt: string, cls = "", inicioAsc = false) => (
    <th className={cls} aria-sort={orden.k === k ? (orden.asc ? "ascending" : "descending") : "none"}>
      <button className="orden" type="button" onClick={() => setOrden({ k, asc: orden.k === k ? !orden.asc : inicioAsc })}>{txt}</button>
    </th>
  );

  const cabTareas = (
    <thead>
      <tr>
        <th>Task statement (O*NET occupation)</th>
        {cab("w", "Weight", "n")}
        {cab("n", "Level", "")}
        <th>Sonnet · Haiku</th>
        {cab("s", "Share", "n")}
        {cab("m", "Human time", "n")}
        <th>Barriers</th>
      </tr>
    </thead>
  );

  const filaTarea = (t: FilaTarea) => (
    <tr key={t.id}>
      <td className="texto-tarea">{t.t}<small>{t.o}{t.core ? "" : " · supplemental task"}</small></td>
      <td className="n num">{t.w.toFixed(1)}%</td>
      <td><Nivel n={t.n} /></td>
      <td><span className="modelos"><Nivel n={t.so} /><Nivel n={t.h} /></span></td>
      <td className="n num">{t.s.toFixed(0)}%</td>
      <td className="n num">{fmtMinutos(t.m)}</td>
      <td className="nota">{t.b.map((v, i) => (v !== null && v >= 0.5 ? TEXTO_B[i] : null)).filter(Boolean).join(", ") || "–"}</td>
    </tr>
  );

  return (
    <div>
      <div className="controles" style={{ marginTop: 14 }}>
        <div className="chips" role="group" aria-label="Filter tasks by delegation level" style={{ marginTop: 0 }}>
          {ETIQ_NIVEL.map(([n, etq]) => {
            const cnt = n === null ? ts.length : conteos[n];
            return (
              <button
                key={etq}
                type="button"
                className={`chip${nivel === n ? " activo" : ""}`}
                aria-pressed={nivel === n}
                onClick={() => setNivel(n)}
                disabled={n !== null && cnt === 0}
              >
                {etq} <span className="num">({cnt})</span>
              </button>
            );
          })}
        </div>
        <input
          className="campo"
          type="search"
          placeholder="Filter tasks in this occupation…"
          aria-label="Filter tasks in this occupation"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ maxWidth: 280, marginLeft: "auto" }}
        />
      </div>

      {!filtrado ? (
        <>
          <div className="tabla-marco tareas">
            <table className="tabla">{cabTareas}<tbody>{ts.slice(0, mostrar).map(filaTarea)}</tbody></table>
          </div>
          {ts.length > mostrar && (
            <details className="mas">
              <summary>Show the other {ts.length - mostrar} tasks</summary>
              <div className="tabla-marco tareas"><table className="tabla">{cabTareas}<tbody>{ts.slice(mostrar).map(filaTarea)}</tbody></table></div>
            </details>
          )}
        </>
      ) : (
        <div className="tabla-marco tareas">
          <table className="tabla">
            {cabTareas}
            <tbody>
              {vista.map(filaTarea)}
              {vista.length === 0 && <tr><td colSpan={7} className="nota">No task matches this filter.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
