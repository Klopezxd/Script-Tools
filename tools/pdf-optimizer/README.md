# PDF Optimizer

Suite de optimización de documentos PDF multiplataforma de alto rendimiento. Integra un motor híbrido que combina re-muestreo inteligente de imágenes en memoria (**PyMuPDF + Pillow**), compresión estructural de flujos de objetos (**pikepdf**) y motor profundo opcional (**Ghostscript**), garantizando en todo momento la preservación íntegra de la capa de texto seleccionable y OCR.

---

## Características

* **100% Funcional sin Dependencias Externas:** El motor nativo en Python no requiere instalar Ghostscript ni binarios externos de terceros para operar al máximo rendimiento.
* **Preservación Estricta de OCR y Texto Vectorial:** Verifica automáticamente antes y después de cada compresión que la capa de texto seleccionable no sufra alteración o borrado accidental.
* **Blindaje de Firmas Digitales y Transparencias:** Detecta y sincroniza matemáticamente máscaras suaves (`/SMask`), transparencias alfa y claves de color (`/Mask`). Cero recuadros negros en firmas y cero membretes opacos tapando texto.
* **Escalado Adaptativo Inteligente (Bounding-Box DPI):** Calcula la resolución en función de los puntos físicos reales que ocupa cada elemento en la hoja, optimizando sellos y códigos QR a su escala exacta sin pixelación.
* **5 Perfiles de Optimización Calibrados:**
  * `extreme`: 72 DPI + JPEG agresivo + remuestreo sincronizado de firmas (75% - 95% de reducción sin romper texto ni sellos).
  * `screen`: 72 DPI (máximo ahorro para plataformas educativas y cuotas web estrictas).
  * `balanced`: 150 DPI (recomendado para tareas universitarias, reportes y correo electrónico).
  * `print`: 300 DPI con compresión JPEG suave (ideal para documentos oficiales o impresos).
  * `lossless`: Compresión puramente estructural (object streams) con 0% de degradación visual.
* **Protección contra Crecimiento de Archivo:** Si el documento de salida resulta ser más pesado que el original, revierte automáticamente para evitar degradaciones innecesarias.
* **Procesamiento por Lotes (Batch):** Procesa carpetas enteras de documentos con estadísticas consolidadas en tablas interactivas.

---

## Requisitos e Instalación

1. **Python 3.10+**
2. **Dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```
*(Opcional: Si Ghostscript está instalado en el sistema, se habilitará como motor alternativo mediante el flag `--engine gs`).*

---

## Guía de Uso

### 1. Menú Contextual de Windows (Clic Derecho)
Instala los accesos directos ejecutando `scripts/install_context_menu.bat` en la raíz.
Luego haz **clic derecho** sobre cualquier archivo `.pdf` y selecciona:
> **Optimizar con Script-Tools**

### 2. Arrastrar y Soltar (Drag & Drop)
Arrastra cualquier archivo `.pdf` sobre `pdf_optimizer.bat` en el Explorador de Windows para procesarlo de inmediato en modo equilibrado.

### 3. Línea de Comandos (CLI)
```bash
# Vía CLI Unificada (raíz)
python tools.py pdf documento.pdf --profile balanced

# O directamente desde este directorio
python pdf_optimizer.py documento.pdf --profile balanced
```

---

## Comparativa de Perfiles

| Perfil | DPI de Imagen | Calidad JPEG | Reducción Típica | Caso de Uso Ideal |
|---|---|---|---|---|
| `extreme` | 72 DPI | 45 (Agresiva) | 75% - 95% | Cuotas estrictas (< 2 MB), WhatsApp, tareas pesadas (mantiene 100% texto/OCR). |
| `screen` | 72 DPI | 50 (Baja) | 70% - 90% | Plataformas educativas o portales web con límites moderados (< 5 MB). |
| `balanced` | 150 DPI | 75 (Media) | 50% - 80% | Tareas universitarias, reportes, diapositivas y envío por email [Recomendado]. |
| `print` | 300 DPI | 85 (Alta) | 30% - 60% | Documentos formales para impresión física o portafolios. |
| `lossless` | Original | Sin re-muestreo | 10% - 35% | Tesis, contratos legales, PDFs ya vectoriales (0% pérdida visual). |

---

## Recetas Frecuentes

| Objetivo | Comando | Explicación Técnica |
|---|---|---|
| **Subir a Aula Virtual / Moodle** | `python tools.py pdf tarea.pdf -p screen` | 72 DPI + JPEG agresivo para superar límites de subida de portales educativos. |
| **Optimizar Documento Legal / OCR** | `python tools.py pdf contrato.pdf --strict-ocr` | Comprime imágenes y revierte si se detecta alteración en la capa OCR. |
| **Optimizar Tesis sin Tocar Gráficos** | `python tools.py pdf tesis.pdf -p lossless` | Re-empaqueta object streams y remueve metadatos redundantes con pikepdf. |
| **Carpeta de Documentos Escaneados** | `python tools.py pdf ./escaneos --batch -p balanced` | Procesa en lote mostrando barra de progreso y tabla de ahorro consolidado. |
| **Utilizar Motor Ghostscript (Alternativo)** | `python tools.py pdf plano.pdf -e gs -p print` | Delega la rasterización a Ghostscript si está instalado en el sistema. |

---

## Parámetros de CLI

| Parámetro | Opciones | Por Defecto | Descripción |
|---|---|---|---|
| `input` | Ruta a archivo o carpeta | *GUI Picker* | Documento o carpeta a procesar. Si se omite, abre diálogo nativo. |
| `-o, --output` | Ruta de archivo | `[nombre]_optimized.pdf` | Ruta de salida personalizada. |
| `-p, --profile` | `extreme`, `screen`, `balanced`, `print`, `lossless` | `balanced` | Perfil de calidad y resolución DPI. |
| `-e, --engine` | `native`, `gs` | `native` | Motor: `native` (Python puro sin dependencias) o `gs` (Ghostscript). |
| `--strict-ocr` | Flag booleano | `False` | Aborta y revierte si detecta pérdida en la capa de texto OCR. |
| `--batch` | Flag booleano | `False` | Procesa recursivamente todos los PDFs en la carpeta indicada. |

