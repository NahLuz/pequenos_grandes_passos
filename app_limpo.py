# PARTE 1: Cabeçalho, leitura de dados, grupos e navegação

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from unidecode import unidecode

st.set_page_config(page_title="Pequenos Grandes PASSOS", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("dados.xlsx", header=1)
    df.columns = df.columns.str.strip()

    df["Categoria"] = df["Categoria"].astype(str).apply(
        lambda x: unidecode(x.strip().lower()))
    df["Preço"] = df["Preço"].astype(str).str.replace(
        "R$", "").str.replace(",", ".").str.replace(" ", "").astype(float)

    return df

# 🔹 ESTILO PERSONALIZADO (opcional e elegante!)
st.markdown("""
    <style>
    /* Cor da barra lateral e fonte mais legível */
    .css-1d391kg { font-family: 'Segoe UI', sans-serif !important; }
    .stRadio > div { flex-wrap: wrap !important; }
    .st-dx { font-weight: 500; color: #555; }

    /* Margem entre elementos */
    .element-container { margin-bottom: 1rem; }

    /* Cor de fundo leve nos filtros */
    .stSelectbox, .stMultiselect {
        background-color: #f9f9fc !important;
        border-radius: 6px;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# BANNER
st.image("img_futuro/banner_pgpassos.png", use_container_width=True)

# LEITURA E PREPARO DOS DADOS
with st.spinner("⏳ Carregando dados... isso pode levar alguns segundos se o app estiver acordando!"):
    df = carregar_dados()
    df.columns = df.columns.str.strip()

df["Categoria"] = df["Categoria"].astype(str).apply(
    lambda x: unidecode(x.strip().lower()))
df["Preço"] = df["Preço"].astype(str).str.replace(
    "R$", "").str.replace(",", ".").str.replace(" ", "").astype(float)

# 🔍 TRATAMENTO DE CATEGORIAS COM 'nan' ELIMINADO
categorias_validas = sorted([
    cat for cat in df["Categoria"].dropna().unique()
    if pd.notna(cat) and str(cat).strip().lower() != "nan"
])

# DICIONÁRIO DE GRUPOS
grupos = {
    "🏪 Todas as Categorias": categorias_validas,
    "👟 Calçados": [unidecode(c.lower()) for c in [
        "Calçados de Menina", "Calçados de Menino", "Calçados Esportivos",
        "Sandálias", "Chinelos", "Tênis de Corrida", "Sapatos Femininos",
        "Sapatos Masculinos", "Sandália Plana e Rasteirinha", "Sandálias e Chinelos", "Botas"]],
    "👗 Roupas": [unidecode(c.lower()) for c in [
        "Blusas", "Camisas", "Roupas de Meninas", "Roupas Masculinas",
        "Trajes e Conjuntos", "Vestimentas Esportivas e para o Ar Livre", "Conjuntos"]],
    "🎒 Acessórios": [unidecode(c.lower()) for c in [
        "Acessórios Infantis", "Bolsas Transversais e de ombro", "Bolsas e Bagagens"]],
    "🧸 Infantil": [unidecode(c.lower()) for c in [
        "Moda Infantil", "Acessórios Infantis", "Calçados de Menina", "Calçados de Menino", "Roupas de Meninas"]],
    "⛹️‍♀️ Esportivo": [unidecode(c.lower()) for c in [
        "Esportes e Atividades ao Ar Livre", "Calçados Esportivos", "Tênis de Corrida", "Vestimentas Esportivas e para o Ar Livre"]]
}

# NAVEGAÇÃO
aba = st.radio("📌 Navegue pelas seções:", [
    "🏠 Início", "📈 Análises", "🛍️ Produtos", "ℹ️ Sobre a Loja"], horizontal=True)

# PARTE 2: Aba Análises com métricas + gráficos completos

if aba == "📈 Análises":
    macro = st.selectbox("📂 Escolha uma categoria ampla:", list(grupos.keys()))
    subcategorias = grupos[macro]
    escolhidas = st.multiselect(
        "🎯 Refine por subcategorias:", subcategorias, default=subcategorias)

    produtos = df[df["Categoria"].isin(escolhidas)].copy()

    precos = produtos["Preço"].dropna()
    if precos.empty:
        st.warning("Nenhum produto com preço disponível.")
    else:
        preco_min, preco_max = int(precos.min()), int(precos.max())
        if preco_min < preco_max:
            faixa = st.slider("💸 Quanto deseja gastar?",
                              preco_min, preco_max, (preco_min, preco_max))
            produtos = produtos[produtos["Preço"].between(faixa[0], faixa[1])]
        else:
            st.markdown(
                f"💸 Todos os produtos têm o preço fixo de R$ {preco_min:.2f}")

    st.session_state["produtos_filtrados"] = produtos
    st.info("📣 Após aplicar os filtros, vá para a aba 👉 **Produtos** para conferir os resultados!")

    if not produtos.empty:
        # MÉTRICAS VISUAIS
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Distribuição", f"{len(produtos)}")
        with col2:
            st.metric("💸 Preço Médio", f"R$ {produtos['Preço'].mean():.2f}")
        with col3:
            st.metric("📦 Estoque", f"{int(produtos['Estoque'].sum())}")
        with col4:
            if "Gênero" in produtos.columns:
                genero_mode = produtos["Gênero"].mode()[0]
                qtd = produtos["Gênero"].value_counts()[genero_mode]
                st.metric("🧍‍♀️ Gênero Predominante", f"{genero_mode} ({qtd})")

        st.markdown("---")

        # GRÁFICO 1: Barras - Distribuição de Preços
        st.markdown("#### 🎯 Distribuição de Preços")
        faixas = pd.cut(produtos["Preço"], bins=[
                        0, 100, 200, 300, 400, 500, 10000])
        preco_faixas = produtos.groupby(faixas).size()
        fig1, ax1 = plt.subplots(figsize=(6, 3.5))
        ax1.bar(preco_faixas.index.astype(str),
                preco_faixas.values, color="#ba68c8")
        ax1.set_ylabel("Qtd. de Produtos")
        ax1.set_xlabel("Faixa de Preço (R$)")
        ax1.set_title("Distribuição de Preços")
        st.pyplot(fig1)

        # GRÁFICO 2: Pizza - Gênero
        if "Gênero" in produtos.columns:
            st.markdown("#### 🧍 Produtos por Gênero")
            genero_counts = produtos["Gênero"].value_counts()
            fig2, ax2 = plt.subplots(figsize=(3.5, 3.5))
            ax2.pie(genero_counts, labels=genero_counts.index,
                    autopct="%1.1f%%", startangle=90, colors=plt.cm.Pastel2.colors)
            ax2.set_title("Distribuição por Gênero")
            st.pyplot(fig2)

        # GRÁFICO 3: Linha - Preço vs Estoque
        st.markdown("#### 📈 Relação Preço x Estoque")
        prod_plot = produtos.dropna(
            subset=["Preço", "Estoque"]).sort_values("Preço")
        fig3, ax3 = plt.subplots(figsize=(6, 3.5))
        ax3.plot(prod_plot["Preço"], prod_plot["Estoque"],
                 color="#4db6ac", marker="o", linewidth=2)
        ax3.set_xlabel("Preço (R$)")
        ax3.set_ylabel("Estoque")
        ax3.set_title("Preço vs Estoque")
        st.pyplot(fig3)

        # GRÁFICO 4: Peso vs Taxa de Envio
        if "Peso" in produtos.columns and "Taxa de envio" in produtos.columns:
            st.markdown("#### 🚚 Custo de Envio por Peso")
            dados_frete = produtos.dropna(subset=["Peso", "Taxa de envio"])
            if not dados_frete.empty:
                agrupado = dados_frete.groupby(
                    "Peso")["Taxa de envio"].mean().sort_index()
                fig4, ax4 = plt.subplots(figsize=(6, 3.5))
                ax4.plot(agrupado.index, agrupado.values,
                         marker="o", color="#ffb74d", linewidth=2)
                ax4.set_title("Taxa de Envio Média por Peso")
                ax4.set_xlabel("Peso (kg)")
                ax4.set_ylabel("Taxa de Envio (R$)")
                st.pyplot(fig4)

# PARTE 3: Abas "Produtos", "Início" e  "Sobre a Loja"

# ABA PRODUTOS
elif aba == "🛍️ Produtos":
    produtos = st.session_state.get("produtos_filtrados", df.copy())

    # 🔁 Elimina produtos duplicados com mesmo nome
    produtos = produtos.drop_duplicates(subset=["Nome Simplificado"])

    if produtos.empty:
        st.warning("Nenhum produto disponível. Vá até a aba **Análises** e personalize sua vitrine.")
    else:
        st.subheader("🧾 Lista de Produtos")
        for _, row in produtos.iterrows():
            col1, col2 = st.columns([1, 6])
            with col1:
                nome_img = row["Imagem"] if pd.notna(row.get("Imagem")) else "placeholder.png"
                st.image(f"img_futuro/{nome_img}", width=80)
            with col2:
                nome = row.get("Nome Simplificado", "Produto")
                preco = f"R$ {float(row['Preço']):.2f}" if pd.notna(row.get("Preço")) else "Preço indisponível"
                genero = row.get("Gênero", "")

                link = str(row.get("Link", "")).strip()

                if link.startswith("http"):
                    st.markdown(
                        f"<strong><a href='{link}' target='_blank'>{nome}</a></strong><br>{genero} — {preco}",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"**{nome}**<br>{genero} — {preco}",
                        unsafe_allow_html=True
                    )

# ABA INÍCIO
elif aba == "🏠 Início":
    st.subheader("👣 Bem-vinda(o) à loja Pequenos Grandes PASSOS!")
    st.markdown("""
    Explore os dados e descubra os produtos mais queridos da nossa loja!

    - Vá até a aba 👉 **Análises** para visualizar métricas e gráficos  
    - Navegue até 👉 **Produtos** para ver os resultados filtrados  
    - Conheça mais em **Sobre a Loja**

    🌈 Tudo feito com carinho para acompanhar cada passo da infância!
    """)

# ABA SOBRE
elif aba == "ℹ️ Sobre a Loja":
    st.title("ℹ️ Sobre a Loja")
    st.markdown("""
    _Pequenos Grandes PASSOS_ é uma loja especializada em calçados, roupas e acessórios infantis, com foco em **qualidade**, **conforto** e **estilo**.

    Nosso propósito é acompanhar cada passo da infância com carinho —  
    da primeira descoberta ao primeiro desfile no quintal.

    👣 Do primeiro sapatinho às aventuras do dia a dia, estamos aqui para celebrar cada momento especial da infância.

    🌈 Seja bem-vinda ao nosso mundo encantado!
    """)

    st.markdown("---")

    st.markdown("### 🌟 Uma história por trás da loja...")
    st.markdown("""
    Nem só de dados vive um app — também vive de histórias. E a da *Pequenos Grandes PASSOS* começa como muitas jornadas de aprendizado: cheia de arquivos quebrados, pip travando, Python fazendo birra… e uma desenvolvedora determinada com o cabelo hidratado e a coragem em dia! 💁‍♀️💻

    Esse projeto foi criado com muito carinho por mim, **Hannah**, como parte do meu caminho no **Bootcamp da TripleTen**. Mesmo com alguns atrasos nas entregas (rs), nunca perdi de vista o objetivo: aprender de verdade, evoluir, e colocar no ar uma aplicação com alma própria — que une moda, dados, e um pouco de confete.

    Cada pedacinho aqui representa um avanço pessoal:  
    💡 Os gráficos? Antes nem rodavam.  
    🧾 A vitrine de produtos? Virou desfile.  
    🚚 A análise de frete? Tá no ponto!

    Esse app é mais do que um desafio técnico. É uma lembrança de que com consistência, bom humor e uns emojis estrategicamente posicionados, a gente chega lá.

    Obrigada por visitar minha loja — e se você chegou até aqui, saiba que o deploy só foi possível graças a muito ctrl+z, café e força de vontade 💖
    """)
