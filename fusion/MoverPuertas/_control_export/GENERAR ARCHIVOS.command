#!/bin/bash
# Generado por ExportarPiezas. Doble clic para producir los archivos de maquina.
cd "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/etapa2" || { echo "No encuentro el generador en /Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/etapa2"; read -n1; exit 1; }
SALIDA="/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/MoverPuertas/_control_export/salida"
AVISO=""
python3 exportar.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/MoverPuertas/_control_export/piezas.json" -o "$SALIDA" || AVISO="ATENCION: exportar.py dejo piezas SIN programa de maquina (ver el detalle arriba)."
python3 listacorte.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/MoverPuertas/_control_export/piezas.json" -o "$SALIDA" || AVISO="$AVISO  Fallo la lista de corte."
python3 hojas.py "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/MoverPuertas/_control_export/piezas.json" -o "$SALIDA/HOJAS_VERIFICACION.html" || AVISO="$AVISO  Fallaron las hojas."
echo
echo "Listo. Todo en: $SALIDA"
[ -n "$AVISO" ] && { echo; echo "$AVISO"; }
open "$SALIDA"
echo "Apreta una tecla para cerrar."
read -n1
