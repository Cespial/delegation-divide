import type { Metadata } from "next";
import Link from "next/link";
import { ExploradorPaises } from "@/components/graficas/ExploradorPaises";
import { N_PAISES, cifra } from "@/lib/datos";
import { PUNTOS, REGIONES, divide } from "@/lib/graficas-datos";

export const metadata: Metadata = {
  title: "Countries: the delegation divide in 146 economies",
  description: `How much of each country's work AI agents can take over: ADI for ${N_PAISES} countries, from ${cifra("titular.ingreso.bajo.l2")}% in low-income to ${cifra("titular.ingreso.alto.l2")}% in high-income economies.`,
  alternates: { canonical: "/adi/countries" },
};

export default function Paises() {
  return (
    <section className="seccion" style={{ borderTop: 0 }}>
      <div className="envoltura">
        <div className="encabezado">
          <div>
            <span className="rotulo">Country atlas · {N_PAISES} countries · v2026.1</span>
            <h1 className="titulo" style={{ marginTop: 14, maxWidth: "18ch" }}>Delegable work follows income</h1>
            <p className="entrada" style={{ marginTop: 18 }}>
              A country’s ADI weights each occupation by its employment there (ILOSTAT, latest year from 2019). The index runs from {cifra("extremo.pais.bot1.l2")}% in
              {" "}{cifra("extremo.pais.bot1.nombre")} to {cifra("extremo.pais.top1.l2")}% in {cifra("extremo.pais.top1.nombre")}. Hover a flag to read a country; switch the
              metric to see what else moves with income.
            </p>
          </div>
          <div className="botones"><Link className="boton" href="/adi/methodology#countries">Methodology</Link><Link className="boton" href="/adi/data">Data</Link></div>
        </div>
        <ExploradorPaises puntos={PUNTOS} divide={divide} regiones={REGIONES} />
        <p className="nota" style={{ marginTop: 14 }}>Finest ISCO-08 level each country reports to ILOSTAT: {cifra("cobertura.paises.2d")} countries at two digits, {cifra("cobertura.paises.1d")} at one.
          “vs income” and the country decomposition are site calculations from the published v2026.1 figures. Flags: flag-icons (MIT).</p>
      </div>
    </section>
  );
}
