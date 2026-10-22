// Shared definitions for the country charts: one record per country with every value a chart can plot, the metrics
// a viewer can switch between, and the income ramp (one hue, light → dark, checked with the dataviz validator:
// monotone lightness, visible steps, light end 2.16:1 on white). Region is never a colour: a chosen region keeps
// its colours and the rest turn grey, because seven hues cannot be told apart in a scatter.
// Pure module (types, constants, formatting): client components import it; the data comes from lib/graficas-datos.ts.

export type Divide = {
  const: number; pendiente: number; r2: number; n: number; pendiente_lo: number; pendiente_hi: number;
  grupos_mundo: { gg: string; share: number; adi: number; contrib: number }[]; b_mundo: number[];
};
export const INGRESO_ORDEN = [
  { k: "low", nombre: "Low income" }, { k: "lower-middle", nombre: "Lower-middle income" },
  { k: "upper-middle", nombre: "Upper-middle income" }, { k: "high", nombre: "High income" },
];

export const COLOR_INGRESO: Record<string, string> = { low: "#7cbcb5", "lower-middle": "#3f968d", "upper-middle": "#196b63", high: "#083d39" };
export const GRIS = "#d9d7d2";

export type Punto = {
  iso3: string; iso2: string; nombre: string; region: string; ingreso: string; ingreso_nombre: string; rk: number;
  l2: number; lo: number; hi: number; l3: number; s: number; fisica: number; uso: number | null; pib: number | null;
  inf: number | null; residuo: number | null; esperado: number | null; emp: number;
};

export type ClaveMetrica = "l2" | "l3" | "s" | "fisica" | "uso" | "residuo";
export type Metrica = { k: ClaveMetrica; corto: string; nombre: string; unidad: string; dec: number; log?: boolean; nota: string };
export const METRICAS: Metrica[] = [
  { k: "l2", corto: "ADI", nombre: "ADI: task time at least partly delegable", unidad: "%", dec: 1, nota: "Share of task time an AI agent can at least partly take over (levels L2–L3)." },
  { k: "l3", corto: "ADI3", nombre: "ADI3: task time fully delegable", unidad: "%", dec: 1, nota: "Share of task time an agent can take over in full (L3)." },
  { k: "s", corto: "ADIs", nombre: "ADIs: expected share of working time delegable", unidad: "%", dec: 1, nota: "Expected share of working time an agent could do, from each task's delegable share." },
  { k: "fisica", corto: "Physical barrier", nombre: "Task weight that needs physical presence", unidad: "%", dec: 0, nota: "Employment-weighted share of task weight flagged as needing a person on site." },
  { k: "uso", corto: "AI use", nombre: "Claude use per working-age person (index)", unidad: "", dec: 2, log: true, nota: "Anthropic Economic Index, usage per capita relative to the world (1 = world average); 101 countries." },
  { k: "residuo", corto: "vs income", nombre: "Points above or below what income predicts", unidad: " pts", dec: 1, nota: "ADI minus the delegation-divide line at the country's GDP per capita." },
];
export const metrica = (k: string) => METRICAS.find((m) => m.k === k) ?? METRICAS[0];
export const valor = (p: Punto, k: ClaveMetrica) => p[k];
export const fmt = (v: number | null, m: Metrica) => (v === null ? "–" : `${m.k === "residuo" && v > 0 ? "+" : ""}${v.toFixed(m.dec)}${m.unidad}`);
export const EJES_X = [
  { k: "pib", nombre: "GDP per capita, PPP (constant 2021 international $), log scale" },
  { k: "uso", nombre: "Claude use per working-age person (world = 1), log scale" },
] as const;
export type ClaveEjeX = (typeof EJES_X)[number]["k"];

export const bandera = (iso2: string, grande = false) => `/flags/${iso2}${grande ? "@4" : ""}.webp`;
export const posicion = (r: number | null) =>
  r === null ? "" : Math.abs(r) < 1.5 ? "in line with what its income predicts" : `${Math.abs(r).toFixed(1)} points ${r > 0 ? "above" : "below"} what its income predicts`;
