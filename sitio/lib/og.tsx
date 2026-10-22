// Open Graph cards (1200×630) in the site's identity: paper, ink, one teal; Barlow Condensed for the figure.
// Rendered at build time by next/og for the home page, every occupation, every country and the report.
import { readFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";
import { resumen } from "./datos";

export const TAM = { width: 1200, height: 630 };
const C = { papel: "#f8f8f7", tinta: "#1a1918", tinta2: "#45494f", gris: "#686c73", filete: "#dcdad6", teal: "#0d7d74", osc: "#0a4a45", n: ["#ece9e4", "#cfe6e3", "#5fa9a1", "#0a4a45"] };

async function fuentes() {
  const f = (n: string) => readFile(path.join(process.cwd(), "fonts-og", n));
  const [med, semi, cond, mono] = await Promise.all([f("Barlow-Medium.ttf"), f("Barlow-SemiBold.ttf"), f("BarlowCondensed-ExtraBold.ttf"), f("JetBrainsMono-Regular.ttf")]);
  return [
    { name: "Barlow", data: med, weight: 500 as const, style: "normal" as const },
    { name: "Barlow", data: semi, weight: 600 as const, style: "normal" as const },
    { name: "Cond", data: cond, weight: 800 as const, style: "normal" as const },
    { name: "Mono", data: mono, weight: 400 as const, style: "normal" as const },
  ];
}

const Pasos = ({ alto = 34 }: { alto?: number }) => {
  const e = alto / 28;
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 1.5 * e }}>
      {[9, 15, 22, 28].map((h, i) => <div key={i} style={{ width: 5 * e, height: h * e, background: ["#cfe6e3", "#9ccbc6", "#2f8f86", "#0a4a45"][i] }} />)}
    </div>
  );
};

export type Tarjeta = {
  rotulo: string; titulo: string; cifra: string; unidad?: string; texto: string;
  barra?: { partes: { v: number; color: string }[]; etiquetas?: string[] } | { v: number; lo?: number; hi?: number; ref?: number; refTexto?: string; max: number };
  lado?: React.ReactNode;
};

export async function tarjeta(t: Tarjeta) {
  const largo = t.titulo.length;
  const tamTitulo = largo > 70 ? 44 : largo > 44 ? 52 : 62;
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", background: C.papel, padding: "48px 64px 44px", fontFamily: "Barlow", color: C.tinta }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, borderBottom: `1px solid ${C.filete}`, paddingBottom: 20 }}>
          <Pasos />
          <div style={{ fontFamily: "Cond", fontWeight: 800, fontSize: 40, letterSpacing: 0.5, marginTop: 4 }}>ADI</div>
          <div style={{ display: "flex", fontFamily: "Mono", fontSize: 19, color: C.gris, marginLeft: 8 }}>{`Agent Delegability Index · v${resumen.version}`}</div>
        </div>
        <div style={{ display: "flex", flex: 1, gap: 48, marginTop: 34 }}>
          <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
            <div style={{ fontFamily: "Mono", fontSize: 20, color: C.teal, textTransform: "uppercase", letterSpacing: 1 }}>{t.rotulo}</div>
            <div style={{ fontWeight: 600, fontSize: tamTitulo, lineHeight: 1.08, marginTop: 14, maxWidth: t.lado ? 640 : 1000 }}>{t.titulo}</div>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 24, marginTop: "auto" }}>
              <div style={{ display: "flex", alignItems: "flex-start", fontFamily: "Cond", fontWeight: 800, color: C.osc, fontSize: 168, lineHeight: 0.82 }}>
                {t.cifra}<span style={{ fontSize: 76, marginTop: 6, marginLeft: 4 }}>{t.unidad ?? "%"}</span>
              </div>
              <div style={{ fontSize: 27, lineHeight: 1.25, color: C.tinta2, maxWidth: t.lado ? 300 : 560, paddingBottom: 6 }}>{t.texto}</div>
            </div>
          </div>
          {t.lado}
        </div>
        {t.barra && <Barra b={t.barra} />}
      </div>
    ),
    { ...TAM, fonts: await fuentes() },
  );
}

function Barra({ b }: { b: NonNullable<Tarjeta["barra"]> }) {
  if ("partes" in b) {
    return (
      <div style={{ display: "flex", flexDirection: "column", marginTop: 28 }}>
        <div style={{ display: "flex", height: 26, gap: 3 }}>
          {b.partes.filter((p) => p.v > 0).map((p, i) => <div key={i} style={{ width: `${p.v}%`, background: p.color }} />)}
        </div>
        {b.etiquetas && <div style={{ display: "flex", gap: 28, marginTop: 10, fontFamily: "Mono", fontSize: 17, color: C.gris }}>
          {b.etiquetas.map((e, i) => <div key={e} style={{ display: "flex", alignItems: "center", gap: 8 }}><div style={{ width: 14, height: 14, background: C.n[i] }} />{e}</div>)}
        </div>}
      </div>
    );
  }
  const x = (v: number) => `${(100 * v) / b.max}%`;
  return (
    <div style={{ display: "flex", flexDirection: "column", marginTop: 28 }}>
      <div style={{ display: "flex", position: "relative", height: 26, background: "#ece9e4" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: x(b.v), background: C.osc }} />
        {b.lo !== undefined && b.hi !== undefined && <div style={{ position: "absolute", left: x(b.lo), width: `${(100 * (b.hi - b.lo)) / b.max}%`, top: 11, height: 4, background: C.teal }} />}
        {b.ref !== undefined && <div style={{ position: "absolute", left: x(b.ref), top: -6, bottom: -6, width: 3, background: C.tinta }} />}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontFamily: "Mono", fontSize: 17, color: C.gris }}>
        <span>0%</span>{b.refTexto && <span>{b.refTexto}</span>}<span>{b.max}%</span>
      </div>
    </div>
  );
}

export const COLORES_NIVEL = C.n;
