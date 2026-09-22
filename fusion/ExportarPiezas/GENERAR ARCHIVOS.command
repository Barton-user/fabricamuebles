#!/bin/bash
# Generado por ExportarPiezas. Doble clic para producir los archivos de maquina.
cd "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/etapa2" || { echo "No encuentro el generador en /Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/etapa2"; read -n1; exit 1; }
SALIDA="/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/ExportarPiezas/salida"
python3 exportar.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/ExportarPiezas/piezas.json" -o "$SALIDA" || { read -n1; exit 1; }
python3 listacorte.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/ExportarPiezas/piezas.json" -o "$SALIDA"
python3 hojas.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/ExportarPiezas/piezas.json" -o "$SALIDA/HOJAS_VERIFICACION.html"
echo
echo "Listo. Todo en: $SALIDA"
open "$SALIDA"
echo "Apreta una tecla para cerrar."
read -n1
