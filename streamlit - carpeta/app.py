import streamlit as st
import pandas as pd
import plotly.express as px

#  Configuracion de la Pagina 
st.set_page_config(
    page_title="Dashboard NBA",
    layout="wide"
)

#  Carga de Datos (con cache para mejorar rendimiento) 

def load_data():
    df = pd.read_csv('nba_all_elo.csv')
    df['date_game'] = pd.to_datetime(df['date_game'])

    return df

df = load_data()

#  Barra Lateral 
st.sidebar.header("Filtros del Dashboard")

# 1. Selector de Año 
sorted_years = sorted(df['year_id'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Seleccionar Año", sorted_years)

# 2. Selector de Equipo
teams_in_year = sorted(df[df['year_id'] == selected_year]['fran_id'].unique())
selected_team = st.sidebar.selectbox("Seleccionar Equipo", teams_in_year)

# 3. Selector de Tipo de Juego 
game_type = st.sidebar.pills(
    "Tipo de Juego",
    ["Temporada Regular", "Playoffs", "Ambos"],
    index=2  # "Ambos" seleccionado por defecto
)

#  Logica de Filtrado de Datos 
df_filtered = df[
    (df['year_id'] == selected_year) &
    (df['fran_id'] == selected_team)
]

# Aplicamos el filtro de tipo de juego
if game_type == "Temporada Regular":
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 0]
elif game_type == "Playoffs":
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 1]


df_filtered = df_filtered.sort_values(by='date_game')

#  Pagina Principal (Visualizaciones) 
st.title(f"Analisis de {selected_team} - Temporada {selected_year}")
st.markdown(f"Mostrando juegos de: **{game_type}**")

# Verificamos si hay datos despues de filtrar
if df_filtered.empty:
    st.warning("No hay datos disponibles para la seleccion actual.")
else:
    #  Calculos para las Graficas 

    # 1. Grafica de Lineas Acumuladas 
    df_filtered['is_win'] = (df_filtered['game_result'] == 'W').astype(int)
    df_filtered['is_loss'] = (df_filtered['game_result'] == 'L').astype(int)
    
    # Calculamos el acumulado 
    df_filtered['Victorias Acumuladas'] = df_filtered['is_win'].cumsum()
    df_filtered['Derrotas Acumuladas'] = df_filtered['is_loss'].cumsum()
    

    df_filtered['Numero de Juego'] = range(1, len(df_filtered) + 1)

    df_line_chart = df_filtered.melt(
        id_vars=['Numero de Juego'],
        value_vars=['Victorias Acumuladas', 'Derrotas Acumuladas'],
        var_name='Tipo de Resultado',
        value_name='Total Acumulado'
    )

    # 2. Grafica de Pastel 
    total_wins = df_filtered['is_win'].sum()
    total_losses = df_filtered['is_loss'].sum()
    
    df_pie_chart = pd.DataFrame({
        'Resultado': ['Victorias', 'Derrotas'],
        'Total': [total_wins, total_losses]
    })

    #  Mostrar Visualizaciones 
    
    st.header("Rendimiento Acumulado de la Temporada")
    # Grafica de Lineas
    fig_line = px.line(
        df_line_chart,
        x='Numero de Juego',
        y='Total Acumulado',
        color='Tipo de Resultado',
        title=f"Acumulado de Victorias vs. Derrotas",
        color_discrete_map={
            'Victorias Acumuladas': 'green',
            'Derrotas Acumuladas': 'red'
        }
    )
    fig_line.update_layout(xaxis_title="Juego #", yaxis_title="Total")
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.header("Porcentaje de Victorias y Derrotas")
    # Grafica de Pastel
    fig_pie = px.pie(
        df_pie_chart,
        names='Resultado',
        values='Total',
        title=f"Distribucion de Resultados (Total: {total_wins + total_losses} juegos)",
        color_discrete_map={'Victorias': 'green', 'Derrotas': 'red'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)


