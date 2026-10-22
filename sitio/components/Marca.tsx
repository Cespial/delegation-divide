// ADI mark: four ascending steps (L0–L3) and the acronym, as on the report cover.
export function Marca({ tonos = ["#cfe6e3", "#9ccbc6", "#2f8f86", "#0a4a45"], texto = "#1a1918", decorativa = false }: { tonos?: string[]; texto?: string; decorativa?: boolean }) {
  const pasos: [number, number, number][] = [[0, 19, 9], [6.5, 13, 15], [13, 6, 22], [19.5, 0, 28]];
  return (
    <svg viewBox="0 0 74 28" xmlns="http://www.w3.org/2000/svg" {...(decorativa ? { "aria-hidden": true } : { role: "img", "aria-label": "ADI, Agent Delegability Index" })}>
      {pasos.map(([x, y, h], i) => <rect key={i} x={x} y={y} width={5} height={h} fill={tonos[i]} />)}
      <text x={30} y={27.4} fontFamily="var(--f-cond), 'Arial Narrow', sans-serif" fontWeight={800} fontSize={35} fill={texto}>ADI</text>
    </svg>
  );
}

// Balam Labs logotype: the name set in Barlow Condensed, no symbol yet. The ADI steps stay the product's mark.
export function MarcaLab() {
  return <span className="marca-lab">Balam<span> Labs</span></span>;
}
