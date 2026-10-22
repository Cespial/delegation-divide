import type { Metadata } from "next";
import Link from "next/link";
import { Marca } from "@/components/Marca";
import { Nav } from "@/components/Nav";
import { LAB, resumen } from "@/lib/datos";

// Product bar of the ADI under the lab header, as on a benchmark page of vals.ai: mark, name, version, the index's own nav.
export const metadata: Metadata = { title: { default: `Agent Delegability Index · ${LAB}`, template: `%s · ADI · ${LAB}` } };

const NAV_ADI = [
  ["/adi", "Overview"], ["/adi/occupations", "Occupations"], ["/adi/countries", "Countries"], ["/adi/compare", "Compare"],
  ["/adi/methodology", "Methodology"], ["/adi/report", "Report"], ["/adi/data", "Data"],
] as const;

export default function LayoutAdi({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="producto">
        <div className="envoltura">
          <Link href="/adi" className="producto-marca"><Marca decorativa /><span>Agent Delegability Index · v{resumen.version}<em> · by {LAB}</em></span></Link>
          <Nav enlaces={NAV_ADI} etiqueta="Agent Delegability Index" clase="nav nav-producto" />
        </div>
      </div>
      {children}
    </>
  );
}
