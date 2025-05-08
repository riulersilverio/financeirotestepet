import streamlit as st
import pandas as pd
import plotly.express as px
import io # Necessário para ler string como arquivo CSV

# --- Configurações Iniciais ---
 LOGO_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLP5iDLJWxquSW4SOt-sSsRZS1yg6gcH7Vnw&s"

# Dados CSV embutidos diretamente no script
# Copie e cole os dados CSV que te passei anteriormente aqui dentro das aspas triplas
csv_data_string = """Data,Receita_Total,Custos_Operacionais,Novos_Clientes,Carteira_Credito_Ativa,Valor_Inadimplente
2022-01-31,30500,18200,8,150000,4500
2022-02-28,31200,18500,9,155000,4800
2022-03-31,33000,19000,10,162000,4700
2022-04-30,32500,19100,9,168000,5100
2022-05-31,34800,19500,11,175000,5000
2022-06-30,36000,20000,12,183000,5500
2022-07-31,35500,20200,11,190000,5800
2022-08-31,37200,20500,13,198000,6000
2022-09-30,38000,21000,14,205000,6100
2022-10-31,39500,21500,15,215000,6500
2022-11-30,41000,22000,16,225000,6800
2022-12-31,45000,23000,18,240000,7000
2023-01-31,42000,22500,15,245000,7200
2023-02-28,43500,22800,16,252000,7500
2023-03-31,46000,23500,17,260000,7700
2023-04-30,45500,23800,16,268000,8000
2023-05-31,48200,24000,19,278000,8100
2023-06-30,50000,24500,20,290000,8500
2023-07-31,49000,24800,18,298000,8800
2023-08-31,51500,25000,21,310000,9000
2023-09-30,53000,25500,22,320000,9200
2023-10-31,55000,26000,23,335000,9500
2023-11-30,57000,26500,25,350000,9800
2023-12-31,62000,27500,28,370000,10000
"""

# --- Interface Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

# Colocar o logo na sidebar
 st.sidebar.image(LOGO_URL, width=150) # Ajuste a largura conforme necessário
st.sidebar.title("Opções de Análise")

st.title("📊 Dashboard de Análise Financeira da Empresa")
st.markdown("Acompanhe os principais indicadores do seu negócio.")

# --- Lógica para Carregar Dados ---
df = None
data_source_info = ""

# Opção de Upload na Sidebar (ainda permite que o usuário substitua os dados embutidos)
uploaded_file = st.sidebar.file_uploader("Substituir dados base com seu arquivo CSV (opcional)", type=["csv"])

if uploaded_file is not None:
    st.sidebar.info("Usando arquivo carregado pelo usuário.")
    try:
        # Tentar ler com diferentes separadores comuns
        try:
            df_temp = pd.read_csv(uploaded_file, sep=',')
        except pd.errors.ParserError:
            df_temp = pd.read_csv(uploaded_file, sep=';')
        df = df_temp
        data_source_info = "Fonte dos Dados: Arquivo Carregado pelo Usuário"
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o arquivo CSV carregado: {e}")
        st.error(f"Não foi possível ler o arquivo CSV carregado. Usando dados base embutidos. Detalhes: {e}")
        # Se o upload falhar, cai para os dados embutidos
        df = None # Reseta df para garantir que os dados embutidos sejam carregados

# Se nenhum arquivo foi carregado (ou o carregamento falhou), usar os dados CSV embutidos
if df is None:
    try:
        st.sidebar.info("Usando dados base embutidos no script.")
        # Converter a string CSV em um objeto tipo arquivo para o Pandas ler
        data_io = io.StringIO(csv_data_string)
        df = pd.read_csv(data_io, sep=',') # Assumindo que o separador na string é vírgula
        data_source_info = "Fonte dos Dados: Dados Base Embutidos no Script"
    except Exception as e:
        st.error(f"Erro ao processar os dados CSV embutidos: {e}")
        st.stop() # Parar se os dados embutidos não puderem ser lidos

# Se nenhum DataFrame foi carregado (algo deu muito errado)
if df is None or df.empty:
    st.error("Não foi possível carregar nenhum dado. Verifique o script ou o arquivo carregado.")
    st.stop()

