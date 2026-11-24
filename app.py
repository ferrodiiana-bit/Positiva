
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Positiva | Flota Inteligente",
    page_icon="🚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

AZUL = "#003145"
TURQUESA = "#FF7500"
VERDE = "#627887"
NARANJA = "#FF9500"
FONDO = "#EDEFF2"
COLORES = [TURQUESA, AZUL, VERDE]

st.markdown("""
<style>
.stApp {background-color:#EDEFF2;}
.block-container {
    padding-top:1.5rem;
    max-width:1450px;
}
h1,h2,h3 {color:#003145;}
[data-testid="stMetric"] {
    background:white;
    padding:18px;
    border-radius:14px;
    border:1px solid #DFEAF0;
}
[data-testid="stMetricValue"] {
    color:#003145;
}
[data-testid="stSidebar"] {
    background:#FFFFFF;
}
.hero {
    background:#FF7500;
    color:white;
    padding:28px;
    border-radius:18px;
    margin-bottom:24px;
}
.hero h1 {color:white;margin:0;}
.hero p {color:#E0F4F8;}
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).resolve().parent

@st.cache_data
def cargar():
    df = pd.read_csv(BASE / "segmentos_positiva.csv")
    comparacion = pd.read_csv(
        BASE / "comparacion_modelos.csv"
    )
    df.columns = df.columns.str.strip()
    comparacion.columns = comparacion.columns.str.strip()
    return df, comparacion

try:
    df, comparacion = cargar()
except Exception as e:
    st.error(f"No se pudieron cargar los archivos: {e}")
    st.stop()

columnas = [
    "CODIGO_VEHICULO",
    "CLUSTER",
    "COSTO_POR_KM_REAL",
    "HUELLA_KGCO2E_POR_KM",
    "KM_ANUALES_EST"
]

faltantes = [c for c in columnas if c not in df.columns]
if faltantes:
    st.error(f"Faltan columnas: {faltantes}")
    st.stop()

for c in columnas[1:]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

if df[columnas].isna().any().any():
    st.error("Hay valores faltantes en columnas esenciales.")
    st.stop()

# Candidatos: clústeres 0 y 2, según evaluación.
df["CANDIDATO"] = df["CLUSTER"].isin([0, 2])
NOMBRES_CLUSTER = {
    0: "Presión financiera",
    1: "Eficiencia relativa",
    2: "Presión ambiental"
}
df["NOMBRE_CLUSTER"] = df["CLUSTER"].map(NOMBRES_CLUSTER)
candidatos = df[df["CANDIDATO"]].copy()


logo = BASE / "logo_positiva.png"

if logo.exists():
    st.sidebar.image(str(logo), width=180)
else:
    st.sidebar.markdown("## POSITIVA")

st.sidebar.caption("Analítica estratégica de flota")
pagina = st.sidebar.radio(
    "Recorrido del pitch",
    [
        "1. Resumen ejecutivo",
        "2. Segmentación inteligente",
        "3. Vehículos prioritarios",
        "4. Simulador de decisiones",
        "5. Propuesta ejecutiva"
    ]
)
st.sidebar.divider()
st.sidebar.caption(
    "CRISP-DM | Modelado, evaluación y despliegue"
)
st.sidebar.caption(
    "Prototipo académico. No constituye "
    "una decisión de inversión aprobada."
)

st.markdown("""
<div class="hero">
<p>POSITIVA · INTELIGENCIA DE NEGOCIO</p>
<h1>Decisiones inteligentes para una flota sostenible</h1>
<p>Optimización financiera, operativa y ambiental
mediante analítica de datos.</p>
</div>
""", unsafe_allow_html=True)

def grafico(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(color="#163B54"),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15,r=15,t=50,b=15)
    )
    st.plotly_chart(fig, use_container_width=True)

def dinero(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")

def formato_numero(valor, decimales=0):
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def tabla_formateada(tabla, formatos):
    """Conserva datos numéricos y aplica formatos visuales por columna."""
    return st.dataframe(tabla.style.format(formatos), use_container_width=True)

def indicador_fila(datos):
    a,b,c,d = st.columns(4)
    a.metric("Vehículos",len(datos))
    b.metric(
        "Costo mediano / km",
        dinero(datos["COSTO_POR_KM_REAL"].median())
    )
    c.metric(
        "Huella mediana kgCO₂e/km",
        f'{datos["HUELLA_KGCO2E_POR_KM"].median():.3f}'
    )
    d.metric(
        "Candidatos a revisión",
        int(datos["CANDIDATO"].sum())
    )

if pagina == "1. Resumen ejecutivo":
    with st.expander("Información del proyecto y hallazgos"):
        st.markdown('**Alcance del análisis.** Se estudiaron **16 vehículos** de la base disponible; los resultados describen esta muestra y no deben extrapolarse automáticamente a toda la flota de Positiva.\n\n**Hallazgo principal.** Se identificaron **tres grupos de comportamiento** y **cinco vehículos (31,25 %)** para revisión prioritaria. El objetivo es focalizar la evaluación, no ordenar reemplazos automáticos.\n\n**Indicadores de referencia.** El costo por kilómetro y las emisiones por kilómetro permiten visualizar diferencias económicas y ambientales. Son indicadores descriptivos: deben complementarse con información técnica y contractual.\n\n**Lectura de las gráficas.** Cada punto representa un registro de vehículo; si dos comparten coordenadas, las burbujas pueden superponerse. Los conteos por grupo permiten comprobar la totalidad de registros.')
    st.header("El desafío de negocio")
    st.write(
        "¿Cómo priorizar decisiones de mantenimiento, "
        "renovación y sostenibilidad de la flota "
        "ejecutiva utilizando evidencia cuantitativa?"
    )
    indicador_fila(df)
    st.subheader("Radiografía de la flota")
    a,b = st.columns(2)
    with a:
        conteos = (
            df.groupby("CLUSTER")
            .size()
            .reset_index(name="Vehículos")
        )
        conteos["NOMBRE_CLUSTER"] = conteos["CLUSTER"].map(NOMBRES_CLUSTER)
        fig = px.bar(
            conteos,
            x="NOMBRE_CLUSTER",
            y="Vehículos",
            color="NOMBRE_CLUSTER",
            category_orders={"NOMBRE_CLUSTER": list(NOMBRES_CLUSTER.values())},
            color_discrete_map={
                "Presión financiera": "#FF7500",
                "Eficiencia relativa": "#003145",
                "Presión ambiental": "#627887"
            },
            text="Vehículos",
            title="Distribución de los 16 vehículos",
            labels={"NOMBRE_CLUSTER": "Segmento"}
        )
        grafico(fig)
    with b:
        datos_grafica = df.copy()
        datos_grafica["CLUSTER_VISUAL"] = datos_grafica["NOMBRE_CLUSTER"]
        fig = px.scatter(
            datos_grafica,
            x="COSTO_POR_KM_REAL",
            y="HUELLA_KGCO2E_POR_KM",
            color="CLUSTER_VISUAL",
            category_orders={"CLUSTER_VISUAL": list(NOMBRES_CLUSTER.values())},
            color_discrete_map={
                "Presión financiera": "#FF7500",
                "Eficiencia relativa": "#003145",
                "Presión ambiental": "#627887"
            },
            hover_name="CODIGO_VEHICULO",
            hover_data={"KM_ANUALES_EST": ":.1f", "CLUSTER_VISUAL": True},
            title="Costo vs. impacto ambiental",
            labels={
                "COSTO_POR_KM_REAL": "COP por km",
                "HUELLA_KGCO2E_POR_KM": "kgCO₂e por km",
                "CLUSTER_VISUAL": "Segmento",
                "KM_ANUALES_EST": "Km anuales"
            }
        )
        fig.update_traces(marker=dict(size=15, opacity=0.82,
                                      line=dict(width=1, color="white")))
        grafico(fig)
        st.caption("Cada punto corresponde a un vehículo. Si dos vehículos "
                   "tienen costo y huella iguales, sus puntos pueden superponerse; "
                   "pase el cursor para consultar el código.")
        with st.expander("Verificar puntos por clúster"):
            conteo = datos_grafica.groupby("CLUSTER_VISUAL").size()
            st.write(conteo.rename("Vehículos"))
            st.caption(f"Registros incluidos: {len(datos_grafica)}")
    st.info(
        "El modelo identifica patrones de comportamiento; "
        "no determina automáticamente qué vehículo reemplazar."
    )

elif pagina == "2. Segmentación inteligente":
    with st.expander("Información del proyecto y hallazgos"):
        st.markdown('**Cómo se construyó la segmentación.** Se utilizaron cuatro variables: costo real por kilómetro, porcentaje de mantenimiento y repuestos, huella de carbono por kilómetro y kilometraje anual estimado. Se aplicaron transformaciones y escalado robusto antes del agrupamiento.\n\n**Alternativas evaluadas.** Se compararon **K-means** y agrupamiento **jerárquico** con dos, tres y cuatro grupos. La configuración seleccionada fue **K-means con tres grupos**, con una silueta aproximada de **0,4513**, la mayor entre las opciones comparadas.\n\n**Qué significa la silueta.** Evalúa cohesión y separación entre grupos; **no** representa precisión predictiva ni probabilidad de falla.\n\n**Prueba de estabilidad.** En la validación dejando fuera un vehículo por vez, el ARI promedio fue **0,9394**; hubo casos de menor coincidencia, por lo que el resultado no garantiza estabilidad absoluta ante datos nuevos.\n\n**Precaución.** Los números 0, 1 y 2 identifican grupos matemáticos; no equivalen por sí mismos a niveles de riesgo.')
    st.header("Del dato al conocimiento")
    st.write(
        "Se compararon técnicas de clustering no supervisado "
        "utilizando variables financieras, operativas y ambientales."
    )
    a,b,c = st.columns(3)
    a.metric("Técnica seleccionada","K-means")
    b.metric("Número de clústeres",3)
    c.metric("Silueta", "0.451")
    st.subheader("Comparación de modelos")
    comparacion_vista = comparacion.rename(columns={
        "Algoritmo": "Algoritmo", "K": "Número de grupos",
        "Silueta": "Índice de silueta (sin unidad)",
        "Grupo_mínimo": "Vehículos en el grupo menor"
    })
    st.dataframe(comparacion_vista.style.format({
        "Índice de silueta (sin unidad)": lambda v: formato_numero(v, 4)
    }), use_container_width=True, hide_index=True)
    st.subheader("Perfiles de los segmentos")
    perfiles = df.groupby("CLUSTER").agg(
        Vehiculos=("CODIGO_VEHICULO","count"),
        Costo_mediano=("COSTO_POR_KM_REAL","median"),
        Huella_mediana=("HUELLA_KGCO2E_POR_KM","median"),
        Km_anuales=("KM_ANUALES_EST","median")
    ).round(3)
    perfiles_vista = perfiles.reset_index().rename(columns={
        "CLUSTER": "Segmento", "Vehiculos": "Vehículos (n.º)",
        "Costo_mediano": "Costo mediano (COP/km)",
        "Huella_mediana": "Emisiones medianas (kgCO₂e/km)",
        "Km_anuales": "Recorrido mediano (km/año)"
    })
    perfiles_vista["Segmento"] = perfiles_vista["Segmento"].map(NOMBRES_CLUSTER)
    st.dataframe(perfiles_vista.style.format({
        "Costo mediano (COP/km)": lambda v: "$" + formato_numero(v, 2),
        "Emisiones medianas (kgCO₂e/km)": lambda v: formato_numero(v, 3),
        "Recorrido mediano (km/año)": lambda v: formato_numero(v, 1)
    }), use_container_width=True, hide_index=True)
    st.caption("COP = pesos colombianos; kgCO₂e = kilogramos de dióxido de carbono equivalente. Las cifras representan medianas por grupo.")
    st.caption(
        "Los nombres de los segmentos describen las "
        "características predominantes de cada grupo identificado "
        "por K-means. No representan niveles de riesgo predefinidos."
    )

elif pagina == "3. Vehículos prioritarios":
    with st.expander("Información del proyecto y hallazgos"):
        st.markdown(
            "**Criterio de focalización.** Los segmentos "
            "**Presión financiera** y **Presión ambiental** "
            "reúnen **cinco de los 16 vehículos (31,25 %)** "
            "seleccionados para revisión prioritaria. "
            "Esta selección orienta el análisis y no implica "
            "una decisión automática de reemplazo."
        )
    st.header("¿Dónde debemos poner la atención?")
    st.metric(
        "Vehículos candidatos a revisión",
        f"{len(candidatos)} de {len(df)}"
    )
    st.write(
        "Se priorizan los segmentos **Presión financiera** y "
        "**Presión ambiental** por su comportamiento relativo "
        "en costos y emisiones. "
        "La selección requiere validación técnica."
    )
    candidatos_vista = candidatos[[
        "CODIGO_VEHICULO", "NOMBRE_CLUSTER", "COSTO_POR_KM_REAL",
        "HUELLA_KGCO2E_POR_KM", "KM_ANUALES_EST"
    ]].rename(columns={
        "CODIGO_VEHICULO": "Vehículo", "NOMBRE_CLUSTER": "Segmento",
        "COSTO_POR_KM_REAL": "Costo (COP/km)",
        "HUELLA_KGCO2E_POR_KM": "Emisiones (kgCO₂e/km)",
        "KM_ANUALES_EST": "Recorrido (km/año)"
    })
    st.dataframe(candidatos_vista.style.format({
        "Costo (COP/km)": lambda v: "$" + formato_numero(v, 2),
        "Emisiones (kgCO₂e/km)": lambda v: formato_numero(v, 3),
        "Recorrido (km/año)": lambda v: formato_numero(v, 1)
    }), use_container_width=True, hide_index=True)
    fig = px.scatter(
        df,
        x="COSTO_POR_KM_REAL",
        y="HUELLA_KGCO2E_POR_KM",
        color=df["CANDIDATO"].map({
            True:"Revisión prioritaria",
            False:"Seguimiento"
        }),
        hover_name="CODIGO_VEHICULO",
        hover_data={"NOMBRE_CLUSTER": True},
        labels={
            "COSTO_POR_KM_REAL": "Costo (COP/km)",
            "HUELLA_KGCO2E_POR_KM": "Emisiones (kgCO₂e/km)",
            "KM_ANUALES_EST": "Recorrido (km/año)",
            "NOMBRE_CLUSTER": "Segmento",
            "color": "Prioridad"
        },
        size="KM_ANUALES_EST",
        color_discrete_map={
            "Revisión prioritaria":NARANJA,
            "Seguimiento":AZUL
        },
        title="Mapa de oportunidades de intervención"
    )
    grafico(fig)

elif pagina == "4. Simulador de decisiones":
    st.header("Simulador de decisiones | Compare tres alternativas")
    st.write("Explore qué podría pasar si conserva un vehículo, compra uno eléctrico o lo alquila. Todos los valores son editables y los resultados se actualizan automáticamente.")
    st.info("**Guía rápida:** 1. Seleccione un vehículo. 2. Elija un escenario de ejemplo o configure sus propios valores. 3. Revise los costos y emisiones. 4. Cambie un dato y observe cómo se modifica la comparación.")
    st.warning("Los precios y las emisiones de las alternativas son **supuestos de demostración**, no cotizaciones oficiales ni estimaciones certificadas. No se recomienda tomar decisiones de compra sin validación.")

    vehiculo = st.selectbox("1. ¿Qué vehículo desea analizar?", candidatos["CODIGO_VEHICULO"].tolist(),
                            help="Los vehículos de esta lista fueron identificados para revisión técnica; no necesariamente requieren reemplazo.")
    v = candidatos.loc[candidatos["CODIGO_VEHICULO"] == vehiculo].iloc[0]
    km = float(v["KM_ANUALES_EST"])
    costo_km = float(v["COSTO_POR_KM_REAL"])
    huella_km = float(v["HUELLA_KGCO2E_POR_KM"])
    segmento = v["NOMBRE_CLUSTER"]
    st.markdown(f"**Segmento del vehículo:** {segmento}")
    def pesos(valor):
        return "$" + f"{valor:,.0f}".replace(",", ".") + " COP"

    def numero(valor, decimales=2):
        return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    st.caption(f"**Datos del vehículo:** {numero(km, 0)} km/año · {pesos(costo_km)}/km · {numero(huella_km, 3)} kgCO₂e/km. Estos valores provienen de la base del proyecto.")
    st.subheader("2. Elija un punto de partida")
    escenario = st.selectbox("Escenario de demostración", [
        "Referencia: supuestos iniciales", "Ejemplo: alquiler más económico", "Personalizado (conservar valores editados)"
    ], help="Los escenarios precargan valores ilustrativos. Puede modificarlos después.")
    presets = {
        "Referencia: supuestos iniciales": dict(electrico=410., compra=120000000., canon=3500000., variable=260.,
                                                he=0.0462, ha=0.0462, anos=5, residual=35, tasa=10),
        "Ejemplo: alquiler más económico": dict(electrico=410., compra=120000000., canon=3000000., variable=260.,
                                                he=0.0462, ha=0.0462, anos=5, residual=35, tasa=10)
    }
    if "sim_escenario_previo" not in st.session_state:
        st.session_state.sim_escenario_previo = None
    if escenario != st.session_state.sim_escenario_previo and escenario in presets:
        for clave, valor in presets[escenario].items():
            st.session_state["sim_" + clave] = valor
    st.session_state.sim_escenario_previo = escenario
    if "sim_electrico" not in st.session_state:
        for clave, valor in presets["Referencia: supuestos iniciales"].items():
            st.session_state["sim_" + clave] = valor

    st.subheader("3. Ajuste los valores de la comparación")
    st.caption("Los campos monetarios están expresados en **$ COP** y los ambientales en **kgCO₂e/km**. Consulte **ⓘ** para ver ejemplos. Streamlit solicita ingresar los números sin símbolos ni separadores; debajo se muestra su equivalencia con formato colombiano.")
    a, b, c = st.columns(3)
    with a:
        costo_electrico = st.number_input("⚡ Costo por kilómetro del eléctrico ($ COP/km)",
            min_value=0., step=50., key="sim_electrico", format="%.0f",
            help="Costo estimado de energía y operación por cada kilómetro del eléctrico. No incluye su precio de compra.")
        costo_adquisicion = st.number_input("🚗 Precio de compra del eléctrico ($ COP)",
            min_value=0., step=5000000., key="sim_compra", format="%.0f",
            help="Precio de adquisición pagado al inicio de la comparación. Ejemplo: 120000000 equivale a $120.000.000 COP.")
    with b:
        canon_alquiler = st.number_input("📅 Pago mensual del alquiler ($ COP/mes)",
            min_value=0., step=250000., key="sim_canon", format="%.0f",
            help="Cuota mensual estimada por usar un vehículo alquilado. Compruebe qué servicios incluye el contrato.")
        costo_alquiler_km = st.number_input("⚡ Costo energético del eléctrico alquilado ($ COP/km)",
            min_value=0., step=10., key="sim_variable", format="%.0f",
            help="Costo de energía por kilómetro recorrido. Estimado con un consumo de 0.21 kWh/km y una tarifa de $1.220,33 COP/kWh de Enel Colombia. No incluye penalizaciones por kilometraje excedente.")
    with c:
        huella_electrica = st.number_input("🌱 Emisiones del eléctrico (kgCO₂e/km)",
            min_value=0., step=0.0001, key="sim_he", format="%.4f",
            help="Emisiones indirectas estimadas con un consumo de 0.21 kWh/km (Weiss et al., 2024) y un factor de emisión de 0.220 kgCO₂e/kWh (UPME, Resolución 000085 de 2026). No incluye fabricación ni ciclo de vida.")
        huella_alquiler = st.number_input("🌍 Emisiones del eléctrico alquilado (kgCO₂e/km)",
            min_value=0., step=0.0001, key="sim_ha", format="%.4f",
            help="Emisiones indirectas de un vehículo 100% eléctrico alquilado. Se utiliza el mismo factor de emisión y consumo energético que para el eléctrico comprado.")

    st.markdown("**Equivalencia de los valores ingresados**")
    r1, r2, r3 = st.columns(3)
    r1.caption(f"⚡ Operación eléctrica: **{pesos(costo_electrico)}/km**  ·  🚗 Compra: **{pesos(costo_adquisicion)}**")
    r2.caption(f"🗓️ Alquiler: **{pesos(canon_alquiler)}/mes** · ⚡ Energía: **{pesos(costo_alquiler_km)}/km**")
    r3.caption(f"🌱 Eléctrico: **{numero(huella_electrica, 4)} kgCO₂e/km** · 🌍 Alquiler: **{numero(huella_alquiler, 4)} kgCO₂e/km**")
    with st.expander("📚 Fundamentación científica y comercial de los valores de referencia"):
        st.markdown("""
        ### Referentes económicos y ambientales

        **Compra de vehículo eléctrico**

        - Costo operativo: $410 COP/km.
        - Precio de adquisición: $120.000.000 COP.
        - Emisiones indirectas: 0,0462 kgCO₂e/km.

        **Alquiler de vehículo eléctrico**

        - Canon mensual estimado: $3.500.000 COP.
        - Costo energético: $260 COP/km.
        - Emisiones indirectas: 0,0462 kgCO₂e/km.

        ### Fundamentación de los cálculos

        - Consumo energético: 0,21 kWh/km.
        - Tarifa eléctrica: $1.220,33 COP/kWh.
        - Costo energético estimado: $256,27 COP/km.
        - Mantenimiento programado estimado: $151,61 COP/km.
        - Factor de emisión: 0,220 kgCO₂e/kWh.
        - Emisiones indirectas: 0,21 × 0,220 = 0,0462 kgCO₂e/km.

        ### Referencias científicas

        - [Weiss et al. (2024). Energy Consumption of Electric Vehicles in Europe. Sustainability, 16(17), 7529.](https://doi.org/10.3390/su16177529)

        - [Burnham et al. (2021). Comprehensive Total Cost of Ownership Quantification for Vehicles with Different Size Classes and Powertrains. Argonne National Laboratory.](https://doi.org/10.2172/1780970)

        - [Cuéllar-Álvarez et al. (2024). Emissions and ownership-cost of conventional and electric passenger vehicles in Bogotá, Colombia.](https://doi.org/10.1016/j.trd.2024.104105)

        ### Referencias oficiales y comerciales

        - [UPME (2026). Resolución 000085 de 2026.](https://gestornormativo.creg.gov.co/gestor/entorno/docs/resolucion_upme_0085_2026.htm)

        - [Enel Colombia. Tarifas de energía eléctrica.](https://www.enel.com.co/)

        - [Kia Colombia. Kia EV3.](https://kia.com.co/nuestros-vehiculos/ev3)

        - [Renting Colombia. Referencias comerciales de alquiler.](https://www.rentingcolombia.com/)

        ### Consideraciones metodológicas

        Los valores corresponden a estimaciones de referencia.
        El canon mensual requiere cotización empresarial.
        El costo energético no incluye penalizaciones por kilometraje excedente.
        El mantenimiento utiliza una referencia internacional y una tasa de cambio supuesta de $4.000 COP/USD.
        Las emisiones corresponden a la operación del vehículo y no incluyen su fabricación ni el ciclo de vida completo.
        La tasa de descuento y el valor residual son supuestos financieros pendientes de validación por Positiva.
        """)
    vida_util = st.slider("¿Durante cuántos años quiere comparar las opciones?", 1, 10, key="sim_anos",
        help="Es el período de análisis, no la vida útil obligatoria del vehículo. Ejemplo: 5 años significa comparar cinco años de costos y emisiones.")
    residual = st.slider("¿Qué porcentaje del precio del eléctrico espera recuperar al venderlo al final?", 0, 80,
        key="sim_residual", format="%d %%",
        help="Es el valor estimado de reventa. Si compra por $100 millones y espera recuperar 35 %, el valor final sería $35 millones.")
    descuento = st.slider("¿Qué porcentaje anual usar para valorar los pagos futuros en dinero de hoy?", 0, 25,
        key="sim_tasa", format="%d %%",
        help="También llamado tasa de descuento: permite comparar dinero pagado hoy con pagos futuros. Una tasa mayor reduce el peso de los pagos futuros. Es un supuesto financiero que Positiva debe validar.")

    st.caption("**Valores actualmente configurados:** compra " + pesos(costo_adquisicion) +
               " · alquiler mensual " + pesos(canon_alquiler) +
               " · valor estimado de reventa " + pesos(costo_adquisicion * residual / 100) +
               f" · plazo {vida_util} años · tasa anual {descuento} %.")

    anual_actual = km * costo_km
    anual_electrico = km * costo_electrico
    anual_alquiler = 12 * canon_alquiler + km * costo_alquiler_km
    tasa = descuento / 100
    def vpn(anual, inicial=0, rescate=0):
        total = inicial
        for t in range(1, vida_util + 1):
            total += anual / (1 + tasa) ** t
        return total - rescate / (1 + tasa) ** vida_util

    resultados = pd.DataFrame({
        "Alternativa": ["Mantener actual", "Comprar eléctrico", "Alquilar"],
        "Costo estimado en dinero de hoy (COP)": [vpn(anual_actual), vpn(anual_electrico, costo_adquisicion,
            costo_adquisicion * residual / 100), vpn(anual_alquiler)],
        "Emisiones operativas estimadas (tCO₂e)": [km * huella_km * vida_util / 1000,
            km * huella_electrica * vida_util / 1000, km * huella_alquiler * vida_util / 1000]
    })
    costo_col = "Costo estimado en dinero de hoy (COP)"
    emision_col = "Emisiones operativas estimadas (tCO₂e)"
    menor_costo = resultados.loc[resultados[costo_col].idxmin()]
    menos_emisiones = resultados.loc[resultados[emision_col].idxmin()]
    base_actual = resultados.loc[resultados["Alternativa"] == "Mantener actual", costo_col].iloc[0]
    diferencia = base_actual - menor_costo[costo_col]

    st.subheader("4. Resultados: ¿qué alternativa conviene bajo estos supuestos?")
    x, y, z = st.columns(3)
    x.metric("Alternativa con menor costo", menor_costo["Alternativa"])
    y.metric("Diferencia frente a mantener actual", pesos(abs(diferencia)),
             help="Si la opción de menor costo es mantener actual, la diferencia es cero.")
    minimo_emisiones = resultados[emision_col].min()
    mejores_ambientales = resultados.loc[
        resultados[emision_col] == minimo_emisiones,
        "Alternativa"
    ].tolist()

    if len(mejores_ambientales) == 3:
        texto_ambiental = "Empate entre las tres"
    elif set(mejores_ambientales) == {"Comprar eléctrico", "Alquilar"}:
        texto_ambiental = "Comprar o alquilar"
    else:
        texto_ambiental = " / ".join(mejores_ambientales)

    z.metric("Alternativa con menos emisiones", texto_ambiental,
        help="Si varias alternativas tienen las mismas emisiones mínimas, se muestran todas.")
    if menor_costo["Alternativa"] != "Mantener actual":
        st.info(f"En este escenario, **{menor_costo['Alternativa'].lower()}** cuesta aproximadamente **{pesos(diferencia)} menos** que mantener el vehículo actual, en dinero de hoy. Es un resultado ilustrativo, no un ahorro garantizado.")
    else:
        st.info("Con estos valores, mantener el vehículo actual tiene el menor costo modelado. Modifique el alquiler o la compra para explorar otras situaciones.")

    a, b = st.columns(2)
    with a:
        fig = px.bar(resultados, x="Alternativa", y=costo_col, color="Alternativa",
                     color_discrete_sequence=COLORES, title="Costo total comparable (valor de hoy)",
                     text=costo_col)
        fig.update_traces(texttemplate="$%{y:,.0f}", textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis_tickprefix="$")
        grafico(fig)
    with b:
        fig = px.bar(resultados, x="Alternativa", y=emision_col, color="Alternativa",
                     color_discrete_sequence=COLORES, title="Emisiones operativas durante el período",
                     text=emision_col)
        fig.update_traces(texttemplate="%{y:.2f} t", textposition="outside", cliponaxis=False)
        grafico(fig)
    tabla = resultados.copy()
    tabla[costo_col] = tabla[costo_col].map(pesos)
    tabla[emision_col] = tabla[emision_col].map(lambda v: numero(v, 2) + " tCO₂e")
    st.dataframe(tabla, hide_index=True, use_container_width=True)
    st.caption("**Cómo leer los resultados:** una barra más baja significa menor costo o menos emisiones, según el gráfico. 'Dinero de hoy' significa que los pagos futuros se ajustan para poder compararlos con una compra inmediata. 1 tCO₂e equivale a 1.000 kgCO₂e.")
    with st.expander("Alcance y límites del cálculo"):
        st.write("El costo incluye operación anual constante, compra inicial y reventa estimada del eléctrico, o cuotas de alquiler. No considera inflación, venta del vehículo actual, cargadores, impuestos, seguros diferenciales ni costos de transición. Las emisiones representan operación, no ciclo de vida completo. El costo histórico del vehículo actual se usa como aproximación del futuro. No es una recomendación automática de inversión.")
    st.download_button("Descargar comparación (CSV)", resultados.to_csv(index=False, sep=";").encode("utf-8-sig"),
                       file_name="simulacion_positiva.csv", mime="text/csv")

elif pagina == "5. Propuesta ejecutiva":
    with st.expander("Información del proyecto y hallazgos"):
        st.markdown('**De hallazgo a decisión.** El proyecto entrega una metodología para identificar unidades que requieren mayor análisis y comparar alternativas mediante supuestos editables. No constituye una aprobación de inversión.\n\n**Ruta sugerida.** **1. Diagnosticar:** revisar los cinco casos priorizados. **2. Validar:** reunir cotizaciones y costos reales de mantenimiento, compra, alquiler y operación. **3. Pilotear:** probar una alternativa con seguimiento. **4. Escalar:** ampliar solo si la evidencia lo respalda.\n\n**Indicadores de seguimiento.** Costo por kilómetro (COP/km), emisiones por kilómetro (kgCO₂e/km), gasto operativo, kilometraje y avance de intervenciones.\n\n**Condición para implementar.** Completar costos omitidos en el prototipo, verificar factores de emisión y acordar responsables, periodicidad de actualización y criterios de decisión.')
    st.header("De la analítica a la acción")
    st.subheader("Nuestra propuesta para Positiva")
    st.markdown("""
**1. Priorizar:** revisar técnicamente los cinco
vehículos identificados por el modelo.

**2. Validar:** obtener cotizaciones reales de
renovación eléctrica, alquiler y mantenimiento.

**3. Simular:** comparar el costo total y la huella
ambiental bajo diferentes escenarios.

**4. Implementar:** realizar un piloto controlado
antes de ampliar las decisiones a toda la flota.
""")
    st.subheader("Indicadores de seguimiento")
    st.write(
        "Costo por kilómetro, huella por kilómetro, "
        "gasto operativo, kilometraje y cumplimiento "
        "de las intervenciones priorizadas."
    )
    st.info(
        "Recomendación: utilizar la segmentación como "
        "herramienta de priorización, no como sustituto "
        "de la evaluación financiera y técnica."
    )
    st.markdown(
        "### Una flota más inteligente comienza "
        "con decisiones basadas en datos."
    )
