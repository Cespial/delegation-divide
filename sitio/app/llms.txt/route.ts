import { N_OCUP, N_PAISES, SITE, cifra, resumen } from "@/lib/datos";

export const dynamic = "force-static";

// Plain-text map of the index for language models (llmstxt.org). Every number comes from the claims file.
export function GET() {
  const t = `# Agent Delegability Index (ADI)

> Open, preregistered index of how much work AI agents can take over, for ${N_OCUP} ISCO-08 occupations and ${N_PAISES} countries (v${resumen.version}).
> Headline: ${cifra("titular.global.l2")}% of task time in world employment is at least partly delegable to AI agents (levels L2–L3) in 2026
> (95% interval ${cifra("titular.global.l2.lo")}–${cifra("titular.global.l2.hi")}%); only ${cifra("titular.global.l3")}% can be handed over in full (L3).
> ${cifra("titular.ingreso.alto.l2")}% in high-income vs ${cifra("titular.ingreso.bajo.l2")}% in low-income countries (the "delegation divide": +${cifra("h1.pendiente")} pp per log point of GDP per capita).
> Four levels per task: L0 no role, L1 augmentation, L2 partial delegation, L3 full delegation. Four barriers: physical presence, accountability, trust and care, access to systems.
> Rated by Claude Sonnet 5.5 and Claude Haiku 5.5 on ${cifra("cobertura.tareas")} O*NET 30.2 tasks; a blind human rating of ${cifra("n.humano")} tasks, led by a coauthor with student raters, agrees at kappa ${cifra("agree.kappa.humano.modelo")}.
> Data DOI: https://doi.org/${resumen.doi_datos} · Preregistration: https://doi.org/${resumen.doi_prerregistro}

## Pages
- [Occupations](${SITE}/occupations): all ${N_OCUP} occupations ranked; one page each at ${SITE}/occupations/<ISCO-08 code>
- [Countries](${SITE}/countries): map and ranking; one page each at ${SITE}/countries/<ISO3>
- [Methodology](${SITE}/methodology): levels, barriers, rubric, aggregation, validation, deviations from the preregistration
- [Report](${SITE}/report): The Delegation Divide, ADI Report 2026.1
- [Data](${SITE}/data): downloads, API, Python package, MCP server, citation

## API (static JSON, no key)
- ${SITE}/adi/v${resumen.version}/index.json
- ${SITE}/adi/v${resumen.version}/isco/<ISCO-08>.json (e.g. ${SITE}/adi/v${resumen.version}/isco/2512.json)
- ${SITE}/adi/v${resumen.version}/country/<ISO3>.json (e.g. ${SITE}/adi/v${resumen.version}/country/COL.json)
Every record carries a "cite" field.

## Tables
- ${SITE}/data/adi_isco.csv, ${SITE}/data/adi_pais.csv, ${SITE}/data/adi_tarea.csv (and .parquet); columns in ${SITE}/data/DATA_DICTIONARY.md
- ${SITE}/data/claims.jsonl: every number in the paper, the report and this site

## Optional
- [llms-full.txt](${SITE}/llms-full.txt): definitions, column schema, tool reference
`;
  return new Response(t, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
