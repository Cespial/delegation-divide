"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

// One nav for the lab header and the ADI product bar. Only the longest matching link is marked as current,
// so /adi/report lights "Report" and not also "ADI".
export function Nav({ enlaces, etiqueta, clase = "nav" }: { enlaces: readonly (readonly [string, string])[]; etiqueta: string; clase?: string }) {
  const ruta = usePathname();
  const actual = enlaces.map(([h]) => h).filter((h) => ruta === h || ruta.startsWith(h + "/")).sort((a, b) => b.length - a.length)[0];
  return (
    <nav className={clase} aria-label={etiqueta}>
      {enlaces.map(([href, txt]) => (
        <Link key={href} href={href} aria-current={href === actual ? "page" : undefined}>{txt}</Link>
      ))}
    </nav>
  );
}
