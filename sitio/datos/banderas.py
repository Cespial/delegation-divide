"""Banderas de los países del atlas para el sitio: de flag-icons (MIT, node_modules/flag-icons/flags/4x3) solo las que usa
datos/paises.json, rasterizadas con sharp a public/flags/<iso2>.webp (64 × 48, para puntos y tablas) y <iso2>@4.webp
(240 × 180, cabecera de la ficha): las SVG con escudos pesan hasta 176 KB y la dispersión carga 146. Uso (desde la raíz, después de exportar.py y `npm i`):
python3 -I sitio/datos/banderas.py"""
import json, pathlib, shutil, subprocess, sys

S = pathlib.Path(__file__).resolve().parents[1]
ORIGEN = S / "node_modules/flag-icons/flags/4x3"; DESTINO = S / "public/flags"
if not ORIGEN.exists(): sys.exit("falta node_modules/flag-icons: corra `npm i` en sitio/")
iso2 = sorted({p["iso2"] for p in json.loads((S / "datos/paises.json").read_text())})
faltan = [c for c in iso2 if not (ORIGEN / f"{c}.svg").exists()]
if faltan: sys.exit(f"sin bandera en flag-icons: {faltan}")
shutil.rmtree(DESTINO, ignore_errors=True); DESTINO.mkdir(parents=True)
shutil.copy(S / "node_modules/flag-icons/LICENSE", DESTINO / "LICENSE-flag-icons.txt")
js = """const sharp = require("sharp"); const [o, d, ...c] = process.argv.slice(1);
Promise.all(c.flatMap((x) => [[64, 48, ""], [240, 180, "@4"]].map(([w, h, s]) =>
  sharp(`${o}/${x}.svg`, { density: 300 }).resize(w, h, { fit: "fill" }).webp({ quality: 82 }).toFile(`${d}/${x}${s}.webp`))))
  .catch((e) => { console.error(e); process.exit(1); });"""
subprocess.run(["node", "-e", js, str(ORIGEN), str(DESTINO), *iso2], check=True, cwd=S)
kb = sum(f.stat().st_size for f in DESTINO.glob("*.webp") if "@" not in f.name) / 1024
kb4 = sum(f.stat().st_size for f in DESTINO.glob("*@4.webp")) / 1024
print(f"public/flags: {len(iso2)} banderas, {kb:.0f} KB a 64 px y {kb4:.0f} KB a 240 px")
