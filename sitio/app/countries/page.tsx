import type { Metadata } from "next";
import { Mapa } from "@/components/Mapa";
import { TablaPaises } from "@/components/TablaPaises";
import { INGRESOS, N_PAISES, cifra, paises } from "@/lib/datos";

export const metadata: Metadata = {
  title: "Countries: the delegation divide in 146 economies",
  description: `How much of each country's work AI agents can take over: ADI for ${N_PAISES} countries, from ${cifra("titular.ingreso.bajo.l2")}% in low-income to ${cifra("titular.ingreso.alto.l2")}% in high-income economies.`,
  alternates: { canonical: "/countries" },
};

export default function Paises() {
  const filas = paises.map((p) => ({ iso3: p.iso3, nombre: p.nombre, region: p.region_nombre, ingreso: p.ingreso, ingreso_nombre: p.ingreso_nombre, l2: p.l2, lo: p.lo, hi: p.hi, l3: p.l3, s: p.s, pib: p.pib, rk: p.rk }));
  const regiones = [...new Set(paises.map((p) => p.region_nombre))].sort();
  return (
    <>
      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado">
            <div>
              <span className="rotulo">Country atlas · {N_PAISES} countries</span>
              <h1 className="titulo" style={{ marginTop: 14, maxWidth: "16ch" }}>Delegable work follows income</h1>
              <p className="entrada" style={{ marginTop: 18 }}>
                A country’s ADI weights each occupation by its employment there (ILOSTAT, latest year from 2019). The index runs from {cifra("extremo.pais.bot1.l2")}% in
                {" "}{cifra("extremo.pais.bot1.nombre")} to {cifra("extremo.pais.top1.l2")}% in {cifra("extremo.pais.top1.nombre")}, and rises {cifra("h1.pendiente")} points per log point of GDP per capita.
              </p>
            </div>
          </div>
          <Mapa />
          <p className="nota" style={{ marginTop: 8 }}>Finest ISCO-08 level each country reports to ILOSTAT: {cifra("cobertura.paises.2d")} countries at two digits, {cifra("cobertura.paises.1d")} at one. Small states shown as dots. Boundaries: Natural Earth 1:110m.</p>
        </div>
      </section>
      <section className="seccion">
        <div className="envoltura">
          <TablaPaises filas={filas} regiones={regiones} ingresos={INGRESOS} />
        </div>
      </section>
    </>
  );
}
