"""
curva_s_logic.py
================
Módulo de cálculo y generación gráfica para la aplicación de Curva S.
Separa la lógica de procesamiento de datos y la renderización con Matplotlib
de la interfaz de usuario de Streamlit.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def procesar_datos_avance(df_input: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Valida y procesa el DataFrame de entrada calculando los acumulados,
    desviaciones e indicadores clave de desempeño (KPIs).

    Retorna:
        - df_procesado: DataFrame con columnas acumuladas y de variación.
        - kpis: Diccionario con métricas resumidas del proyecto.
    """
    df = df_input.copy()

    # Limpieza de nombres de columnas
    df.columns = [c.strip() for c in df.columns]

    # Validar columnas requeridas
    col_plan_per = 'Avance_Planificado_Periodo_%'
    col_real_per = 'Avance_Real_Periodo_%'
    
    if col_plan_per not in df.columns or col_real_per not in df.columns:
        raise ValueError(
            f"El archivo CSV debe contener las columnas '{col_plan_per}' y '{col_real_per}'."
        )

    # Convertir a flotantes por seguridad
    df[col_plan_per] = pd.to_numeric(df[col_plan_per], errors='coerce').fillna(0)
    df[col_real_per] = pd.to_numeric(df[col_real_per], errors='coerce').fillna(0)

    # Calcular Avances Acumulados
    df['Avance_Planificado_Acumulado_%'] = df[col_plan_per].cumsum()
    df['Avance_Real_Acumulado_%'] = df[col_real_per].cumsum()

    # Cap de porcentaje máximo al 100%
    df['Avance_Planificado_Acumulado_%'] = df['Avance_Planificado_Acumulado_%'].clip(upper=100.0)
    df['Avance_Real_Acumulado_%'] = df['Avance_Real_Acumulado_%'].clip(upper=100.0)

    # Desviación acumulada (%)
    df['Desviacion_Acumulada_%'] = df['Avance_Real_Acumulado_%'] - df['Avance_Planificado_Acumulado_%']

    # SPI (Schedule Performance Index)
    df['SPI'] = np.where(
        df['Avance_Planificado_Acumulado_%'] > 0,
        df['Avance_Real_Acumulado_%'] / df['Avance_Planificado_Acumulado_%'],
        1.0
    )

    # Procesar Costos si existen en el dataset
    has_costs = ('Costo_Planificado_USD' in df.columns) and ('Costo_Real_USD' in df.columns)
    if has_costs:
        df['Costo_Planificado_USD'] = pd.to_numeric(df['Costo_Planificado_USD'], errors='coerce').fillna(0)
        df['Costo_Real_USD'] = pd.to_numeric(df['Costo_Real_USD'], errors='coerce').fillna(0)
        df['Costo_Planificado_Acumulado_USD'] = df['Costo_Planificado_USD'].cumsum()
        df['Costo_Real_Acumulado_USD'] = df['Costo_Real_USD'].cumsum()
        df['Variacion_Costo_USD'] = df['Costo_Planificado_Acumulado_USD'] - df['Costo_Real_Acumulado_USD']

    # Obtener último periodo cargado con avance real > 0 o último periodo
    periodos_con_avance = df[df[col_real_per] > 0]
    if not periodos_con_avance.empty:
        idx_ultimo = periodos_con_avance.index[-1]
    else:
        idx_ultimo = df.index[-1] if len(df) > 0 else 0

    row_actual = df.loc[idx_ultimo]
    plan_actual = float(row_actual['Avance_Planificado_Acumulado_%'])
    real_actual = float(row_actual['Avance_Real_Acumulado_%'])
    desv_actual = float(row_actual['Desviacion_Acumulada_%'])
    spi_actual = float(row_actual['SPI'])
    periodo_nombre = str(row_actual.get('Periodo', f"Periodo {idx_ultimo + 1}"))

    # Estado del proyecto
    if desv_actual > 1.0:
        estado = "Adelantado 🟢"
        color_estado = "green"
    elif desv_actual < -1.0:
        estado = "Atrasado 🔴"
        color_estado = "red"
    else:
        estado = "En Fecha 🟡"
        color_estado = "orange"

    kpis = {
        'periodo_actual': periodo_nombre,
        'planificado_acumulado_%': plan_actual,
        'real_acumulado_%': real_actual,
        'desviacion_%': desv_actual,
        'spi': spi_actual,
        'estado': estado,
        'color_estado': color_estado,
        'total_periodos': len(df),
        'tiene_costos': has_costs
    }

    if has_costs:
        kpis['costo_plan_acum_usd'] = float(row_actual['Costo_Planificado_Acumulado_USD'])
        kpis['costo_real_acum_usd'] = float(row_actual['Costo_Real_Acumulado_USD'])
        kpis['variacion_costo_usd'] = float(row_actual['Variacion_Costo_USD'])

    return df, kpis


