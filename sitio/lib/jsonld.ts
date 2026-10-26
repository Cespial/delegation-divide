// Structured data shared by several pages. The Dataset block is what Google Dataset Search indexes.
import { AUTORES, DOI_ARXIV, LAB, SITE, cifra, resumen } from "./datos";

export function jsonDataset() {
  return {
    "@context": "https://schema.org", "@type": "Dataset", "@id": `https://doi.org/${resumen.doi_datos}`,
    name: "Agent Delegability Index (ADI) v2026.1",
    description: `Task-level ratings of how much work AI agents can take over: ${cifra("cobertura.tareas")} O*NET task statements rated on four delegation levels and four barriers by two language models, aggregated to ${cifra("cobertura.isco")} ISCO-08 occupations and ${cifra("cobertura.paises")} countries with 95% bootstrap intervals.`,
    url: `${SITE}/adi/data`, identifier: `https://doi.org/${resumen.doi_datos}`, sameAs: [`https://doi.org/${resumen.doi_datos}`, "https://huggingface.co/datasets/Cespial/adi"],
    version: resumen.version, datePublished: resumen.fecha, license: "https://creativecommons.org/licenses/by/4.0/", isAccessibleForFree: true,
    creator: AUTORES.map((a) => ({ "@type": "Person", name: a.nombre, affiliation: { "@type": "Organization", name: a.afil }, sameAs: `https://orcid.org/${a.orcid}` })),
    keywords: ["AI agents", "delegation", "automation", "ISCO-08", "O*NET", "labour markets", "occupations", "countries"],
    spatialCoverage: { "@type": "Place", name: `World (${cifra("cobertura.paises")} countries)` }, temporalCoverage: "2026",
    variableMeasured: ["ADI: share of task time at partial or full delegation (L2–L3)", "ADI3: share of task time at full delegation (L3)", "ADIs: expected share of working time delegable", "Barrier shares: physical presence, accountability, trust and care, access to systems"],
    citation: [`https://doi.org/${DOI_ARXIV}`, `https://doi.org/${resumen.doi_prerregistro}`],
    publisher: { "@type": "Organization", "@id": `${SITE}/#org`, name: LAB, url: SITE },
    distribution: [
      { "@type": "DataDownload", encodingFormat: "text/csv", contentUrl: `${SITE}/data/adi_isco.csv`, name: "Occupations" },
      { "@type": "DataDownload", encodingFormat: "text/csv", contentUrl: `${SITE}/data/adi_pais.csv`, name: "Countries" },
      { "@type": "DataDownload", encodingFormat: "text/csv", contentUrl: `${SITE}/data/adi_tarea.csv`, name: "Tasks" },
      { "@type": "DataDownload", encodingFormat: "application/json", contentUrl: `${SITE}/adi/v2026.1/index.json`, name: "JSON API index" },
    ],
  };
}
