"""Recorta las fuentes del sitio (woff2 en sitio/app/fonts/) a los caracteres que el sitio usa: todo el texto de sitio/datos
(ocupaciones, tareas, países), el código de las páginas y Latin-1 completo. Sin hinting. Correr después de datos/exportar.py
si entran textos nuevos. Uso (desde la raíz): .venv/bin/python -I sitio/datos/fuentes.py"""
import pathlib, subprocess, sys
R = pathlib.Path(__file__).resolve().parents[2]; S = R / "sitio"
texto = set()
for f in [*(S / "datos").glob("*.json"), *(S / "datos/tareas").glob("*.json"), *(S / "app").rglob("*.tsx"), *(S / "components").glob("*.tsx"), *(S / "lib").glob("*.ts*")]:
    texto |= set(f.read_text(encoding="utf-8"))
texto |= {chr(c) for c in range(0x20, 0x7F)} | {chr(c) for c in range(0xA0, 0x100)} | set("–—‘’“”…·•→←≥≤×−κβρα²³")
cods = sorted(ord(c) for c in texto if ord(c) >= 0x20)
FUENTES = ["Barlow-Regular", "Barlow-Italic", "Barlow-Medium", "Barlow-SemiBold", "Barlow-Bold", "BarlowCondensed-SemiBold", "BarlowCondensed-Bold",
           "BarlowCondensed-ExtraBold", "JetBrainsMono-Regular", "JetBrainsMono-Medium"]
for n in FUENTES:
    subprocess.run([sys.executable, "-m", "fontTools.subset", str(R / "informe/fonts" / f"{n}.ttf"), f"--unicodes={','.join(f'U+{c:04X}' for c in cods)}",
                    "--flavor=woff2", "--layout-features=kern,liga,calt,tnum,lnum,case,ccmp,locl,mark,mkmk", "--no-hinting", "--desubroutinize",
                    "--name-IDs=0,1,2,3,4,5,6", f"--output-file={S / 'app/fonts' / f'{n}.woff2'}"], check=True)
print(f"{len(cods)} caracteres; " + ", ".join(f"{n} {(S / 'app/fonts' / f'{n}.woff2').stat().st_size // 1000} KB" for n in FUENTES))
