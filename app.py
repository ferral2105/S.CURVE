"""
app.py
======
Aplicación Web Principal en Streamlit para el Control de Proyectos y
Generación de Gráficos de Curva S.
"""

import os
import streamlit as st
import pandas as pd
from curva_s_logic import (
    procesar_datos_avance,
    crear_grafico_curva_s,
    obtener_plantilla_csv_bytes
)

# Configuración de página Streamlit
st.set_page_config(
    page_title="Curva S - Avance de Proyecto",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mejorar el diseño estético
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    # --- SIDEBAR LATERAL ---
    st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=64)
    st.sidebar.title("Navegación & Control")
    st.sidebar.markdown("---")

    # 1. Selector de Origen de Datos
    st.sidebar.subheader("📁 Origen de Datos")
    origen_datos = st.sidebar.radio(
        "Seleccione la fuente:",
        options=["Usar Datos Sintéticos de Muestra", "Cargar mi Archivo CSV"],
        index=0
    )

    df_cargado = None
    path_sintetico = os.path.join(os.path.dirname(__file__), "datos_avance_sinteticos.csv")

    if origen_datos == "Cargar mi Archivo CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Subir archivo CSV de avance",
            type=["csv"],
            help="Suba un archivo CSV con las columnas de avance planificado y real."
        )
        if uploaded_file is not None:
            try:
                df_cargado = pd.read_csv(uploaded_file)
                st.sidebar.success("✅ Archivo cargado correctamente.")
            except Exception as e:
                st.sidebar.error(f"❌ Error al leer el CSV: {e}")
        else:
            st.sidebar.info("💡 Por favor cargue un archivo CSV para visualizar.")
    else:
        if os.path.exists(path_sintetico):
            df_cargado = pd.read_csv(path_sintetico)
            st.sidebar.success("📊 Usando datos sintéticos de demostración.")
        else:
            st.sidebar.error("Archivo sintético no encontrado en el servidor.")

    st.sidebar.markdown("---")

    # 2. Configuración Personalizada del Gráfico
    st.sidebar.subheader("🎨 Personalización del Gráfico")
    titulo_grafico = st.sidebar.text_input("Título del Gráfico", value="Curva S de Avance Físico del Proyecto")
    mostrar_barras = st.sidebar.checkbox("Mostrar Histograma Periódico (Barras)", value=True)
    estilo_oscuro = st.sidebar.checkbox("Activar Tema Oscuro en Gráfico", value=False)

    col_c1, col_c2 = st.sidebar.columns(2)
    with col_c1:
        color_plan = st.color_picker("Curva Planificada", "#1F77B4")
    with col_c2:
        color_real = st.color_picker("Curva Real", "#2CA02C")

    grosor_linea = st.sidebar.slider("Grosor de Líneas", min_value=1.0, max_value=4.0, value=2.5, step=0.5)

    st.sidebar.markdown("---")

    # 3. Descarga de Plantilla CSV
    st.sidebar.subheader("📥 Descargar Plantilla")
    csv_bytes = obtener_plantilla_csv_bytes()
    st.sidebar.download_button(
        label="📄 Descargar Plantilla CSV Ejemplo",
        data=csv_bytes,
        file_name="plantilla_curva_s.csv",
        mime="text/csv"
    )

    # --- CUERPO PRINCIPAL DE LA PÁGINA ---
    st.markdown('<div class="main-header">📈 Dashboard de Control de Proyecto - Curva S</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Monitoreo del avance acumulado planificado vs. real mediante gráficos interactivos de Matplotlib.</div>',
        unsafe_allow_html=True
    )

    if df_cargado is None:
        st.warning("⚠️ No hay datos cargados para mostrar. Seleccione 'Usar Datos Sintéticos' o suba su archivo CSV en la barra lateral.")
        return

    # Procesar los datos cargados mediante la lógica separada
    try:
        df_procesado, kpis = procesar_datos_avance(df_cargado)
    except Exception as e:
        st.error(f"❌ Error durante el procesamiento de datos: {e}")
        st.info("Asegúrese de que su archivo CSV cumpla con los nombres de columnas requeridos. Consulte la pestaña 'Guía de Formato CSV'.")
        return

    # --- TARJETAS MÉTRICAS (KPIs) ---
    st.markdown("### 📊 Indicadores Clave de Desempeño (KPIs)")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.metric(
            label="Avance Planificado Acumulado",
            value=f"{kpis['planificado_acumulado_%']:.1f}%",
            help="Porcentaje acumulado esperado según el cronograma."
        )

    with kpi_col2:
        st.metric(
            label="Avance Real Acumulado",
            value=f"{kpis['real_acumulado_%']:.1f}%",
            delta=f"{kpis['desviacion_%']:+.1f}% vs Plan",
            help="Porcentaje de avance ejecutado a la fecha."
        )

    with kpi_col3:
        st.metric(
            label="Índice SPI (Cronograma)",
            value=f"{kpis['spi']:.2f}",
            delta="> 1.0 (Adelantado)" if kpis['spi'] >= 1.0 else "< 1.0 (Atrasado)",
            delta_color="normal" if kpis['spi'] >= 1.0 else "inverse",
            help="Schedule Performance Index (Avance Real / Avance Planificado)."
        )

    with kpi_col4:
        st.metric(
            label="Estado del Proyecto",
            value=kpis['estado'],
            delta=f"Último periodo: {kpis['periodo_actual']}",
            help="Evaluación del estado del proyecto según la variación de avance."
        )

    st.markdown("---")

    # --- VISUALIZACIÓN PRINCIPAL DEL GRÁFICO ---
    st.markdown("### 📉 Representación Gráfica de Curva S")
    
    # Generar la figura con Matplotlib
    fig = crear_grafico_curva_s(
        df=df_procesado,
        titulo=titulo_grafico,
        mostrar_barras=mostrar_barras,
        estilo_oscuro=estilo_oscuro,
        color_plan=color_plan,
        color_real=color_real,
        ancho_linea=grosor_linea
    )

    # Renderizar en Streamlit
    st.pyplot(fig, use_container_width=True)

    st.markdown("---")

    # --- SECCIÓN DE PESTAÑAS DETALLADAS ---
    tab_tabla, tab_analisis, tab_guia = st.tabs([
        "📋 Tabla de Avance de Datos",
        "🔍 Análisis y Diagnóstico",
        "📖 Guía de Formato CSV"
    ])

    # Pestaña 1: Tabla de Datos
    with tab_tabla:
        st.subheader("Tabla de Datos Procesada")
        st.write("A continuación se muestra el detalle numérico periodo a periodo:")
        
        # Formatear columnas para mejor lectura visual
        cols_a_mostrar = [
            'Periodo', 'Avance_Planificado_Periodo_%', 'Avance_Real_Periodo_%',
            'Avance_Planificado_Acumulado_%', 'Avance_Real_Acumulado_%',
            'Desviacion_Acumulada_%', 'SPI'
        ]
        if kpis['tiene_costos']:
            cols_a_mostrar.extend(['Costo_Planificado_USD', 'Costo_Real_USD', 'Variacion_Costo_USD'])

        cols_existentes = [c for c in cols_a_mostrar if c in df_procesado.columns]
        
        st.dataframe(
            df_procesado[cols_existentes].style.format({
                'Avance_Planificado_Periodo_%': '{:.2f}%',
                'Avance_Real_Periodo_%': '{:.2f}%',
                'Avance_Planificado_Acumulado_%': '{:.2f}%',
                'Avance_Real_Acumulado_%': '{:.2f}%',
                'Desviacion_Acumulada_%': '{:+.2f}%',
                'SPI': '{:.2f}',
                'Costo_Planificado_USD': '${:,.2f}',
                'Costo_Real_USD': '${:,.2f}',
                'Variacion_Costo_USD': '${:+,.2f}'
            }),
            use_container_width=True
        )

        # Botón para descargar los datos procesados en CSV
        csv_procesado = df_procesado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Descargar Reporte Completo en CSV",
            data=csv_procesado,
            file_name="reporte_avance_curva_s.csv",
            mime="text/csv"
        )

    # Pestaña 2: Análisis y Diagnóstico
    with tab_analisis:
        st.subheader("Resumen Ejecutivo y Diagnóstico del Proyecto")

        st.markdown(f"**Periodo de Evaluación:** `{kpis['periodo_actual']}` de {kpis['total_periodos']} periodos totales.")
        
        if kpis['desviacion_%'] > 1.0:
            st.success(f"🟢 **Proyecto Adelantado:** El avance real supera al planificado en +{kpis['desviacion_%']:.2f}%. Las actividades se están ejecutando a un ritmo superior a la línea base.")
        elif kpis['desviacion_%'] < -1.0:
            st.error(f"🔴 **Proyecto Atrasado:** El avance real presenta una desviación de {kpis['desviacion_%']:.2f}% respecto al plan original. Se recomienda tomar medidas correctivas e incrementar recursos.")
        else:
            st.info(f"🟡 **Proyecto En Fecha:** El proyecto se encuentra alineado con la línea base planificada (Desviación: {kpis['desviacion_%']:.2f}%).")

        st.markdown("#### Métricas Financieras y de Costo" if kpis['tiene_costos'] else "#### Análisis de Desempeño")
        if kpis['tiene_costos']:
            c_plan = kpis['costo_plan_acum_usd']
            c_real = kpis['costo_real_acum_usd']
            var_costo = kpis['variacion_costo_usd']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Costo Planificado Acumulado", f"${c_plan:,.2f}")
            c2.metric("Costo Real Acumulado", f"${c_real:,.2f}")
            c3.metric("Variación de Costo (CV)", f"${var_costo:+,.2f}", delta_color="normal" if var_costo >= 0 else "inverse")

            if var_costo >= 0:
                st.write("💡 **Ahorro de Costo:** Se ha gastado menos presupuesto de lo planificado para el periodo ejecutado.")
            else:
                st.write("⚠️ **Sobrecosto Detectado:** Los costos gastados superan la asignación presupuestaria planificada.")

    # Pestaña 3: Guía de Formato CSV
    with tab_guia:
        st.subheader("Instrucciones y Formato de Archivo CSV")
        st.markdown("""
        Para cargar su propio proyecto en la aplicación, prepare un archivo CSV que contenga las siguientes columnas obligatorias:

        1. **`Periodo`**: Nombre del periodo o semana (Ej: `Semana 01`, `Enero`, `P1`).
        2. **`Avance_Planificado_Periodo_%`**: Porcentaje de avance planificado ejecutable en dicho periodo (número entre 0 y 100).
        3. **`Avance_Real_Periodo_%`**: Porcentaje de avance real registrado en dicho periodo (número entre 0 y 100).

        *Columnas Opcionales para Análisis Financiero:*
        - **`Fecha`**: Fecha correspondiente en formato AAAA-MM-DD.
        - **`Costo_Planificado_USD`**: Costo planificado en dicho periodo.
        - **`Costo_Real_USD`**: Costo gastado en dicho periodo.

        #### Ejemplos de Estructura de Filas:
        | Periodo | Avance_Planificado_Periodo_% | Avance_Real_Periodo_% | Costo_Planificado_USD | Costo_Real_USD |
        | :--- | :--- | :--- | :--- | :--- |
        | Semana 01 | 5.0 | 4.5 | 25000 | 24000 |
        | Semana 02 | 10.0 | 9.8 | 50000 | 49000 |
        """)


if __name__ == "__main__":
    main()
