"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const ENLACES = [
  ["/occupations", "Occupations"], ["/countries", "Countries"], ["/compare", "Compare"], ["/methodology", "Methodology"],
  ["/report", "Report"], ["/data", "Data"], ["/about", "About"],
] as const;

export function Nav() {
  const ruta = usePathname();
  return (
    <nav className="nav" aria-label="Main">
      {ENLACES.map(([href, txt]) => (
        <Link key={href} href={href} aria-current={ruta === href || ruta.startsWith(href + "/") ? "page" : undefined}>{txt}</Link>
      ))}
    </nav>
  );
}