def crear_grafico_curva_s(
    df: pd.DataFrame,
    titulo: str = "Curva S de Avance de Proyecto",
    mostrar_barras: bool = True,
    estilo_oscuro: bool = False,
    color_plan: str = "#1f77b4",
    color_real: str = "#2ca02c",
    ancho_linea: float = 2.5
) -> plt.Figure:
    """
    Genera el gráfico de la Curva S utilizando Matplotlib.
    
    Parámetros:
        - df: DataFrame procesado con avances acumulados y periódicos.
        - titulo: Título del gráfico.
        - mostrar_barras: Si True, incluye un subgráfico inferior con los avances semanales.
        - estilo_oscuro: Si True, usa un tema oscuro ajustado.
        - color_plan: Color de la curva planificada.
        - color_real: Color de la curva real.
        - ancho_linea: Grosor de las líneas.
    """
    # Configuración de tema/colores según estilo
    if estilo_oscuro:
        bg_color = "#0e1117"
        paper_color = "#161b22"
        text_color = "#ffffff"
        grid_color = "#30363d"
    else:
        bg_color = "#ffffff"
        paper_color = "#f8f9fa"
        text_color = "#212529"
        grid_color = "#e0e0e0"

    x_labels = df['Periodo'].astype(str) if 'Periodo' in df.columns else df.index.astype(str)
    x_indices = np.arange(len(df))

    # Crear figura con 1 o 2 subplots según opción mostrar_barras
    if mostrar_barras:
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(10, 7), sharex=True,
            gridspec_kw={'height_ratios': [3, 1]}
        )
    else:
        fig, ax1 = plt.subplots(figsize=(10, 5.5))
        ax2 = None

    fig.patch.set_facecolor(bg_color)
    ax1.set_facecolor(paper_color)

    # --- DIBUJO DE LA CURVA S (ACUMULADOS) ---
    plan_acum = df['Avance_Planificado_Acumulado_%']
    real_acum = df['Avance_Real_Acumulado_%']

    ax1.plot(
        x_indices, plan_acum,
        label='Avance Planificado Acumulado (%)',
        color=color_plan, linestyle='--', marker='o', linewidth=ancho_linea, markersize=5
    )
    ax1.plot(
        x_indices, real_acum,
        label='Avance Real Acumulado (%)',
        color=color_real, linestyle='-', marker='s', linewidth=ancho_linea, markersize=5
    )

    # Resaltar punto final del avance real
    idx_real_validos = df[df['Avance_Real_Periodo_%'] > 0].index
    if len(idx_real_validos) > 0:
        idx_last = idx_real_validos[-1]
        val_last = real_acum.loc[idx_last]
        ax1.annotate(
            f'Real: {val_last:.1f}%',
            xy=(idx_last, val_last),
            xytext=(idx_last, val_last + 5),
            arrowprops=dict(facecolor=color_real, shrink=0.05, width=1, headwidth=6),
            fontsize=9, fontweight='bold', color=text_color, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc=paper_color, ec=color_real, lw=1.5)
        )

    # Personalización de ax1 (Curva S)
    ax1.set_title(titulo, fontsize=14, fontweight='bold', color=text_color, pad=12)
    ax1.set_ylabel('Avance Acumulado (%)', fontsize=11, fontweight='bold', color=text_color)
    ax1.set_ylim(0, 105)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.grid(True, linestyle=':', color=grid_color, alpha=0.7)
    ax1.tick_params(colors=text_color, labelsize=9)
    ax1.legend(facecolor=paper_color, edgecolor=grid_color, labelcolor=text_color, loc='upper left')

    for spine in ax1.spines.values():
        spine.set_color(grid_color)

    # --- DIBUJO DE HISTOGRAMA DE AVANCES PERIÓDICOS (BARRA INFERIOR) ---
    if mostrar_barras and ax2 is not None:
        ax2.set_facecolor(paper_color)
        width = 0.35
        
        ax2.bar(
            x_indices - width/2, df['Avance_Planificado_Periodo_%'],
            width=width, label='Planificado Periodo (%)', color=color_plan, alpha=0.6
        )
        ax2.bar(
            x_indices + width/2, df['Avance_Real_Periodo_%'],
            width=width, label='Real Periodo (%)', color=color_real, alpha=0.8
        )

        ax2.set_ylabel('Avance Periodo (%)', fontsize=9, fontweight='bold', color=text_color)
        ax2.set_xlabel('Periodos / Semanas', fontsize=10, fontweight='bold', color=text_color)
        ax2.grid(True, linestyle=':', color=grid_color, alpha=0.7)
        ax2.tick_params(colors=text_color, labelsize=9)
        ax2.legend(facecolor=paper_color, edgecolor=grid_color, labelcolor=text_color, loc='upper right', fontsize=8)
        
        for spine in ax2.spines.values():
            spine.set_color(grid_color)
    else:
        ax1.set_xlabel('Periodos / Semanas', fontsize=10, fontweight='bold', color=text_color)

    # Ajustar marcas del eje X
    plt.xticks(x_indices, x_labels, rotation=45, ha='right', color=text_color)
    plt.tight_layout()

    return fig


