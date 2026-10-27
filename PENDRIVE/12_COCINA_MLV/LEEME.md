# COCINA MLV (Malvinas) — paquete de producción

GuiGui: orden **260625-20**, habitación COCINA MLV (room 117131062), **guardado 22/10 20:39 (China)**.
13 muebles, **125 piezas**. Generado el 27/10/2026 directo del `render.json`, sin pasar por Fusion:

```
cd etapa2
./generar_desde_render.sh ../referencia/GUIGUI_MCP/1022/COCINA_MLV_207960w11792672732285.render.json \
    ../PENDRIVE/12_COCINA_MLV 260625-20 MALVINAS 22/10/2026
```

Si la diseñadora cambia algo en GuiGui: bajar el render nuevo (MCP, `docs/GUIGUI.md`) y volver a correr esa línea.
Todo sale de nuevo, con los mismos códigos.

## Qué hay en esta carpeta

| Carpeta / archivo | Para qué |
|---|---|
| `lista_corte.xlsx` / `.csv` | **Sierra (AutoCUT)**. Medida de corte = terminada − canto. Columna `条码` = código |
| `etiquetas_qr_web/` | **Etiquetas**: `etiquetas_A4.pdf` (impresora común, recortar) o `etiquetas_60x39.pdf` (AIBAO). QR → página de la pieza |
| `XML3/` | **Perforadora**: un programa por pieza, nombre = código. Se escanea la etiqueta y lo carga |
| `XML3_2PASOS/` | Segundo programa de las 13 piezas que van en dos pasos (códigos que empiezan con **99**, se tipean) |
| `XML3_PRUEBA_UN_PASO/` | Esas mismas piezas en **un** solo programa, para probar si MH2026 lo acepta (ver abajo) |
| `HOJAS_VERIFICACION.html` | Dibujo de cada programa: comparar con la pantalla antes de largar |
| `HOJAS_2PASOS.html` | Ídem para las piezas en dos pasos |
| `manuales/manual_<mueble>.pdf` | Manual de armado de 2 hojas por mueble (también en la web, botón "Manual de armado") |
| `maestra.json` | Número, nombre y medidas de cada pieza (los mismos en etiqueta, web, planos y manual) |
| `piezas/` | Intermedios: `piezas.json` (terminada) → `piezas_corte.json` → `piezas_maquina.json`; `piezas_informe.txt` (qué se cambió y avisos por pieza), `ajustes_maquina.txt` (qué cara va arriba), `dos_pasos.txt` |
| `IDEE_*.pdf` | Planos de IDEE (verificados contra GuiGui el 22/10: 125/125) |

Las carpetas `etiquetas/`, `etiquetas_tspl_*`, `gap*`, `cal2*` son de las pruebas de la impresora: no usar.

## Orden de trabajo

1. **Sierra** con `lista_corte.xlsx`. Material: Blanco 18 (45 piezas, 8,7 m²), Gris 18 (43, 11,5 m²),
   PET Gris 18 (11, 3,7 m²), PET Blanco 18 (6, 1,4 m²), "NPetfrente Gris" 18 (6, 1,1 m²: toda la Alacena simple
   ajuste), Blanco 5 (14 fondos, 4,8 m²). Pegar la etiqueta al salir cada pieza.
2. **Perforadora** antes de cantear (los programas están en medida de corte). Escanear la etiqueta.
   **Medir el ancho con calibre**: si la sierra dejó 1–2 mm de más salta `202h` (ver `CONTEXTO.md` §4).
   La cara de arriba es la que dice `HOJAS_VERIFICACION.html`.
3. **Cantos** (HH-509R): la etiqueta y la web dicen de qué lado.
4. **Armado** con el manual de cada mueble.

## Lo que GuiGui trae viejo y ya está corregido en los programas

GuiGui al 22/10 sigue con los herrajes de antes; `render_piezas.py --herrajes-vigentes` los cambia por
`herrajes/medidas.json`:

- Tornillos de bisagra Ø3 × 0,5 → **Ø5 × 3** (posición de GuiGui: 6 de la cazoleta, ±24, ya está bien).
- Cazoletas Ø35 × 12 → **× 13**.
- Placa base: Ø3 a 37 y 69 del frente, acostada → **2 × Ø5 × 3 a 37 del frente, ±16** (25 bases).
- Receptor del 3 en 1 Ø5 × 11 → **× 12**. Perno de canto Ø8 × 34 → **× 33**.
- Tornillos de corredera Ø3 × 2 (48): **sacados** (no hay mecha Ø3). Las correderas se atornillan con plantilla.
- Materiales de muestra de GuiGui: 4 travesaños en 多层实木 → Gris 18; 3 fondos en 装饰板 → Blanco 5; 1 en PETFRONT → PET Gris.
  **Avisar a la diseñadora.**

## Ojo en la máquina

- **13 piezas en dos pasos** (`piezas/dos_pasos.txt`): las que tienen las Ø15 de un lado y la ranura de 6 del
  otro (el caso que falló el 19/10 con el cajón del Bandejero) y el estante del Bajo mesada doble c/cesto
  (ranuras de 6 en las dos caras: no hay otra). Paso 1 = el código de la etiqueta (Ø15 arriba + agujeros de
  canto). Paso 2 = el código 99… de `XML3_2PASOS/`: dar vuelta la pieza y tipearlo.
  **Prueba sugerida**: un cajón con `XML3_PRUEBA_UN_PASO/`. Si anda, usar esos y saltear el paso 2.
- **Ranura LED 18 × 11 por abajo** (11 pisos y techos de alacena): la hace la T11 (Ø10), con 18 de ancho
  necesita dos pasadas. Primera vez: mirar qué hace MH2026 con la primera pieza.
- **Ranura de 6**: si sale "diámetro 6" (la T187 no es Ø6, ver `PENDRIVE/9_BANDEJERO_CAJON/LEEME.txt`),
  pasar la ranura a 5 en la tabla o pedir los programas con ranura 5.
- **4 piezas de menos de 50 de ancho** (no entran en la perforadora: mínimo 50): Travesaño 564×51 del Horno
  y anafe (1956217421338), Uñero 2482×50 (1956217421420), Tapa 2264×50 del Escobero (2114155255098), Tapa
  876,5×50 de la Alacena simple ajuste (3717179022661). Perforar a mano con la hoja de verificación.
- **1 ranura de canto** (6 × 6 a lo largo, Travesaño 964×150 del Bajo mesada doble, 2114715076057): no está
  en el programa. Hacerla con tupí o router de mano.
- **9 piezas con recorte** (escotadura de la mesada o del cesto): el programa es el rectángulo; el recorte va
  a mano (caladora) o en el router. Laterales 780×580 del Horno y anafe, Bajo mesada doble, Bandejero y
  Cajonera; estante 964×580 del Bajo mesada doble; piso 400×350 de la Alacena simple ajuste.
- **Banquina del Escobero** (2114155254978): está en GuiGui sin geometría → no tiene programa ni etiqueta.
  Medirla en GuiGui y cortarla aparte.

## Web y QR

Cada etiqueta lleva un QR a `https://leiten.vercel.app/p/<código>`: datos de la pieza, plano, dónde va,
planos del módulo y manual de armado. Se actualiza con el mismo script (escribe en `curvado/public/`) y un push.
