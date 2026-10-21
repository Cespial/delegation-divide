"""Paso 4: índices comparables (Tabla 1 del paper): Eloundou, Felten, Webb, Eisfeldt, ILO-Gmyrek, Anthropic Economic Index,
Agentic Adoption Index (fuente arXiv), GDPval y Remote Labor Index si están públicos."""
import sys, os; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comun import *
lg = log("04_comparadores"); d = DATOS / "comparadores"
copiar(AHC / "data/raw/eloundou/occ_level.csv", d / "eloundou/occ_level.csv", "Eloundou (copia AHC)", lg)
descargar("https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/full_labelset.tsv", d / "eloundou/full_labelset.tsv", "Eloundou GPTs-are-GPTs", lg)
descargar("https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occupation_level_exposure.csv", d / "eloundou/occupation_level_exposure.csv", "Eloundou", lg)
copiar(AHC / "data/raw/felten/AIOE_DataAppendix.xlsx", d / "felten/AIOE_DataAppendix.xlsx", "Felten AIOE (copia AHC)", lg) or \
    descargar("https://github.com/AIOE-Data/AIOE/raw/main/AIOE_DataAppendix.xlsx", d / "felten/AIOE_DataAppendix.xlsx", "Felten AIOE", lg)
copiar(AHC / "data/raw/webb/autoScores.csv", d / "webb/autoScores.csv", "Webb 2020 (copia AHC)", lg)
copiar(AHC / "data/raw/eisfeldt/genaiexp_scores.csv", d / "eisfeldt/genaiexp_scores.csv", "Eisfeldt et al. (copia AHC)", lg)
descargar("https://www.ilo.org/sites/default/files/2025-05/WP140_web.pdf", d / "ilo_gmyrek/WP140_web.pdf", "ILO WP140 Gmyrek 2025", lg)
# Libro de trabajo de la OIT (índice refinado): URL conocida en la nota; si cambia, queda registrado el fallo
descargar("https://www.ilo.org/sites/default/files/2025-05/GenAI_exposure_index_2025.xlsx", d / "ilo_gmyrek/GenAI_exposure_index_2025.xlsx", "ILO índice refinado 2025", lg, reintentos=2)
# Agentic Adoption Index: fuente LaTeX de arXiv (contiene tablas y, a veces, enlace al repo de datos)
descargar("https://arxiv.org/e-print/2608.20425", d / "agentic_adoption/2608.20425.tar", "arXiv 2608.20425 fuente", lg, reintentos=2)
descargar("https://arxiv.org/pdf/2608.20425", d / "agentic_adoption/2608.20425.pdf", "arXiv 2608.20425 pdf", lg, reintentos=2)
descargar("https://arxiv.org/pdf/2607.05404", d / "jagged_global/2607.05404.pdf", "arXiv Jagged Global Economy", lg, reintentos=2)
descargar("https://arxiv.org/pdf/2604.18849", d / "henseke/2604.18849.pdf", "arXiv Henseke GAISI", lg, reintentos=2)
# Anthropic Economic Index (Hugging Face): todas las versiones públicas
try:
    from huggingface_hub import snapshot_download
    ruta = snapshot_download("Anthropic/EconomicIndex", repo_type="dataset", local_dir=str(d / "anthropic_economic_index"), max_workers=4)
    n = sum(1 for _ in Path(ruta).rglob("*") if _.is_file()); registrar(Path(ruta), "Anthropic Economic Index (HF)", "https://huggingface.co/datasets/Anthropic/EconomicIndex", nota=f"{n} archivos")
    lg.info(f"Anthropic Economic Index: {n} archivos")
except Exception as e:
    lg.error(f"Anthropic Economic Index falló: {e}"); registrar(d / "anthropic_economic_index", "Anthropic Economic Index (HF)", nota=f"FALLÓ {e}", ok=False)
for repo, carpeta in [("openai/gdpval", "gdpval")]:
    try:
        from huggingface_hub import snapshot_download
        ruta = snapshot_download(repo, repo_type="dataset", local_dir=str(d / carpeta), max_workers=4)
        registrar(Path(ruta), f"{repo} (HF)", f"https://huggingface.co/datasets/{repo}"); lg.info(f"{repo} OK")
    except Exception as e:
        lg.warning(f"{repo}: {e}")
lg.info("comparadores listos")