def obtener_plantilla_csv_bytes() -> bytes:
    """
    Genera los bytes de un archivo CSV de ejemplo para descargar como plantilla.
    """
    df_ejemplo = pd.DataFrame({
        'Periodo': [f'Semana {i:02d}' for i in range(1, 13)],
        'Fecha': pd.date_range(start='2026-01-05', periods=12, freq='W-MON').strftime('%Y-%m-%d'),
        'Avance_Planificado_Periodo_%': [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 14.0, 12.0, 8.0, 6.0, 4.0, 2.0],
        'Avance_Real_Periodo_%': [3.8, 5.5, 7.8, 9.5, 11.8, 13.5, 13.0, 11.5, 7.5, 5.8, 3.5, 2.0],
        'Costo_Planificado_USD': [20000, 30000, 40000, 50000, 60000, 70000, 70000, 60000, 40000, 30000, 20000, 10000],
        'Costo_Real_USD': [19500, 29000, 39000, 49500, 59000, 68500, 69000, 58000, 39500, 29000, 19000, 9500]
    })
    return df_ejemplo.to_csv(index=False).encode('utf-8')


if __name__ == "__main__":
    import os
    import sys
    # Soporte de codificación UTF-8 para consola de Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "datos_avance_sinteticos.csv")
    print(f"📌 Ejecutando prueba de curva_s_logic.py...")
    print(f"📂 Ruta del archivo CSV local: {csv_path}")

    if os.path.exists(csv_path):
        df_raw = pd.read_csv(csv_path)
        df_proc, kpis = procesar_datos_avance(df_raw)
        print("✅ Lectura y procesamiento del archivo CSV exitosos:")
        print(f"   • Periodos totales: {kpis['total_periodos']}")
        print(f"   • Avance Planificado Acumulado: {kpis['planificado_acumulado_%']:.2f}%")
        print(f"   • Avance Real Acumulado: {kpis['real_acumulado_%']:.2f}%")
        print(f"   • Desviación Acumulada: {kpis['desviacion_%']:+.2f}%")
        print(f"   • Estado del Proyecto: {kpis['estado']}")
    else:
        print(f"❌ No se encontró el archivo CSV en la ruta especificada: {csv_path}")

