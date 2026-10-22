// Inline bar on a 0–max scale with the 95% bootstrap interval as a whisker; the value itself is printed beside it, never only drawn.
export function Barra({ v, lo, hi, max = 100, fuerte = false, marca: referencia, etiqueta }: {
  v: number; lo?: number; hi?: number; max?: number; fuerte?: boolean; marca?: number; etiqueta?: string;
}) {
  const p = (x: number) => `${Math.max(0, Math.min(100, (100 * x) / max))}%`;
  return (
    <div className={`barra${fuerte ? " fuerte" : ""}`} role="img" aria-label={etiqueta ?? `${v.toFixed(1)}%${lo !== undefined && hi !== undefined ? `, 95% interval ${lo.toFixed(1)} to ${hi.toFixed(1)}` : ""}`}>
      <div className="relleno" style={{ width: p(v) }} />
      {lo !== undefined && hi !== undefined && hi > lo && <div className="bigote" style={{ left: p(lo), width: `calc(${p(hi)} - ${p(lo)})` }} />}
      {referencia !== undefined && <div className="marca-ref" style={{ left: p(referencia) }} />}
    </div>
  );
}

export function Barreras({ b }: { b: (number | null)[] }) {
  const B = [["Physical presence", "var(--b-fisica)"], ["Accountability", "var(--b-resp)"], ["Trust and care", "var(--b-conf)"], ["Access to systems", "var(--b-acceso)"]];
  return (
    <div className="barreras">
      {B.map(([nom, color], i) => (
        <div className="barrera" key={nom}>
          <span>{nom}</span>
          <div className="pista" role="img" aria-label={`${nom}: ${b[i]?.toFixed(1)}% of task weight`}><i style={{ width: `${b[i] ?? 0}%`, background: color }} /></div>
          <span className="v">{b[i] === null ? "–" : `${b[i]!.toFixed(0)}%`}</span>
        </div>
      ))}
    </div>
  );
}

export function Nivel({ n }: { n: number | null }) {
  if (n === null) return <span className="nivel n0">–</span>;
  return <span className={`nivel n${n}`} title={["No meaningful role", "Augmentation", "Partial delegation", "Full delegation"][n]}>L{n}</span>;
}
