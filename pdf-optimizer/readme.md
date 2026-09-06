# 📄 PDF Optimizer

Optimizador de documentos PDF que reduce peso mediante recompreión de imágenes con **Ghostscript** y limpieza estructural con **pikepdf**, preservando la capa de texto y OCR con **PyMuPDF**.

## 🌟 Características
* **Preservación de OCR:** Mantiene intacto el texto seleccionable.
* **Perfiles de compresión:**
  * `1`: Baja compresión (300 DPI - Calidad de Impresión).
  * `2`: Media compresión (150 DPI - Recomendado para visualización en pantalla).
  * `3`: Alta compresión (72 DPI - Máximo ahorro de peso).
* **Protección de calidad:** Si el archivo comprimido no ahorra espacio, el script cancela la operación automáticamente para evitar degradación innecesaria.
* **CLI & GUI:** Funciona tanto por comandos directos como de forma interactiva con ventana de selección.

## 📋 Requisitos
* Python 3.8+
* [Ghostscript](https://www.ghostscript.com/download/gsdnld.html) instalado en Windows.
* Dependencias: `pip install -r requirements.txt`

## 💻 Uso
```bash
# Modo interactivo:
python pdf_optimizer.py

# Modo CLI directo:
python pdf_optimizer.py -i "documento.pdf" -p 2
```
