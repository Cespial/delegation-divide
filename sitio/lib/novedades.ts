// Dated releases of the lab, newest first. The home page shows them twice, as on vals.ai/home: one line each in the
// strip under the header, and in full (lead sentence and findings) under "Latest reports".
import { ARXIV, ARXIV_ID, N_OCUP, N_PAISES, cifra, informe, resumen } from "./datos";

export type Novedad = { fecha: string; corto: string; titulo: string; href: string; entrada: string; puntos: string[]; producto: string };

export const NOVEDADES: Novedad[] = [
  {
    fecha: "2026-10-22", corto: "ADI paper on arXiv", titulo: "The Delegation Divide: the paper on arXiv", href: ARXIV, producto: "ADI",
    entrada: `The peer-review version of the index, with the same data and numbers as the report.`,
    puntos: [
      `${cifra("titular.global.l2")}% of task time in world employment is at least partly delegable to AI agents; only ${cifra("titular.global.l3")}% in full.`,
      `Four preregistered hypotheses tested on ${cifra("cobertura.tareas")} O*NET tasks, ${N_OCUP} occupations and ${N_PAISES} countries.`,
      `Cite as arXiv:${ARXIV_ID} [econ.GN], cross-listed to cs.AI and cs.CY.`,
    ],
  },
  {
    fecha: "2026-10-22", corto: "ADI Report 2026.1", titulo: "The Delegation Divide: ADI Report 2026.1", href: "/adi/report", producto: "ADI",
    entrada: `About a third of the world’s working time is at least partly delegable to AI agents, and full delegation is rare.`,
    puntos: [
      `${cifra("titular.global.l2")}% of task time in world employment can be at least partly delegated; only ${cifra("titular.global.l3")}% in full.`,
      `Delegable work rises with income, from ${cifra("titular.ingreso.bajo.l2")}% in low-income to ${cifra("titular.ingreso.alto.l2")}% in high-income countries.`,
      `Full delegation is most likely for tasks that take a person about ${cifra("h4.pico.minutos")} minutes.`,
    ],
  },
  {
    fecha: "2026-10-22", corto: "ADI v2026.1 dataset", titulo: "ADI v2026.1 dataset on Zenodo", href: "/adi/data", producto: "ADI",
    entrada: `Every rating, score and line of code behind the index, under CC BY 4.0 and MIT.`,
    puntos: [
      `Ratings for all ${cifra("cobertura.tareas")} O*NET task statements on four delegation levels and four barriers.`,
      `Scores with 95% intervals for ${N_OCUP} ISCO-08 occupations and ${N_PAISES} countries, as CSV, Parquet and a static JSON API.`,
      `A Python package and an MCP server that return each record with its citation. doi:${resumen.doi_datos}`,
    ],
  },
  {
    fecha: "2026-10-21", corto: "ADI preregistration", titulo: "ADI preregistration on OSF", href: `https://doi.org/${resumen.doi_prerregistro}`, producto: "ADI",
    entrada: `Hypotheses, rubric and analysis plan were registered before the main scoring run.`,
    puntos: [
      `Four hypotheses: the income gradient, the gap with observed AI use, agreement with earlier exposure indices, and task length.`,
      `Deviations from the registered plan are dated and listed in the methodology.`,
      `The registration is public on OSF Registries: doi:${resumen.doi_prerregistro}.`,
    ],
  },
];

export const fechaCorta = (f: string) => f.replaceAll("-", "/");
export const PAGINAS_INFORME = informe.paginas;
