"use client";
import Link from "next/link";
import { useMemo, useState } from "react";

// Look-up box for occupations (title or ISCO-08 code) and countries (name or ISO3).
export function Buscador({ items, placeholder }: { items: { href: string; nombre: string; codigo: string; valor: string }[]; placeholder: string }) {
  const [q, setQ] = useState("");
  const res = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (t.length < 2) return [];
    return items.filter((x) => x.nombre.toLowerCase().includes(t) || x.codigo.toLowerCase().startsWith(t)).slice(0, 8);
  }, [q, items]);
  return (
    <div>
      <input className="campo" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={placeholder} aria-label={placeholder}
        style={{ width: "100%" }} />
      {q.trim().length >= 2 && (
        <ul className="feed" style={{ marginTop: 10 }} aria-live="polite">
          {res.length === 0 && <li style={{ display: "block" }}><span className="nota">Nothing matches “{q}”. Try a shorter word or a code.</span></li>}
          {res.map((x) => (
            <li key={x.href} style={{ gridTemplateColumns: "70px minmax(0,1fr) auto", padding: "10px 0" }}>
              <span className="codigo">{x.codigo}</span><Link href={x.href}>{x.nombre}</Link><span className="valor num">{x.valor}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
