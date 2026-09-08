#!/usr/bin/env bash
# Automated Environment Setup for Script-Tools (Linux & macOS)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "  🛠️  CONFIGURACIÓN AUTOMÁTICA DE SCRIPT-TOOLS"
echo "=========================================================="

echo "[1/3] Verificando interprete de Python 3..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python 3.10+ es requerido pero no fue encontrado." >&2
    exit 1
fi

echo "[2/3] Configurando entorno virtual en .venv..."
if [ ! -d "$DIR/.venv" ]; then
    "$PYTHON_BIN" -m venv "$DIR/.venv"
fi

echo "[3/3] Instalando y actualizando dependencias..."
"$DIR/.venv/bin/python" -m pip install --upgrade pip --quiet
"$DIR/.venv/bin/python" -m pip install -e "$DIR" --quiet

echo ""
echo "=========================================================="
echo "  [OK] ¡Instalación completada con éxito!"
echo "  Puedes ejecutar la suite de cualquiera de estas formas:"
echo "    • ./tools.sh"
echo "    • python3 tools.py menu"
echo "    • tools (comando global instalado)"
echo "=========================================================="
