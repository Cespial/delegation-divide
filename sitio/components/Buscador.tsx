"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { bandera } from "@/lib/graficas";

export type ItemBusqueda = {
  href: string;
  nombre: string;
  codigo: string;
  valor: string;
  subtitulo?: string;
  iso2?: string;
};

export type Sugerencia = { etiqueta: string; q: string };

// Look-up box for occupations (title or ISCO-08 code) and countries (name or ISO3), with keyboard navigation and quick picks.
export function Buscador({
  items,
  placeholder,
  sugerencias,
}: {
  items: ItemBusqueda[];
  placeholder: string;
  sugerencias?: Sugerencia[];
}) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);

  const res = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (t.length < 2) return [];
    const exactos: ItemBusqueda[] = [];
    const resto: ItemBusqueda[] = [];
    for (const x of items) {
      const cod = x.codigo.toLowerCase();
      const nom = x.nombre.toLowerCase();
      if (cod === t || nom.startsWith(t)) exactos.push(x);
      else if (cod.startsWith(t) || nom.includes(t)) resto.push(x);
    }
    return [...exactos, ...resto].slice(0, 8);
  }, [q, items]);

  const tecla = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setQ("");
      setSel(0);
      return;
    }
    if (res.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSel((s) => (s + 1) % res.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSel((s) => (s - 1 + res.length) % res.length);
    } else if (e.key === "Enter" && res[sel]) {
      e.preventDefault();
      router.push(res[sel].href);
    }
  };

  return (
    <div>
      <div className="buscador-caja">
        <input
          className="campo"
          type="search"
          value={q}
          onChange={(e) => { setQ(e.target.value); setSel(0); }}
          onKeyDown={tecla}
          placeholder={placeholder}
          aria-label={placeholder}
          style={{ width: "100%" }}
        />
        {q && (
          <button type="button" className="limpiar" onClick={() => { setQ(""); setSel(0); }} aria-label="Clear search">
            Clear
          </button>
        )}
      </div>
      {q.trim().length < 2 && sugerencias && sugerencias.length > 0 && (
        <div className="chips" aria-label="Try a search">
          <span className="rotulo">Try:</span>
          {sugerencias.map((s) => (
            <button key={s.etiqueta} type="button" className="chip" onClick={() => { setQ(s.q); setSel(0); }}>
              {s.etiqueta}
            </button>
          ))}
        </div>
      )}
      {q.trim().length >= 2 && (
        <ul className="feed buscador-lista" style={{ marginTop: 10 }} aria-live="polite">
          {res.length === 0 && (
            <li style={{ display: "block" }}>
              <span className="nota">Nothing matches “{q}”. Try a shorter word, an ISCO-08 code (e.g. 2512) or an ISO3 code (e.g. COL).</span>
            </li>
          )}
          {res.map((x, i) => (
            <li
              key={x.href}
              className={i === sel ? "activa" : undefined}
              onPointerEnter={() => setSel(i)}
              style={{ gridTemplateColumns: "82px minmax(0,1fr) auto", padding: "10px 8px" }}
            >
              <span className="codigo" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                {x.iso2 && <img src={bandera(x.iso2)} alt="" width={20} height={15} style={{ borderRadius: 2, boxShadow: "0 0 0 1px var(--filete)" }} />}
                {x.codigo}
              </span>
              <div>
                <Link href={x.href}>{x.nombre}</Link>
                {x.subtitulo && <small className="buscador-sub">{x.subtitulo}</small>}
              </div>
              <span className="valor num">{x.valor}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
