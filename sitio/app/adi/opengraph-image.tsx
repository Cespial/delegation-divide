import { cifra } from "@/lib/datos";
import { LadoIngresos, TAM, tarjeta } from "@/lib/og";

export const alt = "Agent Delegability Index: share of the world's task time that AI agents can at least partly take over, by country income group";
export const size = TAM;
export const contentType = "image/png";

export default async function Imagen() {
  return tarjeta({
    rotulo: "World employment, 2026", titulo: "How much of the world’s work can AI agents take over?",
    cifra: cifra("titular.global.l2"), texto: `of task time is at least partly delegable. Only ${cifra("titular.global.l3")}% in full.`,
    lado: <LadoIngresos />,
  });
}
