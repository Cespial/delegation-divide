// Data layer of the site. Everything comes from sitio/datos/*.json, written by datos/exportar.py from the published
// outputs of ADI v2026.1 (the same files as the paper and the report). Nothing here computes an index value.
import fs from "node:fs";
import path from "node:path";
import resumenJson from "@/datos/resumen.json";
import ocupacionesJson from "@/datos/ocupaciones.json";
import gruposJson from "@/datos/grupos.json";
import paisesJson from "@/datos/paises.json";
import mapaJson from "@/datos/mapa.json";
import colombiaJson from "@/datos/colombia.json";
import h4Json from "@/datos/h4.json";
import informeJson from "@/datos/informe.json";

export type Comparador = { v: number; p: number } | null;
export type Ocupacion = {
  isco: string; titulo: string; gg: string; sub: string;
  l2: number; l2_lo: number; l2_hi: number; l3: number; l3_lo: number; l3_hi: number; s: number; s_lo: number; s_hi: number;
  n: number; imp: boolean; emp: number; b: number[]; rk: number; rk3: number; rks: number;
  comp: Record<string, Comparador>;
};
export type Grupo = { gg: string; nombre: string; l2: number; lo: number; hi: number; l3: number; s: number; b: number[]; emp: number; n: number };
export type FilaPerfil = { tema: string; nombre: string; unidad: string; col: string; puesto: string; mejor: string; region: string; alto: string; mundo: string; fuente: string };
export type Pais = {
  iso3: string; nombre: string; region: string; region_nombre: string; ingreso: string; ingreso_nombre: string; anio: number; res: number;
  l2: number; lo: number; hi: number; l3: number; s: number; l2_iguales: number; emp: number; pib: number | null; inf: number | null; uso: number | null; rk: number;
  perfil: { hallazgo: string; hallazgo_fig: string; n_region: number; region_l2: string; mundo_l2: string; filas: FilaPerfil[]; barras: [string, string, number][] };
};
export type Tarea = { id: number; t: string; o: string; w: number; n: number; s: number; m: number | null; h: number | null; so: number | null; b: (number | null)[]; core: boolean };

export const resumen = resumenJson as { cifras: Record<string, string>; version: string; fecha: string; doi_datos: string; doi_datos_concepto: string; doi_prerregistro: string; doi_informe: string | null };
export const cifra = (id: string): string => {
  const v = resumen.cifras[id];
  if (v === undefined) throw new Error(`cifra inexistente: ${id}`); // a missing id fails the build, as in the report
  return v;
};
export const ocupaciones = (ocupacionesJson as { filas: Ocupacion[] }).filas;
export const comparadores = (ocupacionesJson as { comparadores: Record<string, string> }).comparadores;
export const GG = (ocupacionesJson as { grupos: Record<string, string> }).grupos;
export const grupos = gruposJson as Grupo[];
export const paises = paisesJson as Pais[];
export const mapa = mapaJson as { ancho: number; alto: number; paises: { iso3: string; nombre: string; d: string }[]; puntos: { iso3: string; x: number; y: number }[] };
export const colombia = colombiaJson as { grupo: string; cat: string; l2: number; lo: number; hi: number; l3: number; emp: number }[];
export const h4 = h4Json as { curva: [number, number][]; puntos: [number, number][]; pico_lmin: number };

export const ocupacion = (isco: string) => ocupaciones.find((o) => o.isco === isco);
export const pais = (iso3: string) => paises.find((p) => p.iso3 === iso3);
export const tareas = (isco: string): Tarea[] =>
  JSON.parse(fs.readFileSync(path.join(process.cwd(), "datos", "tareas", `${isco}.json`), "utf8"));

export const N_OCUP = ocupaciones.length;
export const N_PAISES = paises.length;
export const BARRERAS = [
  { k: "physical", nombre: "Physical presence", color: "var(--b-fisica)" },
  { k: "accountability", nombre: "Accountability", color: "var(--b-resp)" },
  { k: "trust", nombre: "Trust and care", color: "var(--b-conf)" },
  { k: "access", nombre: "Access to systems", color: "var(--b-acceso)" },
];
export const NIVELES = [
  { k: "L0", nombre: "No meaningful role", corto: "No role" },
  { k: "L1", nombre: "Augmentation", corto: "Augment" },
  { k: "L2", nombre: "Partial delegation", corto: "Partial" },
  { k: "L3", nombre: "Full delegation", corto: "Full" },
];
export const INGRESOS = [
  { k: "low", nombre: "Low income", id: "bajo" },
  { k: "lower-middle", nombre: "Lower-middle income", id: "medio_bajo" },
  { k: "upper-middle", nombre: "Upper-middle income", id: "medio_alto" },
  { k: "high", nombre: "High income", id: "alto" },
];

export const f1 = (v: number | null | undefined) => (v === null || v === undefined ? "–" : v.toFixed(1));
export const minutos = (m: number | null) => {
  if (m === null) return "–";
  if (m < 60) return `${Math.round(m)} min`;
  const h = m / 60;
  return h < 10 ? `${h.toFixed(1)} h` : `${Math.round(h)} h`;
};
export const ordinal = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[n % 10] ?? "th"}`;

// Site URL: explicit env var, else the Vercel production domain, else local.
export const SITE =
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : "http://localhost:3000");

export const AUTORES = [
  { nombre: "Cristian Espinal Maya", bib: "Espinal Maya, Cristian", afil: "Universidad Nacional de Colombia, Facultad de Minas", orcid: "0009-0000-1009-8388" },
  { nombre: "Santiago Jiménez Londoño", bib: "Jim{\\'e}nez Londo{\\~n}o, Santiago", afil: "Universidad EAFIT", orcid: "0009-0007-9862-7133" },
];
export const REPO = "https://github.com/Cespial/delegation-divide";
export const HF = "https://huggingface.co/datasets/Cespial/adi";
export const PDF_INFORME = "/report/delegation-divide-report-2026.pdf";
// The PDF is served only once the cleaned copy (limpiadoc) exists; until then the site points to /report.
export const informe = informeJson as { paginas: number; pdf: boolean; mb: number | null };
export const ENLACE_INFORME = informe.pdf ? PDF_INFORME : "/report";
export const TITULO_PAPER = "The Delegation Divide: An Open Index of AI-Agent Delegability across Occupations and Countries";

// PyPI packages: until they are published, the site shows the install-from-GitHub command.
export const PYPI = false;
export const INSTALAR = PYPI ? "pip install adi-index" : 'pip install "adi-index @ git+https://github.com/Cespial/delegation-divide#subdirectory=herramientas/adi-index"';
export const INSTALAR_MCP = PYPI ? "pip install adi-mcp" : 'pip install "adi-mcp @ git+https://github.com/Cespial/delegation-divide#subdirectory=herramientas/adi-mcp"';
