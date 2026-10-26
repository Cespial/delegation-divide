// Citation strings shown on every page. The report keeps its own DOI once reserved (release/zenodo_informe.py);
// until then it is cited with the repository URL, exactly as the PDF does.
import { ARXIV, ARXIV_ID, AUTORES, DOI_ARXIV, LAB, REPO, TITULO_PAPER, resumen } from "./datos";

const autoresTexto = "Espinal Maya, Cristian, and Santiago Jiménez Londoño";
const autoresBib = AUTORES.map((a) => a.bib).join(" and ");

export function citaInforme() {
  const doi = resumen.doi_informe;
  const url = doi ? `https://doi.org/${doi}` : REPO;
  return {
    texto: `${autoresTexto}. 2026. ${TITULO_PAPER}. ADI Report 2026.1. ${LAB}. ${url}`,
    bibtex: [
      "@techreport{espinal2026delegationreport,",
      `  title       = {${TITULO_PAPER}},`,
      `  author      = {${autoresBib}},`,
      `  institution = {${LAB}},`,
      "  type        = {ADI Report},",
      "  number      = {2026.1},",
      "  year        = {2026},",
      ...(doi ? [`  doi         = {${doi}},`] : []),
      `  url         = {${url}}`,
      "}",
    ].join("\n"),
  };
}

export function citaDatos() {
  const doi = resumen.doi_datos;
  return {
    texto: `${autoresTexto}. 2026. ADI v2026.1: Agent Delegability Index data, code and MCP server. Zenodo. https://doi.org/${doi}`,
    bibtex: [
      "@misc{espinal2026adidata,",
      "  title     = {{ADI} v2026.1: Agent Delegability Index data, code and {MCP} server},",
      `  author    = {${autoresBib}},`,
      "  year      = {2026},",
      "  publisher = {Zenodo},",
      "  version   = {v2026.1},",
      `  doi       = {${doi}},`,
      `  url       = {https://doi.org/${doi}}`,
      "}",
    ].join("\n"),
  };
}

export function citaPaper() {
  return {
    texto: `${autoresTexto}. 2026. ${TITULO_PAPER}. arXiv:${ARXIV_ID} [econ.GN]. https://doi.org/${DOI_ARXIV}`,
    bibtex: [
      "@misc{espinal2026delegation,",
      `  title         = {${TITULO_PAPER}},`,
      `  author        = {${autoresBib}},`,
      "  year          = {2026},",
      `  eprint        = {${ARXIV_ID}},`,
      "  archivePrefix = {arXiv},",
      "  primaryClass  = {econ.GN},",
      `  doi           = {${DOI_ARXIV}},`,
      `  url           = {${ARXIV}}`,
      "}",
    ].join("\n"),
  };
}

// A record (occupation or country) is cited as the dataset, with the record named in the note.
export function citaRegistro(nombre: string, url: string) {
  const d = citaDatos();
  return {
    texto: `${d.texto}. Record: ${nombre}, ${url}`,
    bibtex: d.bibtex.replace(/\n}$/, `,\n  note      = {Record: ${nombre.replace(/[{}]/g, "")}}\n}`),
  };
}
