// Structured data for search engines and dataset indexes (Google Dataset Search reads the Dataset type).
export function JsonLd({ datos }: { datos: object }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datos).replace(/</g, "\\u003c") }} />;
}
