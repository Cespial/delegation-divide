"use client";
import { useState } from "react";

export function Copiar({ texto, rotulo = "Copy" }: { texto: string; rotulo?: string }) {
  const [hecho, setHecho] = useState(false);
  return (
    <button type="button" className="copiar" onClick={async () => {
      try { await navigator.clipboard.writeText(texto); setHecho(true); setTimeout(() => setHecho(false), 1600); } catch { /* clipboard blocked: text stays selectable */ }
    }} aria-live="polite">{hecho ? "Copied" : rotulo}</button>
  );
}
