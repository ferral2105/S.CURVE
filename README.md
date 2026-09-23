# 📈 Aplicación Web de Curva S para Control de Proyectos

Aplicación web desarrollada con **Streamlit** y gráficos estilizados en **Matplotlib** para la generación y monitoreo de gráficos de **Curva S de Avance de Proyecto** (Avance Planificado Acumulado vs. Avance Real Acumulado).

---

## 📁 Estructura del Proyecto

```text
curva_s_app/
│
├── app.py                      # Interfaz de usuario y dashboard en Streamlit
├── curva_s_logic.py            # Lógica de procesamiento de datos y gráficos Matplotlib
├── datos_avance_sinteticos.csv # Datos sintéticos de prueba (16 semanas)
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación de la aplicación
```

---

## ⚙️ Requisitos e Instalación

Asegúrate de contar con Python 3.9 o superior instalado.

1. Navega a la carpeta de la aplicación:
   ```bash
   cd curva_s_app
   ```

2. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Cómo Ejecutar la Aplicación

Para iniciar el servidor de Streamlit en tu navegador:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado (por defecto en `http://localhost:8501`).

---

## ✨ Características Principales

1. **Arquitectura Modular**: Separación total entre la lógica matemática/gráfica (`curva_s_logic.py`) y la interfaz Streamlit (`app.py`).
2. **Carga de Datos Personalizada o Muestra Sintética**: Permite usar el dataset sintético integrado o cargar cualquier archivo CSV.
3. **Gráficos Matplotlib Personalizables**:
   - Ajuste del título y temas (Claro / Oscuro).
   - Selector de colores para Curva Planificada y Curva Real.
   - Histograma de avance periódico por semana (barras inferiores).
   - Anotación automática del último avance real registrado.
4. **Métricas KPI Dinámicas**:
   - Avance Planificado Acumulado %
   - Avance Real Acumulado %
   - Desviación Acumulada % (Delta)
   - Índice de Desempeño del Cronograma (SPI)
   - Estado del Proyecto (Adelantado 🟢, En Fecha 🟡, Atrasado 🔴)
5. **Reportes y Descarga de Plantillas**:
   - Pestaña con tabla procesada de datos y descarga en formato CSV.
   - Descarga directa de plantilla CSV de ejemplo desde el Sidebar.
   - Diagnóstico automático del estado del proyecto.

---

## 📊 Formato del Archivo CSV

El archivo CSV cargado debe contener las siguientes columnas clave:
- `Periodo` (Ej: `Semana 01`, `Semana 02`, ...)
- `Avance_Planificado_Periodo_%` (Valor numérico del % planificado para la semana)
- `Avance_Real_Periodo_%` (Valor numérico del % ejecutado en la semana)
- *(Opcional)* `Costo_Planificado_USD` y `Costo_Real_USD` para análisis financiero.
