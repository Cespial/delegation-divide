import { cifra } from "@/lib/datos";
import { LadoIngresos, TAM, tarjeta } from "@/lib/og";

export const alt = "Balam Labs: independent indices of what AI agents can do. First index: the Agent Delegability Index";
export const size = TAM;
export const contentType = "image/png";

export default async function Imagen() {
  return tarjeta({
    lab: true, rotulo: "Agent Delegability Index v2026.1", titulo: "Measuring how much of the world’s work AI agents can take over",
    cifra: cifra("titular.global.l2"), texto: `of task time in world employment is at least partly delegable to AI agents.`,
    lado: <LadoIngresos />,
  });
}
