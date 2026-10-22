import { GG, N_OCUP, NIVELES, ocupacion, ocupaciones, ordinal, tareas } from "@/lib/datos";
import { COLORES_NIVEL, TAM, tarjeta } from "@/lib/og";

export const alt = "Agent Delegability Index: occupation card";
export const size = TAM;
export const contentType = "image/png";
export function generateStaticParams() {
  return ocupaciones.map((o) => ({ isco: o.isco }));
}

export default async function Imagen({ params }: { params: Promise<{ isco: string }> }) {
  const o = ocupacion((await params).isco)!;
  const ts = tareas(o.isco);
  const por = [0, 1, 2, 3].map((n) => ts.filter((t) => t.n === n).reduce((a, t) => a + t.w, 0));
  return tarjeta({
    rotulo: `ISCO-08 ${o.isco} · ${GG[o.gg]}`, titulo: o.titulo, cifra: o.l2.toFixed(1),
    texto: `of task time is at least partly delegable to AI agents. ${ordinal(o.rk)} of ${N_OCUP} occupations.`,
    barra: { partes: por.map((v, i) => ({ v, color: COLORES_NIVEL[i] })), etiquetas: NIVELES.map((n, i) => `${n.k} ${n.corto} ${por[i].toFixed(0)}%`) },
  });
}
