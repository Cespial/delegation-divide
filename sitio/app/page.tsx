import Link from "next/link";
import { Buscador, type ItemBusqueda, type Sugerencia } from "@/components/Buscador";
import { JsonLd } from "@/components/JsonLd";
import { Leaderboard } from "@/components/Leaderboard";
import { Marca } from "@/components/Marca";
import { GG, LAB, N_OCUP, N_PAISES, SITE, cifra, ocupaciones, ordinal, paises, resumen } from "@/lib/datos";
import { NOVEDADES, fechaCorta } from "@/lib/novedades";

// Lab home, laid out like vals.ai/home: dated strip, hero with quick lookup, the index leaderboard with tabs,
// latest reports with findings, then the products. Identity (paper, ink, teal, Barlow) is the ADI's.
const externo = (h: string) => h.startsWith("http");

const SUGERENCIAS: Sugerencia[] = [
  { etiqueta: "Software developers", q: "2512" },
  { etiqueta: "Economists", q: "2631" },
  { etiqueta: "Colombia", q: "Colombia" },
  { etiqueta: "United States", q: "United States" },
  { etiqueta: "Singapore", q: "Singapore" },
];

export default function InicioLab() {
  const items: ItemBusqueda[] = [
    ...ocupaciones.map((o) => ({
      href: `/adi/occupations/${o.isco}`,
      nombre: o.titulo,
      codigo: o.isco,
      valor: `${o.l2.toFixed(1)}%`,
      subtitulo: `${GG[o.gg]} · ${ordinal(o.rk)} of ${N_OCUP}`,
    })),
    ...paises.map((p) => ({
      href: `/adi/countries/${p.iso3}`,
      nombre: p.nombre,
      codigo: p.iso3,
      iso2: p.iso2,
      valor: `${p.l2.toFixed(1)}%`,
      subtitulo: `${p.ingreso_nombre} · ${ordinal(p.rk)} of ${N_PAISES}`,
    })),
  ];
  return (
    <>
      <div className="tira">
        <ul className="envoltura" aria-label="Latest releases">
          {NOVEDADES.map((n) => (
            <li key={n.titulo}><time dateTime={n.fecha}>{fechaCorta(n.fecha)}</time>
              {externo(n.href) ? <a href={n.href}>{n.corto}</a> : <Link href={n.href}>{n.corto}</Link>}</li>
          ))}
        </ul>
      </div>

      <section className="portada portada-lab">
        <div className="envoltura">
          <p className="lema">Independent indices of what AI agents can do</p>
          <h1 className="titulo">Measuring how much of the world’s work AI agents can take over</h1>
          <p className="entrada">{LAB} builds open, preregistered indices of AI agents at work, task by task, and publishes every rating, score and line of code
            behind the numbers. The first is the Agent Delegability Index, covering {N_OCUP} occupations and {N_PAISES} countries.</p>
          <div style={{ maxWidth: 640, marginTop: 26 }}>
            <Buscador items={items} placeholder="Quick lookup: occupation, ISCO-08 code, country or ISO3…" sugerencias={SUGERENCIAS} />
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="tablero">
            <div className="tablero-cabeza">
              <Link href="/adi" className="sello"><Marca decorativa /><span>Agent Delegability Index<br /><b>v{resumen.version}</b> · updated 22 Oct 2026</span></Link>
              <div className="botones">
                <Link className="boton" href="/adi/countries">Country atlas ({N_PAISES})</Link>
                <Link className="boton lleno" href="/adi/occupations">View full results ({N_OCUP})</Link>
              </div>
            </div>
            <div className="tablero-cuerpo">
              <div>
                <Leaderboard />
                <p className="nota" style={{ marginTop: 10 }}>ISCO-08 major groups. Employment-weighted means over {N_OCUP} unit groups; whiskers are 95% bootstrap intervals.</p>
              </div>
              <div className="titular">
                <span className="cifra">{cifra("titular.global.l2")}<small>%</small></span>
                <p>of task time in world employment is at least partly delegable to AI agents in 2026. Only {cifra("titular.global.l3")}% can be handed over in full.</p>
                <div className="intervalo">95% interval {cifra("titular.global.l2.lo")}–{cifra("titular.global.l2.hi")}% · employment-weighted</div>
                <p><Link href="/adi/countries">From {cifra("titular.ingreso.bajo.l2")}% in low-income to {cifra("titular.ingreso.alto.l2")}% in high-income countries</Link></p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado"><div><h2 className="titulo-2">Latest reports</h2><p>Recent releases and what they found.</p></div></div>
          <ul className="informes">
            {NOVEDADES.map((n) => (
              <li key={n.titulo}>
                <div className="informe-meta"><time dateTime={n.fecha}>{fechaCorta(n.fecha)}</time><span>{n.producto}</span></div>
                <div>
                  <h3 className="titulo-3">{externo(n.href) ? <a href={n.href}>{n.titulo}</a> : <Link href={n.href}>{n.titulo}</Link>}</h3>
                  <p><b>{n.entrada}</b></p>
                  <ul>{n.puntos.map((t) => <li key={t}>{t}</li>)}</ul>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="seccion">
        <div className="envoltura">
          <div className="encabezado"><div><h2 className="titulo-2">Products</h2><p>Each index is versioned, has a DOI and keeps its numbers at fixed paths.</p></div></div>
          <ul className="productos">
            <li>
              <Link href="/adi" className="producto-fila">
                <Marca decorativa />
                <div><h3 className="titulo-3">Agent Delegability Index</h3>
                  <p>How much of each task a current AI agent can carry out, from helping a person to finishing the job alone.</p></div>
                <dl>
                  <div><dt>Tasks</dt><dd>{cifra("cobertura.tareas")}</dd></div>
                  <div><dt>Occupations</dt><dd>{N_OCUP}</dd></div>
                  <div><dt>Countries</dt><dd>{N_PAISES}</dd></div>
                  <div><dt>Version</dt><dd>v{resumen.version}</dd></div>
                </dl>
              </Link>
            </li>
          </ul>
          <p className="nota" style={{ marginTop: 18 }}>Every record is citable and machine-readable: <Link href="/adi/data">data, API, Python package and MCP server</Link>.</p>
        </div>
      </section>
      <JsonLd datos={{ "@context": "https://schema.org", "@type": "CollectionPage", url: SITE, name: LAB, about: { "@id": `${SITE}/#org` },
        hasPart: [{ "@type": "Dataset", name: "Agent Delegability Index (ADI) v2026.1", url: `${SITE}/adi`, identifier: `https://doi.org/${resumen.doi_datos}` }] }} />
    </>
  );
}
