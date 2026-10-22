import type { Metadata } from "next";
import { Comparador } from "@/components/Comparador";
import { GG, N_OCUP, N_PAISES, ocupaciones, ordinal, paises } from "@/lib/datos";

export const metadata: Metadata = {
  title: "Compare occupations or countries",
  description: "Put two occupations or two countries side by side: delegability, full delegation, share of working time and barriers, with 95% intervals.",
  alternates: { canonical: "/compare" },
};

export default function Comparar() {
  const B = ["Barrier: physical presence", "Barrier: accountability", "Barrier: trust and care", "Barrier: access to systems"];
  const occ = ocupaciones.map((o) => ({
    id: o.isco, nombre: o.titulo, nota: `ISCO-08 ${o.isco} · ${GG[o.gg]} · ${ordinal(o.rk)} of ${N_OCUP}`,
    filas: [["ADI · partial or full", o.l2, o.l2_lo, o.l2_hi, 100], ["ADI3 · full delegation", o.l3, o.l3_lo, o.l3_hi, 100], ["ADIs · share of working time", o.s, o.s_lo, o.s_hi, 100],
      ...o.b.map((v, i) => [B[i], v, null, null, 100])] as [string, number, number | null, number | null, number][],
  }));
  const pai = [...paises].sort((a, b) => a.nombre.localeCompare(b.nombre)).map((p) => ({
    id: p.iso3, nombre: p.nombre, nota: `${p.region_nombre} · ${p.ingreso_nombre} · ${ordinal(p.rk)} of ${N_PAISES}`,
    filas: [["ADI · partial or full", p.l2, p.lo, p.hi, 70], ["ADI3 · full delegation", p.l3, null, null, 10], ["ADIs · share of working time", p.s, null, null, 70],
      ...(p.inf !== null ? [["Informal employment, %", p.inf, null, null, 100]] : [])] as [string, number, number | null, number | null, number][],
  }));
  return (
    <section className="seccion">
      <div className="envoltura">
        <span className="rotulo">Compare</span>
        <h1 className="titulo" style={{ margin: "14px 0 28px", maxWidth: "16ch" }}>Side by side</h1>
        <Comparador ocupaciones={occ} paises={pai} />
        <p className="nota" style={{ marginTop: 16 }}>Bars run from 0 to 100% for occupations and from 0 to 70% for countries (0–10% for full delegation). Whiskers: 95% bootstrap interval.</p>
      </div>
    </section>
  );
}
