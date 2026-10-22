// Card shown on hover or focus of a country in any chart: flag, name, the plotted value with its interval, context.
import { bandera, fmt, posicion, type ClaveMetrica, type Metrica, type Punto } from "@/lib/graficas";

export function TarjetaPais({ p, y, m, total, style }: { p: Punto; y: ClaveMetrica; m: Metrica; total: number; style: React.CSSProperties }) {
  return (
    <div className="tarjeta-dato" role="status" style={style}>
      <div className="tarjeta-cab"><img src={bandera(p.iso2)} alt="" width={28} height={21} /><b>{p.nombre}</b></div>
      <div className="nota">{p.region} · {p.ingreso_nombre}</div>
      <div className="tarjeta-cifra">{fmt(p[y], m)}<span>{m.corto}{y === "l2" ? ` · 95% ${p.lo.toFixed(1)}–${p.hi.toFixed(1)}` : ""}</span></div>
      <dl>
        {y !== "l2" && <><dt>ADI</dt><dd>{p.l2.toFixed(1)}%</dd></>}
        <dt>Rank</dt><dd>{p.rk} of {total}</dd>
        {p.pib !== null && <><dt>GDP pc</dt><dd>${p.pib.toLocaleString("en-US")}</dd></>}
        {p.residuo !== null && <><dt>vs income</dt><dd>{p.residuo > 0 ? "+" : ""}{p.residuo.toFixed(1)} pts</dd></>}
      </dl>
      <div className="tarjeta-pie">{posicion(p.residuo)}</div>
    </div>
  );
}
