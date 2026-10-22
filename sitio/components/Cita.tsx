import { Copiar } from "./Copiar";

export function Cita({ titulo, cita }: { titulo: string; cita: { texto: string; bibtex: string } }) {
  return (
    <div className="cita">
      <div className="cita-cab"><span className="rotulo">{titulo}</span><Copiar texto={cita.texto} rotulo="Copy text" /></div>
      <p>{cita.texto}</p>
      <div className="cita-cab"><span className="rotulo">BibTeX</span><Copiar texto={cita.bibtex} rotulo="Copy BibTeX" /></div>
      <pre>{cita.bibtex}</pre>
    </div>
  );
}
