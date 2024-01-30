import streamlit as st
import pandas as pd
import numpy as np
import statistics as stat
import plotly.express as px
from scipy import stats
import math

# Configuración de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.header('Ensayo de Corte Directo ASTM D3080')
st.sidebar.header('Ensayo de corte Directo')
st.sidebar.subheader('Seleccionar archivos')

# Constantes
AREA = 0.06**2 * np.pi / 4
DEFORMACIONES = [0, 0.03, 0.06, 0.12, 0.21, 0.3, 0.45, 0.6, 0.75, 0.9, 1.05, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3, 3.6, 4.2, 4.8, 5.4, 6, 6.6, 7.2]
TIEMPO = [0, 0.13, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60]

# Funciones
def cargar_y_procesar_datos(ruta, es_corte, presion=None):
    if ruta is not None:
        df = pd.read_csv(ruta, sep=',', skiprows=2, header=None)
        if es_corte:
            df = df.assign(Esfuerzo_normal=presion)
        else:
            presion = np.round(stat.mode(df[8].iloc[1:]) / AREA, 2)
            df = df.assign(Esfuerzo_normal=presion, Tiempo=TIEMPO[:df.shape[0]])
        return df, presion
    return None, None

def procesar_datos_corte(df):
    inicio = next(k for k in df.index if df.iloc[k + 1, 4] - df.iloc[k, 4] > 0.01)
    df = df.iloc[inicio:]
    df[8] = df[8] - df.iloc[inicio, 8]
    df[4] = df[4] - df.iloc[inicio, 4]
    df[12] = df[12] - df.iloc[inicio, 12]

    # Interpolación para DEFORMACIONES
    filas_interpoladas = []
    for deformacion in DEFORMACIONES:
        df_filtrado = df[df[8] <= deformacion]
        if not df_filtrado.empty:
            fila_interpolada = df_filtrado.iloc[-1].copy()
            fila_interpolada[8] = deformacion  # Asegurarse de que la deformación sea exacta
            filas_interpoladas.append(fila_interpolada)

    df_interpolado = pd.DataFrame(filas_interpoladas, columns=[12, 4, 8, 'Esfuerzo_normal'])
    df_interpolado.columns = ['Def_Vert', 'F_tang', 'Def_tang', 'Esfuerzo_normal']
    return df_interpolado



# Carga de archivos y procesamiento
lista_presiones = []
lista_dfcorte_fill = []
c1, c2 = st.columns((1, 1))

for i in range(1, 4):
    ruta_cons = st.sidebar.file_uploader(f'Selecciona Especimen {i} - CONSOLIDACIÓN')
    ruta_cort = st.sidebar.file_uploader(f'Selecciona Especimen {i} - CORTE')

    df_cons, presion = cargar_y_procesar_datos(ruta_cons, es_corte=False)
    df_cort, _ = cargar_y_procesar_datos(ruta_cort, es_corte=True, presion=presion)

    if df_cons is not None:
        lista_presiones.append(presion)
        with c1:
            st.write(f'Especimen #{i} de Consolidación:', presion, 'kPa')
            st.write(df_cons)

    if df_cort is not None:
        df_cort_procesado = procesar_datos_corte(df_cort)
        lista_dfcorte_fill.append(df_cort_procesado)
        with c2:
            st.write(f'Especimen #{i} de Corte:')
            st.write(df_cort_procesado)

# Gráficos y análisis
if lista_dfcorte_fill:
    df_corte_fill = pd.concat(lista_dfcorte_fill, axis=0)
    grafico_corte = px.line(df_corte_fill, x='Def_tang', y='F_tang', color='Esfuerzo_normal', markers=True)
    st.write(grafico_corte)

    # Cálculo de envolvente de falla
    max_corte = [df['F_tang'].max() / AREA for df in lista_dfcorte_fill]
    envolvente = pd.DataFrame({'Esfuerzo_normal': lista_presiones, 'Esfuerzo_corte': max_corte})
    fig_envol = px.scatter(envolvente, x='Esfuerzo_normal', y='Esfuerzo_corte', trendline='ols')
    slope, intercept, r_value, p_value, std_err = stats.linregress(envolvente['Esfuerzo_normal'], envolvente['Esfuerzo_corte'])
    st.write(fig_envol)
    st.write(f'Ángulo de Fricción: {round(math.atan(slope) * 180 / np.pi, 2)}°')
    st.write(f'Cohesión: {round(intercept, 2)} kPa')
    st.write(f'r : {r_value}')

print('Hello Friend')
