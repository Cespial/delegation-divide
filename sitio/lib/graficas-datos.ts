// Server side of the charts: builds the plotted records from the site data (lib/datos.ts reads files, so client
// components never import it; pages pass these arrays down as props).
import divideJson from "@/datos/divide.json";
import { paises, type Pais } from "./datos";
import type { Divide, Punto } from "./graficas";

export const divide = divideJson as Divide;
export const punto = (p: Pais): Punto => ({
  iso3: p.iso3, iso2: p.iso2, nombre: p.nombre, region: p.region_nombre.charAt(0).toUpperCase() + p.region_nombre.slice(1), ingreso: p.ingreso, ingreso_nombre: p.ingreso_nombre, rk: p.rk,
  l2: p.l2, lo: p.lo, hi: p.hi, l3: p.l3, s: p.s, fisica: p.b[0], uso: p.uso, pib: p.pib, inf: p.inf, residuo: p.residuo, esperado: p.esperado, emp: p.emp,
});
export const PUNTOS: Punto[] = paises.map(punto);
export const REGIONES = [...new Set(PUNTOS.map((p) => p.region))].sort();
