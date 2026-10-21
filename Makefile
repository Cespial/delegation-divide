# The Delegation Divide — tareas reproducibles
# Uso: make datos | indice | paper | herramientas | test
PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: all datos indice paper herramientas test

all: datos indice paper

## Captura nocturna de datos crudos (O*NET, ILOSTAT, ESCO, comparadores, Banco Mundial, microdatos)
datos:
	zsh noche/noche.sh

## Agregación tarea -> ocupación -> país; escribe salidas/adi_isco.csv y salidas/adi_pais.csv
indice:
	$(PY) -I analisis/indice.py

## Reproduce cifras, figuras y PDF del artículo (claims.jsonl)
paper:
	sh articulo/reproducir.sh

## Copia salidas/adi_*.csv al paquete e instala adi-index y adi-mcp en modo editable
herramientas:
	sh herramientas/adi-index/sincronizar.sh
	$(PIP) install -e herramientas/adi-index -e herramientas/adi-mcp

## Tests sin red de ambos paquetes + humo del servidor MCP por stdio
test:
	$(PY) -m pytest herramientas/adi-index/tests herramientas/adi-mcp/tests -q
	PATH="$(CURDIR)/.venv/bin:$$PATH" $(PY) herramientas/adi-mcp/cliente_prueba.py
