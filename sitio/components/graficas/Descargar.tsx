"use client";
// PNG · SVG · CSV for the chart inside `objetivo`. The SVG is cloned with its computed styles written inline and its flag
// images embedded as data URIs, so the file stands alone; the PNG is that SVG painted at 2× with the source line under it.
import { useState } from "react";

const PROPS = ["fill", "fill-opacity", "stroke", "stroke-width", "stroke-dasharray", "stroke-linejoin", "opacity", "font-family",
  "font-size", "font-weight", "paint-order", "text-anchor", "dominant-baseline", "filter"];
const FUENTE = "Balam Labs · Agent Delegability Index v2026.1 · balamlabs.org/adi";

function guardar(blob: Blob, nombre: string) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = nombre;
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
const comoData = (url: string) => fetch(url).then((r) => r.blob()).then((b) => new Promise<string>((ok) => {
  const f = new FileReader(); f.onload = () => ok(f.result as string); f.readAsDataURL(b);
}));

async function serializar(svg: SVGSVGElement) {
  const copia = svg.cloneNode(true) as SVGSVGElement;
  const orig = svg.querySelectorAll("*"), dest = copia.querySelectorAll("*");
  orig.forEach((el, i) => {
    const cs = getComputedStyle(el), d = dest[i] as SVGElement;
    const estilo = PROPS.map((k) => `${k}:${cs.getPropertyValue(k)}`).join(";");
    const tf = (el as SVGElement).style.transform;
    d.setAttribute("style", estilo + (tf ? `;transform:${tf}` : ""));
    d.removeAttribute("class");
  });
  await Promise.all([...copia.querySelectorAll("image")].map(async (im) => {
    const h = im.getAttribute("href"); if (h && !h.startsWith("data:")) im.setAttribute("href", await comoData(h));
  }));
  copia.querySelectorAll("a").forEach((a) => a.removeAttribute("href"));
  const { width, height } = svg.viewBox.baseVal.width ? svg.viewBox.baseVal : svg.getBoundingClientRect();
  copia.setAttribute("xmlns", "http://www.w3.org/2000/svg"); copia.setAttribute("width", String(width)); copia.setAttribute("height", String(height));
  return { texto: new XMLSerializer().serializeToString(copia), width, height };
}

export function Descargar({ objetivo, nombre, csv }: { objetivo: React.RefObject<HTMLElement | null>; nombre: string; csv: () => (string | number | null)[][] }) {
  const [ocupado, setOcupado] = useState(false);
  const svg = () => objetivo.current?.querySelector<SVGSVGElement>("svg.lienzo") ?? null;
  const conSvg = (f: (s: SVGSVGElement) => Promise<void>) => async () => {
    const s = svg(); if (!s || ocupado) return; setOcupado(true);
    try { await f(s); } finally { setOcupado(false); }
  };
  const descSvg = conSvg(async (s) => { const { texto } = await serializar(s); guardar(new Blob([texto], { type: "image/svg+xml" }), `${nombre}.svg`); });
  const descPng = conSvg(async (s) => {
    const { texto, width, height } = await serializar(s);
    const img = new Image(); img.src = URL.createObjectURL(new Blob([texto], { type: "image/svg+xml" }));
    await img.decode();
    const k = 2, pie = 28, c = document.createElement("canvas"); c.width = width * k; c.height = (height + pie) * k;
    const g = c.getContext("2d")!; g.scale(k, k); g.fillStyle = "#fff"; g.fillRect(0, 0, width, height + pie); g.drawImage(img, 0, 0, width, height);
    g.fillStyle = "#686c73"; g.font = "12px Menlo, monospace"; g.fillText(FUENTE, 8, height + 18);
    URL.revokeObjectURL(img.src);
    await new Promise<void>((ok) => c.toBlob((b) => { if (b) guardar(b, `${nombre}.png`); ok(); }, "image/png"));
  });
  const descCsv = () => {
    const esc = (v: string | number | null) => (v === null ? "" : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
    guardar(new Blob([csv().map((f) => f.map(esc).join(",")).join("\n") + "\n"], { type: "text/csv" }), `${nombre}.csv`);
  };
  return (
    <div className="descargar" role="group" aria-label="Download this chart">
      <span className="rotulo">Download</span>
      <button type="button" onClick={descPng} disabled={ocupado}>PNG</button>
      <button type="button" onClick={descSvg} disabled={ocupado}>SVG</button>
      <button type="button" onClick={descCsv}>CSV</button>
    </div>
  );
}
