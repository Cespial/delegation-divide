import { INGRESOS, cifra } from "@/lib/datos";
import { TAM, tarjeta } from "@/lib/og";

export const alt = "Agent Delegability Index: share of the world's task time that AI agents can at least partly take over, by country income group";
export const size = TAM;
export const contentType = "image/png";

const CORTO: Record<string, string> = { low: "Low", "lower-middle": "Lower-mid", "upper-middle": "Upper-mid", high: "High" };
const TONOS = ["#9ccbc6", "#5fa9a1", "#0d7d74", "#0a4a45"];

export default async function Imagen() {
  const v = INGRESOS.map((g) => Number(cifra(`titular.ingreso.${g.id}.l2`)));
  return tarjeta({
    rotulo: "World employment, 2026", titulo: "How much of the world’s work can AI agents take over?",
    cifra: cifra("titular.global.l2"), texto: `of task time is at least partly delegable. Only ${cifra("titular.global.l3")}% in full.`,
    lado: (
      <div style={{ display: "flex", flexDirection: "column", width: 330 }}>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 10, height: 300, borderBottom: "2px solid #1a1918" }}>
          {v.map((x, i) => (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
              <div style={{ fontFamily: "Cond", fontWeight: 800, fontSize: 34, color: "#0a4a45", marginBottom: 6 }}>{x.toFixed(1)}</div>
              <div style={{ width: "100%", height: (x / 55) * 240, background: TONOS[i] }} />
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
          {INGRESOS.map((g) => <div key={g.k} style={{ flex: 1, display: "flex", justifyContent: "center", fontFamily: "Mono", fontSize: 15, color: "#686c73" }}>{CORTO[g.k]}</div>)}
        </div>
        <div style={{ display: "flex", fontFamily: "Mono", fontSize: 15, color: "#686c73", marginTop: 6, justifyContent: "center" }}>ADI by country income group, %</div>
      </div>
    ),
  });
}
