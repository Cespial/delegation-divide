import Link from "next/link";
import { Barra } from "./Barra";
import { Pestanas } from "./Pestanas";
import { grupos } from "@/lib/datos";

// ISCO-08 major groups ranked three ways (ADI, ADI3, barriers). Shared by the lab home and the ADI overview.
export function Leaderboard() {
  const porL2 = [...grupos].sort((a, b) => b.l2 - a.l2);
  const porL3 = [...grupos].sort((a, b) => b.l3 - a.l3);
  return (
    <Pestanas etiquetas={["Delegability (ADI)", "Full delegation (ADI3)", "Barriers"]}>
      {[
        <div className="tabla-marco" key="l2"><table className="tabla"><thead><tr><th>#</th><th>Major group</th><th className="barra-celda">ADI, % of task time at L2–L3</th><th className="n">ADI</th><th className="n">95% interval</th></tr></thead>
          <tbody>{porL2.map((g, i) => (
            <tr key={g.gg}><td className="puesto">{i + 1} of 9</td><td><Link href={`/adi/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
              <td className="barra-celda"><Barra v={g.l2} lo={g.lo} hi={g.hi} fuerte={i === 0} /></td><td className="n valor">{g.l2.toFixed(1)}</td><td className="n ic">{g.lo.toFixed(1)}–{g.hi.toFixed(1)}</td></tr>
          ))}</tbody></table></div>,
        <div className="tabla-marco" key="l3"><table className="tabla"><thead><tr><th>#</th><th>Major group</th><th className="barra-celda">ADI3, % of task time at L3 (scale 0–10)</th><th className="n">ADI3</th></tr></thead>
          <tbody>{porL3.map((g, i) => (
            <tr key={g.gg}><td className="puesto">{i + 1} of 9</td><td><Link href={`/adi/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
              <td className="barra-celda"><Barra v={g.l3} max={10} fuerte={i === 0} /></td><td className="n valor">{g.l3.toFixed(1)}</td></tr>
          ))}</tbody></table></div>,
        <div className="tabla-marco" key="b"><table className="tabla"><thead><tr><th>Major group</th><th className="n">Physical presence</th><th className="n">Accountability</th><th className="n">Trust and care</th><th className="n">Access to systems</th></tr></thead>
          <tbody>{[...grupos].sort((a, b) => Number(a.gg) - Number(b.gg)).map((g) => (
            <tr key={g.gg}><td><Link href={`/adi/occupations?group=${g.gg}`}>{g.gg} · {g.nombre}</Link></td>
              {g.b.map((v, j) => <td className="n valor" key={j} style={{ color: v >= 60 ? "var(--tinta)" : "var(--tinta-2)", fontWeight: v >= 60 ? 700 : 500 }}>{v.toFixed(0)}%</td>)}</tr>
          ))}</tbody></table>
          <p className="nota" style={{ marginTop: 10 }}>Share of task weight flagged by each barrier. Barriers are not exclusive. Bold: 60% or more.</p></div>,
      ]}
    </Pestanas>
  );
}
