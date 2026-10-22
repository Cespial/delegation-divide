"use client";
// What drives a country's ADI: the same nine ISCO-08 major groups twice, once as shares of employment and once as
// points of delegable task time (their sum is the ADI), for the country and for the world. Groups run from most to
// least delegable and are shaded by their ADI on one hue, so a small dark block that grows in the second bar is a
// group that punches above its weight. Hovering a block lights the same group in all four bars.
import { scaleLinear } from "d3-scale";
import { useState } from "react";

export type Bloque = { gg: string; share: number; adi: number; contrib: number };
const tono = scaleLinear<string>().domain([10, 85]).range(["#d4ebe8", "#083d39"]).clamp(true);
const tinta = (adi: number) => (adi > 48 ? "#fff" : "#1a1918");

export function Descomposicion({ pais, mundo, nombre, nombres }: { pais: Bloque[]; mundo: Bloque[]; nombre: string; nombres: Record<string, string> }) {
  const [sel, setSel] = useState<string | null>(null);
  const orden = [...mundo].sort((a, b) => b.adi - a.adi).map((g) => g.gg);
  const de = (lista: Bloque[]) => orden.map((k) => lista.find((g) => g.gg === k)!).filter(Boolean);
  const adiPais = pais.reduce((a, g) => a + g.contrib, 0), adiMundo = mundo.reduce((a, g) => a + g.contrib, 0);
  const barra = (lista: Bloque[], campo: "share" | "contrib", etiqueta: string, total: number) => (
    <div className="desc-fila">
      <span className="desc-etiqueta">{etiqueta}</span>
      <div className="desc-pista" role="img" aria-label={`${etiqueta}: ${de(lista).map((g) => `${nombres[g.gg]} ${g[campo].toFixed(1)}`).join(", ")}`}>
        {de(lista).map((g) => (
          <div key={g.gg} className={`desc-bloque${sel && sel !== g.gg ? " apagado" : ""}`} style={{ width: `${g[campo]}%`, background: tono(g.adi), color: tinta(g.adi) }}
            onPointerEnter={() => setSel(g.gg)} onPointerLeave={() => setSel(null)}>
            {g[campo] >= 4.5 && <span>{g.gg}</span>}
          </div>
        ))}
      </div>
      <span className="desc-total">{campo === "share" ? "100%" : `${total.toFixed(1)}%`}</span>
    </div>
  );
  const g = sel ? pais.find((x) => x.gg === sel) : null, w = sel ? mundo.find((x) => x.gg === sel) : null;
  return (
    <div className="descomposicion">
      <div className="desc-grupo"><span className="rotulo">Share of employment</span>
        {barra(pais, "share", nombre, 100)}{barra(mundo, "share", "World", 100)}</div>
      <div className="desc-grupo"><span className="rotulo">Points of delegable task time (sum = ADI)</span>
        {barra(pais, "contrib", nombre, adiPais)}{barra(mundo, "contrib", "World", adiMundo)}</div>
      <p className="desc-lectura" aria-live="polite">
        {g && w ? <><b>{sel} · {nombres[sel!]}</b>: {g.share.toFixed(1)}% of {nombre}’s workers (world {w.share.toFixed(1)}%), ADI {g.adi.toFixed(1)}% in this mix,
          adding <b>{g.contrib.toFixed(1)} points</b> to {nombre}’s {adiPais.toFixed(1)}%.</> : <>Hover a block to read one group. Shade: the group’s ADI, light 10% to dark 85%.</>}
      </p>
      <table className="tabla desc-tabla">
        <thead><tr><th>Major group</th><th className="n">Employment</th><th className="n">World</th><th className="n">ADI of group</th><th className="n">Points of ADI</th></tr></thead>
        <tbody>{de(pais).map((x) => {
          const y = mundo.find((z) => z.gg === x.gg)!;
          return (
            <tr key={x.gg} className={sel === x.gg ? "destacada" : undefined} onPointerEnter={() => setSel(x.gg)} onPointerLeave={() => setSel(null)}>
              <td><i className="desc-muestra" style={{ background: tono(x.adi) }} />{x.gg} · {nombres[x.gg]}</td>
              <td className="n num">{x.share.toFixed(1)}%</td><td className="n num">{y.share.toFixed(1)}%</td>
              <td className="n num">{x.adi.toFixed(1)}</td><td className="n valor">{x.contrib.toFixed(1)}</td>
            </tr>
          );
        })}</tbody>
      </table>
    </div>
  );
}