# --- Se o DataFrame foi carregado com sucesso ---
st.success(data_source_info)

# --- Tratamento de Dados Essencial ---
try:
    if 'Data' not in df.columns:
        st.error("A coluna 'Data' não foi encontrada nos dados. Verifique o cabeçalho.")
        st.stop()

    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df.dropna(subset=['Data'], inplace=True)

    if df.empty:
        st.error("Nenhuma data válida encontrada na coluna 'Data' após a conversão. Verifique o formato das datas.")
        st.stop()

    df = df.sort_values(by='Data')
    df.set_index('Data', inplace=True)

    st.sidebar.subheader("Período para Análise:")
    min_date = df.index.min().date()
    max_date = df.index.max().date()

    if min_date == max_date:
        start_date = min_date
        end_date = max_date
        st.sidebar.info(f"Apenas um período de dados disponível: {min_date.strftime('%d/%m/%Y')}")
    else:
        # Assegurar que start_date não seja maior que end_date no widget
        default_start_date = min_date
        default_end_date = max_date
        start_date_input = st.sidebar.date_input("Data Inicial", default_start_date, min_value=min_date, max_value=max_date)
        end_date_input = st.sidebar.date_input("Data Final", default_end_date, min_value=start_date_input, max_value=max_date) # min_value aqui é start_date_input

        start_date = start_date_input
        end_date = end_date_input


    df_filtrado = df[(df.index.date >= start_date) & (df.index.date <= end_date)]

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para o período selecionado.")
        st.stop()

    st.subheader(f"Análise do Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")

    # --- Cálculos de Indicadores Derivados ---
    if 'Receita_Total' in df_filtrado.columns and 'Custos_Operacionais' in df_filtrado.columns:
        df_filtrado['Lucro_Operacional_Bruto'] = df_filtrado['Receita_Total'] - df_filtrado['Custos_Operacionais']
        # Evitar divisão por zero na margem
        df_filtrado['Margem_Operacional_Bruta_%'] = 0.0
        mask_receita_positiva = df_filtrado['Receita_Total'] > 0
        df_filtrado.loc[mask_receita_positiva, 'Margem_Operacional_Bruta_%'] = \
            (df_filtrado.loc[mask_receita_positiva, 'Lucro_Operacional_Bruto'] / df_filtrado.loc[mask_receita_positiva, 'Receita_Total']) * 100
        df_filtrado['Margem_Operacional_Bruta_%'] = df_filtrado['Margem_Operacional_Bruta_%'].round(2)

    if 'Valor_Inadimplente' in df_filtrado.columns and 'Carteira_Credito_Ativa' in df_filtrado.columns:
        df_filtrado['Taxa_Inadimplencia_%'] = 0.0
        mask_carteira_positiva = df_filtrado['Carteira_Credito_Ativa'] > 0
        df_filtrado.loc[mask_carteira_positiva, 'Taxa_Inadimplencia_%'] = \
            (df_filtrado.loc[mask_carteira_positiva, 'Valor_Inadimplente'] / df_filtrado.loc[mask_carteira_positiva, 'Carteira_Credito_Ativa']) * 100
        df_filtrado['Taxa_Inadimplencia_%'] = df_filtrado['Taxa_Inadimplencia_%'].round(2)

    # --- Exibição dos Indicadores (KPIs) ---
    st.header("Principais KPIs (Último Período Selecionado)")
    if not df_filtrado.empty:
        ultimo_periodo = df_filtrado.iloc[-1]
        cols_kpi = st.columns(3)
        with cols_kpi[0]:
            if 'Receita_Total' in ultimo_periodo: st.metric(label="Receita Total", value=f"R$ {ultimo_periodo['Receita_Total']:,.2f}")
            if 'Novos_Clientes' in ultimo_periodo: st.metric(label="Novos Clientes", value=f"{ultimo_periodo.get('Novos_Clientes', 0):.0f}")
        with cols_kpi[1]:
            if 'Lucro_Operacional_Bruto' in ultimo_periodo: st.metric(label="Lucro Operacional", value=f"R$ {ultimo_periodo['Lucro_Operacional_Bruto']:,.2f}")
            if 'Carteira_Credito_Ativa' in ultimo_periodo: st.metric(label="Carteira de Crédito", value=f"R$ {ultimo_periodo.get('Carteira_Credito_Ativa', 0):,.2f}")
        with cols_kpi[2]:
            if 'Margem_Operacional_Bruta_%' in ultimo_periodo: st.metric(label="Margem Operacional", value=f"{ultimo_periodo['Margem_Operacional_Bruta_%']:.2f}%")
            if 'Taxa_Inadimplencia_%' in ultimo_periodo: st.metric(label="Taxa Inadimplência", value=f"{ultimo_periodo.get('Taxa_Inadimplencia_%', 0):.2f}%")
    else:
        st.info("Nenhum dado para exibir KPIs no período selecionado.")

    # --- Gráficos ---
    st.header("Visualização de Tendências")
    tabs_graficos = st.tabs(["Receitas e Lucros", "Clientes", "Crédito e Inadimplência", "Dados Completos"])

    with tabs_graficos[0]:
        colunas_receita_lucro = []
        if 'Receita_Total' in df_filtrado.columns: colunas_receita_lucro.append('Receita_Total')
        if 'Lucro_Operacional_Bruto' in df_filtrado.columns: colunas_receita_lucro.append('Lucro_Operacional_Bruto')

        if colunas_receita_lucro:
            fig_receita_lucro = px.line(df_filtrado.reset_index(), x='Data', y=colunas_receita_lucro,
                                        title="Evolução da Receita e Lucro Operacional",
                                        labels={'value': 'Valor (R$)', 'variable': 'Métrica'}, markers=True)
            fig_receita_lucro.update_layout(hovermode="x unified")
            st.plotly_chart(fig_receita_lucro, use_container_width=True)

        if 'Margem_Operacional_Bruta_%' in df_filtrado.columns:
            fig_margem = px.line(df_filtrado.reset_index(), x='Data', y='Margem_Operacional_Bruta_%',
                                 title="Evolução da Margem Operacional (%)",
                                 labels={'Margem_Operacional_Bruta_%': 'Margem (%)'}, markers=True)
            fig_margem.update_layout(hovermode="x unified")
            st.plotly_chart(fig_margem, use_container_width=True)

    with tabs_graficos[1]:
        if 'Novos_Clientes' in df_filtrado.columns:
            fig_clientes = px.bar(df_filtrado.reset_index(), x='Data', y='Novos_Clientes',
                                  title="Evolução de Novos Clientes",
                                  labels={'Novos_Clientes': 'Número de Novos Clientes'})
            st.plotly_chart(fig_clientes, use_container_width=True)

    with tabs_graficos[2]:
        if 'Carteira_Credito_Ativa' in df_filtrado.columns:
            fig_carteira = px.line(df_filtrado.reset_index(), x='Data', y='Carteira_Credito_Ativa',
                                   title="Evolução da Carteira de Crédito Ativa",
                                   labels={'Carteira_Credito_Ativa': 'Valor (R$)'}, markers=True)
            fig_carteira.update_layout(hovermode="x unified")
            st.plotly_chart(fig_carteira, use_container_width=True)

        if 'Taxa_Inadimplencia_%' in df_filtrado.columns:
            fig_inadimplencia = px.line(df_filtrado.reset_index(), x='Data', y='Taxa_Inadimplencia_%',
                                        title="Evolução da Taxa de Inadimplência (%)",
                                        labels={'Taxa_Inadimplencia_%': 'Taxa (%)'}, markers=True, color_discrete_sequence=['red'])
            fig_inadimplencia.update_layout(hovermode="x unified")
            st.plotly_chart(fig_inadimplencia, use_container_width=True)

    with tabs_graficos[3]:
        st.subheader("Tabela de Dados Filtrados")
        # Selecionar apenas colunas numéricas para formatação, e não formatar o índice
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns
        format_dict = {col: "{:,.2f}" for col in colunas_numericas}
        st.dataframe(df_filtrado.style.format(format_dict, na_rep="-"))


except Exception as e:
    st.error(f"Ocorreu um erro geral ao processar os dados: {e}")
    st.exception(e) # Mostra o traceback completo para depuração
    st.info("Verifique se os dados (embutidos ou carregados) estão formatados corretamente e se as colunas esperadas existem.")
