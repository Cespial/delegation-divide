import Link from "next/link";

export default function NoEncontrada() {
  return (
    <section className="seccion">
      <div className="envoltura" style={{ minHeight: "50vh" }}>
        <span className="rotulo">404</span>
        <h1 className="titulo" style={{ margin: "14px 0 18px" }}>No page at this address</h1>
        <p className="entrada" style={{ maxWidth: "56ch" }}>Occupations live at <code>/occupations/</code> followed by a four-digit ISCO-08 code, and countries at <code>/countries/</code> followed
          by a three-letter ISO code.</p>
        <div className="botones"><Link className="boton lleno" href="/occupations">Browse occupations</Link><Link className="boton" href="/countries">Browse countries</Link><Link className="boton" href="/">Home</Link></div>
      </div>
    </section>
  );
}
