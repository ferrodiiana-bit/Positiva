# Positiva | Entrega CRISP-DM 4–6

## Instalación

1. Descomprimir el ZIP.
2. Abrir una terminal en la carpeta `positiva_streamlit`.
3. Ejecutar `pip install -r requirements.txt`.
4. Ejecutar `python modelo.py` para generar y revisar resultados de segmentación.
5. Ejecutar `streamlit run app.py` para abrir el dashboard en el navegador.

## Metodología

- Fuente: `base_vehiculo_anio.csv`, generada en fase 3.
- Se consolida por vehículo para evitar tratar años del mismo vehículo como individuos independientes.
- Se comparan K-means y clustering jerárquico (2–4 clústeres) por silueta.
- Los perfiles son **orientativos**, no decisiones de renovación validadas.
- El simulador usa **supuestos académicos editables**; no son cotizaciones.
- No se estima costo total de propiedad completo ni huella de ciclo de vida.
- Antes de una decisión oficial, conciliar duplicados de combustible y validar kilometraje, precios, tasas y factores.
