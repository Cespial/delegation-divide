"use client";
import { useId, useState } from "react";

// Accessible tabs: panels are rendered on the server and only shown or hidden here.
export function Pestanas({ etiquetas, children }: { etiquetas: string[]; children: React.ReactNode[] }) {
  const [activa, setActiva] = useState(0);
  const id = useId();
  return (
    <div>
      <div className="pestanas" role="tablist" onKeyDown={(e) => {
        if (e.key === "ArrowRight") setActiva((activa + 1) % etiquetas.length);
        if (e.key === "ArrowLeft") setActiva((activa - 1 + etiquetas.length) % etiquetas.length);
      }}>
        {etiquetas.map((t, i) => (
          <button key={t} role="tab" id={`${id}-t${i}`} aria-controls={`${id}-p${i}`} aria-selected={activa === i} tabIndex={activa === i ? 0 : -1}
            onClick={() => setActiva(i)}>{t}</button>
        ))}
      </div>
      {children.map((panel, i) => (
        <div key={i} role="tabpanel" id={`${id}-p${i}`} aria-labelledby={`${id}-t${i}`} hidden={activa !== i}>{panel}</div>
      ))}
    </div>
  );
}
