import fs from "node:fs";
import path from "node:path";
import type { Metadata } from "next";
import { Cita } from "@/components/Cita";
import { JsonLd } from "@/components/JsonLd";
import { HF, INSTALAR, INSTALAR_MCP, REPO, cifra, resumen } from "@/lib/datos";
import { citaDatos } from "@/lib/citar";
import { jsonDataset } from "@/lib/jsonld";

export const metadata: Metadata = {
  title: "Data, API and code",
  description: `Download the Agent Delegability Index v${resumen.version}: CSV and Parquet tables for ${cifra("cobertura.isco")} occupations, ${cifra("cobertura.paises")} countries and every task rating, a static JSON API, a Python package and an MCP server. CC BY 4.0, doi:${resumen.doi_datos}.`,
  alternates: { canonical: "/adi/data" },
};

const tam = (f: string) => {
  const b = fs.statSync(path.join(process.cwd(), "public", "data", f)).size;
  return b < 1e6 ? `${Math.round(b / 1e3)} KB` : `${(b / 1e6).toFixed(1)} MB`;
};
const TABLAS: [string, string, string[]][] = [
  ["Occupations", `${cifra("cobertura.isco")} ISCO-08 unit groups: ADI with its 95% interval, ADI3, ADIs, the four barrier shares and the number of tasks.`, ["adi_isco.csv", "adi_isco.parquet"]],
  ["Countries", `${cifra("cobertura.paises")} countries: the three indices, total employment, income group, ILOSTAT year and the ISCO resolution used.`, ["adi_pais.csv", "adi_pais.parquet"]],
  ["Tasks", `All ${cifra("cobertura.tareas")} task statements: consensus level, each model’s level, share of time, human minutes and the four barriers.`, ["adi_tarea.csv", "adi_tarea.parquet"]],
  ["Claims", "Every number in the paper, the report and this site, with its identifier and the script that produced it.", ["claims.jsonl"]],
  ["Dictionary and checksums", "Column definitions for every table, and SHA-256 sums of the release.", ["DATA_DICTIONARY.md", "SHA256SUMS"]],
];

export default function Datos() {
  return (
    <>
      <section className="seccion">
        <div className="envoltura">
          <span className="rotulo">Data · v{resumen.version} · CC BY 4.0</span>
          <h1 className="titulo" style={{ margin: "14px 0 18px", maxWidth: "18ch" }}>Data, API and code</h1>
          <p className="entrada" style={{ maxWidth: "62ch" }}>Everything behind the index is open: the ratings of every task, the scores of every occupation and country, the rubric,
            the prompts and the code that builds them. The archived release is on Zenodo; the files below are the same tables.</p>
          <div className="botones">
            <a className="boton lleno" href={`https://doi.org/${resumen.doi_datos}`}>Zenodo · doi:{resumen.doi_datos}</a>
            <a className="boton" href={HF}>Hugging Face</a><a className="boton" href={REPO}>GitHub</a>
          </div>
          <div className="tabla-marco" style={{ marginTop: 32 }}><table className="tabla">
            <thead><tr><th>Table</th><th>Contents</th><th>Files</th></tr></thead>
            <tbody>{TABLAS.map(([t, d, fs_]) => (
              <tr key={t}><td><b>{t}</b></td><td>{d}</td>
                <td><span className="descargas">{fs_.map((f) => <a key={f} href={`/data/${f}`} download><code>{f}</code> <span className="nota">{tam(f)}</span></a>)}</span></td></tr>
            ))}</tbody>
          </table></div>
          <p className="nota" style={{ marginTop: 10 }}>The raw ratings of each model (one JSON line per task, with the rubric hash and a timestamp) are in the Zenodo record, under release/v2026.1.</p>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado"><div><span className="rotulo">Static JSON API</span>
            <h2 className="titulo-2" style={{ marginTop: 10 }}>One file per record, with its citation</h2>
            <p>No key, no rate limit, CORS open. Paths are versioned, so a link never changes meaning.</p></div></div>
          <div className="tabla-marco"><table className="tabla"><thead><tr><th>Path</th><th>Returns</th></tr></thead><tbody>
            <tr><td><a href="/adi/v2026.1/index.json"><code>/adi/v2026.1/index.json</code></a></td><td>List of occupations and countries with their headline values.</td></tr>
            <tr><td><a href="/adi/v2026.1/isco/2512.json"><code>/adi/v2026.1/isco/&#123;ISCO-08&#125;.json</code></a></td><td>One occupation: the three indices with 95% intervals, barrier shares, rank and a <code>cite</code> field.</td></tr>
            <tr><td><a href="/adi/v2026.1/country/COL.json"><code>/adi/v2026.1/country/&#123;ISO3&#125;.json</code></a></td><td>One country: indices, intervals, income group and a <code>cite</code> field.</td></tr>
          </tbody></table></div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div><span className="rotulo">Python</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 14px" }}>adi-index</h2>
            <pre className="bloque">{`${INSTALAR}\n\nadi lookup 2512\nadi country COL\nadi top -n 10\nadi cite bibtex`}</pre>
            <p className="nota">Command line and library. The tables travel inside the package, so it works offline.</p></div>
          <div><span className="rotulo">MCP server</span>
            <h2 className="titulo-2" style={{ margin: "10px 0 14px" }}>adi-mcp</h2>
            <pre className="bloque">{`${INSTALAR_MCP}\n\nclaude mcp add adi -- adi-mcp`}</pre>
            <p className="nota">Four tools for AI assistants: <code>lookup_occupation</code>, <code>country_profile</code>, <code>top_occupations</code>, <code>cite</code>.</p></div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura dos">
          <div><span className="rotulo">How to cite the data</span><div style={{ marginTop: 14 }}><Cita titulo="Text" cita={citaDatos()} /></div></div>
          <div><span className="rotulo">For language models</span>
            <p style={{ marginTop: 14 }}><a href="/llms.txt"><code>/llms.txt</code></a> is a plain-text map of the index; <a href="/llms-full.txt"><code>/llms-full.txt</code></a> adds
              definitions, column schema and the tool reference.</p>
            <p>Licences: data and text CC BY 4.0; code MIT. O*NET content is used under CC BY 4.0 from the U.S. Department of Labor; ILOSTAT data under CC BY 4.0.</p></div>
        </div>
      </section>
      <JsonLd datos={jsonDataset()} />
    </>
  );
}
