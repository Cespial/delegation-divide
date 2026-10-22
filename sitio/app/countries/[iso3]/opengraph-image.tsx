import { N_PAISES, cifra, ordinal, pais, paises } from "@/lib/datos";
import { TAM, tarjeta } from "@/lib/og";

export const alt = "Agent Delegability Index: country card";
export const size = TAM;
export const contentType = "image/png";
export function generateStaticParams() {
  return paises.map((p) => ({ iso3: p.iso3 }));
}

export default async function Imagen({ params }: { params: Promise<{ iso3: string }> }) {
  const p = pais((await params).iso3)!;
  const mundo = Number(cifra("titular.global.l2"));
  return tarjeta({
    rotulo: `${p.region_nombre} · ${p.ingreso_nombre}`, titulo: p.nombre, cifra: p.l2.toFixed(1),
    texto: `of task time in employment is at least partly delegable to AI agents. ${ordinal(p.rk)} of ${N_PAISES} countries.`,
    barra: { v: p.l2, lo: p.lo, hi: p.hi, ref: mundo, refTexto: `World ${mundo.toFixed(1)}%`, max: 70 },
  });
}
