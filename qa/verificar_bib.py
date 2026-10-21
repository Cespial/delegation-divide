#!/usr/bin/env python3
"""Re-verifica articulo/referencias.bib contra Crossref (y DataCite para DOIs de datos).

Para cada entrada con campo doi: consulta https://api.crossref.org/works/<doi> y comprueba
  - año: el `year` del .bib debe coincidir con issued, published-print, published-online o published;
  - primer autor: el apellido del primer autor del .bib debe contener (o estar contenido en) el de Crossref;
  - título: similitud (difflib) >= 0.85 entre títulos normalizados (sin LaTeX, sin HTML, solo alfanuméricos), contra el título
    de Crossref solo y contra «título: subtítulo» (Crossref separa el subtítulo en ILO, OECD y OUP);
  si Crossref no trae ningún autor con apellido (p. ej. OECD Working Papers) el autor se marca «s/a» y no cuenta como fallo.
Las entradas sin doi: @misc se listan como "gris"; las demás se buscan en Crossref por título (query.bibliographic) y se
informan como "titulo" (OK si similitud >= 0.85, si no REVISAR, sin contar como fallo: preprints y documentos de trabajo
a menudo no están en Crossref). Adaptado de ~/paper-sismo-2026-luces/qa/verificar_bib.py.
Imprime una tabla y sale con código 1 si hay algún desajuste o DOI inexistente.
Uso: .venv/bin/python qa/verificar_bib.py [ruta.bib]
"""
import difflib, html, re, sys, time, unicodedata, urllib.parse
from pathlib import Path
import requests

UA = {"User-Agent": "delegation-divide/verificar_bib (mailto:cespinal@unal.edu.co)"}
BIB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "articulo" / "referencias.bib"
UMBRAL = 0.85


def fetch(url):
    """GET con reintentos: si la red cae, espera 30 s y vuelve a intentar (hasta 20 veces)."""
    for intento in range(20):
        try:
            r = requests.get(url, headers=UA, timeout=40)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"  [red] {e}; reintento en 30 s", file=sys.stderr)
            time.sleep(30)
    raise SystemExit("sin red tras 20 intentos")


def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        typ, key, i = m.group(1).lower(), m.group(2), m.end()
        depth, j = 1, i
        while depth and j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        body, fields = text[i:j - 1], {}
        for f in re.finditer(r"(\w+)\s*=\s*\{", body):
            k, d, p = f.group(1).lower(), 1, f.end()
            while d and p < len(body):
                d += {"{": 1, "}": -1}.get(body[p], 0)
                p += 1
            fields.setdefault(k, body[f.end():p - 1].strip())
        entries.append((typ, key, fields))
    return entries


def delatex(s):
    s = s.replace("{\\o}", "o").replace("{\\O}", "O").replace("{\\ss}", "ss").replace("\\i", "i")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)          # \texttt etc.
    s = re.sub(r"\\[\'`^\"~=.]", "", s)            # acentos {\'a}
    s = re.sub(r"\\[cvu]\{?", "", s)
    return s.replace("{", "").replace("}", "").replace("$", "")


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = s.replace("ø", "o").replace("Ø", "O").replace("\u2010", "-")
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def first_surname(author_field):
    a = delatex(author_field.split(" and ")[0])
    return a.split(",")[0] if "," in a else a.split()[-1]


def years(msg):
    out = set()
    for k in ("issued", "published-print", "published-online", "published"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp[0] and dp[0][0]:
            out.add(int(dp[0][0]))
    return out


def main():
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    keys = [k for _, k, _ in entries]
    dup = {k for k in keys if keys.count(k) > 1}
    fallos = 0
    print(f"{'clave':<20} {'fuente':<8} {'año':<9} {'autor':<6} {'sim':>5}  resultado  revista/editor")
    print("-" * 110)
    for typ, key, f in entries:
        doi = f.get("doi")
        if not doi and typ == "misc":
            print(f"{key:<20} {'gris':<8} {f.get('year','-'):<9} {'-':<6} {'-':>5}  OK-gris    {f.get('url','')[:45]}")
            continue
        if not doi:
            q = delatex(f.get("title", ""))
            data = fetch("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q + " " + first_surname(f.get("author", ""))))
            mejor, sim, cont = None, 0.0, ""
            for it in (data or {}).get("message", {}).get("items", []):
                s_ = difflib.SequenceMatcher(None, norm(q), norm((it.get("title") or [""])[0])).ratio()
                if s_ > sim: mejor, sim = it, s_
            if mejor: cont = f"{mejor.get('DOI', '')} {(mejor.get('container-title') or [''])[0]}"
            print(f"{key:<20} {'titulo':<8} {f.get('year','-'):<9} {'-':<6} {sim:5.2f}  {'OK' if sim >= UMBRAL else 'REVISAR':<10} {html.unescape(cont)[:45]}")
            time.sleep(0.2); continue
        fuente, cont = "crossref", ""
        data = fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()"))
        if data:
            msg = data["message"]
            t_ref = (msg.get("title") or [""])[0]
            # Crossref separa a menudo el subtítulo (ILO, OECD, OUP): se compara contra «título: subtítulo» también
            t_alt = t_ref + ": " + (msg.get("subtitle") or [""])[0] if msg.get("subtitle") else t_ref
            fams = [x.get("family", "") for x in msg.get("author") or [] if x.get("family")]
            fam = fams[0] if fams else ""
            sin_autor = not fams   # p. ej. OECD Working Papers: Crossref no trae autores; no se cuenta como fallo
            yrs = years(msg)
            cont = (msg.get("container-title") or [msg.get("publisher", "")])[0] if msg.get("container-title") else msg.get("publisher", "")
        else:
            dc = fetch("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/()"))
            if not dc:
                print(f"{key:<20} {'?':<8} {f.get('year','-'):<9} {'-':<6} {'-':>5}  FALLO      DOI no existe en Crossref ni DataCite")
                fallos += 1
                continue
            fuente, a = "datacite", dc["data"]["attributes"]; sin_autor = False
            t_ref = a["titles"][0]["title"]; t_alt = t_ref
            fam = a["creators"][0].get("familyName") or a["creators"][0]["name"].split(",")[0]
            yrs = {int(a["publicationYear"])}
            cont = a.get("publisher") if isinstance(a.get("publisher"), str) else (a.get("publisher") or {}).get("name", "")
        y_ok = f.get("year", "").isdigit() and int(f["year"]) in yrs
        s_bib, s_ref = norm(first_surname(f.get("author", ""))), norm(fam)
        a_ok = sin_autor or (bool(s_bib and s_ref) and (s_ref in s_bib or s_bib in s_ref))
        sim = max(difflib.SequenceMatcher(None, norm(delatex(f.get("title", ""))), norm(x)).ratio() for x in (t_ref, t_alt))
        ok = y_ok and a_ok and sim >= UMBRAL and key not in dup
        fallos += not ok
        print(f"{key:<20} {fuente:<8} {f.get('year','-')+('' if y_ok else '≠'+str(sorted(yrs))):<9} "
              f"{('s/a' if sin_autor else 'ok') if a_ok else 'FALLO':<6} {sim:5.2f}  {'OK' if ok else 'FALLO':<10} {html.unescape(cont)[:45]}")
        time.sleep(0.2)
    n = len(entries)
    print("-" * 110)
    print(f"{n} entradas ({sum(1 for _,_,f in entries if f.get('doi'))} con DOI); fallos: {fallos}"
          + (f"; claves duplicadas: {sorted(dup)}" if dup else ""))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
