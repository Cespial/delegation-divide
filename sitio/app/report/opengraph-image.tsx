import { readFile } from "node:fs/promises";
import path from "node:path";
import { cifra } from "@/lib/datos";
import { TAM, tarjeta } from "@/lib/og";

export const alt = "The Delegation Divide: ADI Report 2026.1, cover";
export const size = TAM;
export const contentType = "image/png";

export default async function Imagen() {
  const portada = await readFile(path.join(process.cwd(), "datos", "portada-og.jpg"), "base64");
  return tarjeta({
    rotulo: "ADI Report 2026.1", titulo: "The Delegation Divide", cifra: cifra("h1.pendiente"), unidad: "pp",
    texto: `more delegable work for each log point of GDP per capita, across ${cifra("cobertura.paises")} countries.`,
    lado: <img src={`data:image/jpeg;base64,${portada}`} width={300} height={389} style={{ border: "1px solid #dcdad6", marginTop: -8 }} />,
  });
}
