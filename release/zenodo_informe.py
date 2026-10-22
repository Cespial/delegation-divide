"""DOI propio del informe en Zenodo (registro tipo publication/report, distinto del dataset 10.5281/zenodo.23552918).
Lo corre Cristian en su Terminal, con el token exportado en esa sesión; el script nunca lo imprime ni lo escribe:
    export ZENODO_TOKEN=…            (scopes deposit:write y deposit:actions; https://zenodo.org/account/settings/applications/)
    python3 release/zenodo_informe.py reservar      crea el borrador con los metadatos y reserva el DOI
    python3 release/zenodo_informe.py subir         sube el PDF limpio (informe/out/limpio/…) al borrador; reemplaza el anterior
    python3 release/zenodo_informe.py estado        muestra el borrador tal como está en Zenodo
    python3 release/zenodo_informe.py publicar --si publica (irreversible: el DOI queda registrado en DataCite)
Con --sandbox todo va a sandbox.zenodo.org (token propio del sandbox) para probar sin acuñar nada real.
Metadatos: release/zenodo_informe.json; la descripción se arma con las cifras de informe/cifras.json (ninguna tecleada a mano).
Estado: release/zenodo_informe.estado.json (id del borrador y DOI; sin secretos). ensamblar.py y render.py leen de ahí el DOI."""
import json, os, re, sys, pathlib, urllib.request, urllib.error
from datetime import date

R = pathlib.Path(__file__).resolve().parents[1]
META, ESTADO = R / "release/zenodo_informe.json", R / "release/zenodo_informe.estado.json"
PDF = R / "informe/out/limpio/delegation-divide-report-2026.pdf"
SANDBOX = "--sandbox" in sys.argv
API = "https://sandbox.zenodo.org/api" if SANDBOX else "https://zenodo.org/api"


def token():
    t = os.environ.get("ZENODO_TOKEN", "").strip()
    if not t: sys.exit("Falta ZENODO_TOKEN en el entorno de esta Terminal (export ZENODO_TOKEN=…).")
    return t


def pedir(metodo, url, cuerpo=None, tipo="application/json"):
    datos = cuerpo if isinstance(cuerpo, (bytes, type(None))) else json.dumps(cuerpo).encode()
    req = urllib.request.Request(url if url.startswith("http") else API + url, data=datos, method=metodo,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": tipo, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            texto = r.read().decode(); return json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Zenodo respondió {e.code} a {metodo} {url}: {e.read().decode()[:800]}")


def metadatos():
    m = json.loads(META.read_text()); C = json.loads((R / "informe/cifras.json").read_text())["cifras"]
    def cifra(mm):
        if mm[1] not in C: sys.exit(f"cifra inexistente en la descripción: {mm[1]}")
        return re.sub(r"<[^>]+>", "", C[mm[1]]["txt"])
    m["description"] = re.sub(r"\{([A-Za-z0-9_.]+)\}", cifra, "".join(m.pop("description_plantilla")))
    m.setdefault("publication_date", date.today().isoformat())
    return m


def leer_estado():
    if not ESTADO.exists(): sys.exit("No hay borrador: primero «reservar».")
    e = json.loads(ESTADO.read_text())
    if e.get("sandbox", False) != SANDBOX: sys.exit("El estado guardado es de " + ("sandbox" if e.get("sandbox") else "Zenodo real") + "; usa la misma opción --sandbox.")
    return e


def guardar(d, extra=None):
    e = {"id": d["id"], "doi": d["metadata"]["prereserve_doi"]["doi"] if "prereserve_doi" in d["metadata"] else d.get("doi"),
         "estado": "publicado" if d.get("submitted") else "borrador", "html": d["links"].get("html"), "sandbox": SANDBOX, **(extra or {})}
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n"); return e


paso = next((a for a in sys.argv[1:] if not a.startswith("--")), "")
if paso == "reservar":
    if ESTADO.exists() and json.loads(ESTADO.read_text()).get("sandbox", False) == SANDBOX:
        sys.exit(f"Ya hay un borrador ({ESTADO.name}); para no duplicar DOI no se crea otro. Bórralo en Zenodo y el archivo si de verdad quieres empezar de cero.")
    m = metadatos(); m["prereserve_doi"] = True
    d = pedir("POST", "/deposit/depositions", {"metadata": m})
    e = guardar(d, {"bucket": d["links"]["bucket"]})
    print(f"DOI reservado: {e['doi']}\nborrador: {e['html']}\n→ ahora: zsh informe/construir.sh, QA, limpiadoc, y «subir».")
elif paso == "subir":
    e = leer_estado()
    if not PDF.exists(): sys.exit(f"No existe {PDF.relative_to(R)}: corre limpiadoc antes.")
    d = pedir("GET", f"/deposit/depositions/{e['id']}")
    for f in d.get("files", []):
        if f["filename"] == PDF.name: pedir("DELETE", f["links"]["self"])
    f = pedir("PUT", f"{e['bucket']}/{PDF.name}", PDF.read_bytes(), "application/octet-stream")
    pedir("PUT", f"/deposit/depositions/{e['id']}", {"metadata": {**metadatos(), "prereserve_doi": True}})  # metadatos al día con las cifras
    print(f"subido {PDF.name}: {f.get('size', 0) / 1e6:.1f} MB, checksum {f.get('checksum')}")
elif paso == "estado":
    e = leer_estado(); d = pedir("GET", f"/deposit/depositions/{e['id']}")
    print(json.dumps({"doi": e["doi"], "estado": d.get("state"), "publicado": d.get("submitted"), "titulo": d["metadata"].get("title"),
                      "archivos": [(f["filename"], f["filesize"]) for f in d.get("files", [])], "html": d["links"].get("html")}, ensure_ascii=False, indent=1))
elif paso == "publicar":
    if "--si" not in sys.argv: sys.exit("Publicar es irreversible (el DOI queda registrado). Repite con --si cuando Santiago haya leído el informe.")
    e = leer_estado(); d = pedir("GET", f"/deposit/depositions/{e['id']}")
    if not any(f["filename"] == PDF.name for f in d.get("files", [])): sys.exit("El borrador no tiene el PDF: «subir» primero.")
    d = pedir("POST", f"/deposit/depositions/{e['id']}/actions/publish")
    e = guardar(d, {"bucket": e.get("bucket")}); print(f"publicado: https://doi.org/{e['doi']}")
else:
    sys.exit(__doc__)
