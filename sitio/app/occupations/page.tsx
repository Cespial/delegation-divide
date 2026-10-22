import type { Metadata } from "next";
import { TablaOcupaciones } from "@/components/TablaOcupaciones";
import { GG, N_OCUP, cifra, ocupaciones } from "@/lib/datos";

export const metadata: Metadata = {
  title: "Occupations: AI-agent delegability for 433 ISCO-08 unit groups",
  description: `Ranking of ${N_OCUP} ISCO-08 occupations by the share of task time AI agents can take over, with 95% intervals, full delegation and barriers.`,
  alternates: { canonical: "/occupations" },
};

export default function Ocupaciones() {
  const filas = ocupaciones.map((o) => ({ isco: o.isco, titulo: o.titulo, gg: o.gg, l2: o.l2, lo: o.l2_lo, hi: o.l2_hi, l3: o.l3, s: o.s, n: o.n, rk: o.rk }));
  return (
    <section className="seccion">
      <div className="envoltura">
        <div className="encabezado">
          <div>
            <span className="rotulo">Occupations · ISCO-08 unit groups</span>
            <h1 className="titulo" style={{ marginTop: 14, maxWidth: "18ch" }}>Which jobs can AI agents take over?</h1>
            <p className="entrada" style={{ marginTop: 18 }}>
              {N_OCUP} occupations ranked by ADI, the share of task time an agent can at least partly carry out (L2 or L3). {cifra("extremo.isco.n.max")} unit
              groups reach the maximum and {cifra("extremo.isco.n.min")} reach zero. ADI3 counts full delegation only; ADIs is the expected share of working time.
            </p>
          </div>
        </div>
        <TablaOcupaciones filas={filas} grupos={GG} />
        <p className="nota" style={{ marginTop: 14 }}>Task statements from O*NET 30.2, bridged to ISCO-08 and weighted by importance and frequency. Intervals: 1,000 bootstrap
          draws with tasks resampled within occupation. Rank 1 is the most delegable; ties share a rank.</p>
      </div>
    </section>
  );
}
