"""Originales de Midjourney (informe/img-src/*.jpeg, fuera de git) → derivados del informe en informe/img/.
- Aperturas de capítulo: duotono positivo en el color de su parte (tinta → color oscuro de la parte, papel → tinte claro).
- Portada: duotono negativo en teal (tinta → trazo claro, papel → teal profundo), para que la ilustración se funda con el fondo.
El duotono va horneado en el JPEG: los filtros CSS inflaban el PDF. Uso: .venv/bin/python -I informe/duotono.py"""
import pathlib
import numpy as np
from PIL import Image
INF = pathlib.Path(__file__).resolve().parent
PARTES = {  # oscuro, claro
    "p1": ("#1c3a5e", "#eef2f7"), "p2": ("#0a4a45", "#eaf4f2"), "p3": ("#5e3c0d", "#f6efe4"), "marca": ("#0a4a45", "#eaf4f2")}
CAP = {"cap1": "p1", "cap2": "p1", "cap3": "p1", "cap4": "p2", "cap5": "p2", "cap6": "p3", "cap7": "p3"}
rgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def niveles(src):
    g = np.asarray(Image.open(src).convert("L"), float)
    lo, hi = np.percentile(g, 1.5), np.percentile(g, 88)  # el papel (percentil alto) queda en 1: fondo parejo
    return np.clip((g - lo) / (hi - lo), 0, 1)


def duotono(t, oscuro, claro, ancho):
    a, b = rgb(oscuro), rgb(claro)
    im = Image.fromarray((a + (b - a) * t[..., None]).astype(np.uint8))
    im.thumbnail((ancho, ancho)); return im


for cap, parte in CAP.items():
    t = niveles(INF / f"img-src/{cap}.jpeg"); o, c = PARTES[parte]
    duotono(t, o, c, 2000).save(INF / f"img/{cap}.jpg", quality=84, optimize=True, progressive=True)
    print(f"img/{cap}.jpg ({parte})")
t = niveles(INF / "img-src/introduccion.jpeg")
duotono(1 - t ** 0.9, "#062f2c", "#bfe3dd", 2400).save(INF / "img/portada.jpg", quality=86, optimize=True, progressive=True)
print("img/portada.jpg (negativo teal)")
