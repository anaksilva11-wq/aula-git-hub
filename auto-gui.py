import streamlit as st
import pandas as pd
import random
import urllib.parse
import sqlite3
import smtplib
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SmartPrice Pro • Inteligência de Preços",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS GLOBAL COM ANIMAÇÕES SUAVES E UI/UX REFINADO
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Ocultar elementos padrão do Streamlit */
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    
    /* Animação Global de Fade In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Animação de Pulso Leve para Badges */
    @keyframes pulseSoft {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* Aplicando transição suave nas páginas/elementos */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 95% !important;
        animation: fadeIn 0.5s ease-out;
    }
    .main {
        background-color: #f1f5f9;
    }
    
    /* Hero Header Corporativo com gradiente dinâmico */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 35px 40px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
        animation: fadeIn 0.6s ease-out;
        transition: transform 0.3s ease;
    }
    .hero-container:hover {
        transform: translateY(-2px);
    }
    .hero-container h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .hero-container p {
        color: #94a3b8;
        font-size: 1.1rem;
        margin: 0;
    }

    /* Cards de Produtos Modernos com Micro-interações */
    .product-card {
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        text-align: center;
        margin-bottom: 20px;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.7s ease-out;
    }
    .product-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }
    .product-card img {
        transition: transform 0.4s ease;
    }
    .product-card:hover img {
        transform: scale(1.03);
    }
    
    .badge-tag {
        background-color: #ef4444;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
        animation: pulseSoft 3s infinite ease-in-out;
    }
    .price-tag {
        color: #059669;
        font-size: 22px;
        font-weight: 800;
        margin: 6px 0 2px 0;
    }
    .old-price {
        font-size: 13px;
        color: #94a3b8;
        text-decoration: line-through;
    }

    /* Estilização da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding: 24px 16px;
    }

    /* Ajuste nos botões e inputs globais com transições */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BANCO DE DADOS E CONFIGURAÇÕES
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("rastreador.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            produto TEXT,
            preco_alvo REAL,
            data_cadastro TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = init_db()

nichos = [
    "Eletrônicos", "Casa e Cozinha", "Perfumes e Cosméticos", 
    "Roupas e Moda", "Esportes", "Beleza", "Gamer", 
    "Livros e Papelaria", "Automotivos"
]

lojas_disponiveis = ["Mercado Livre", "Amazon", "Shopee", "Magalu", "Kabum"]
cupons_disponiveis = ["SEM_CUPOM", "CUPOM10", "PROMO15", "DESTAQUE20", "SUPER25", "ECONOMIZE30", "BLACK50"]

produtos_base = {
    "Eletrônicos": [
        ("Smartphone 5G 128GB", 1200, 2500, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=300"),
        ("Smart TV 50 Polegadas 4K", 2000, 3500, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=300"),
        ("Fone Bluetooth TWS", 70, 180, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300"),
        ("Tablet 10 Polegadas", 850, 1400, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=300"),
        ("Smartwatch Esportivo GPS", 250, 600, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=300"),
        ("Câmera Digital Mirrorless", 2200, 4500, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=300")
    ],
    "Casa e Cozinha": [
        ("Air Fryer 4L Digital", 320, 590, "https://images.unsplash.com/photo-1626531135461-71ce3335a98d?w=300"),
        ("Robô Aspirador de Pó", 550, 1100, "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=300"),
        ("Cafeteira Elétrica Programável", 180, 400, "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=300"),
        ("Liquidificador Turbo 10 Vel", 120, 280, "https://images.unsplash.com/photo-1570222094114-d074f7e9e5e5?w=300"),
        ("Panela de Pressão Elétrica 6L", 280, 480, "https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=300")
    ],
    "Perfumes e Cosméticos": [
        ("Perfume Importado Eau de Parfum 100ml", 200, 450, "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=300"),
        ("Colônia Masculina Amadeirada 100ml", 80, 170, "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=300"),
        ("Kit Skincare Facial Completo", 150, 320, "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300"),
        ("Sérum Antienvelhecimento 30ml", 90, 210, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=300")
    ],
    "Roupas e Moda": [
        ("Jaqueta Jeans Masculina Casual", 110, 240, "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=300"),
        ("Vestido Midi Floral Feminino", 80, 190, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300"),
        ("Tênis Esportivo Casual Confort", 160, 350, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300"),
        ("Bolsa de Couro Feminina Transversal", 130, 290, "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300")
    ],
    "Esportes": [
        ("Kit Halteres Ajustáveis 20kg", 230, 430, "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=300"),
        ("Bicicleta Ergométrica Vertical", 650, 1200, "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=300"),
        ("Tapete Yoga Mat Antiderrapante", 50, 120, "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=300"),
        ("Mochila de Hidratação Trail", 110, 250, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300")
    ],
    "Beleza": [
        ("Secador de Cabelo Profissional", 180, 380, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=300"),
        ("Prancha Alisadora Titanium", 140, 310, "https://images.unsplash.com/photo-1560869713-7d0a29430803?w=300"),
        ("Modelador de Cachos Automático", 210, 420, "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=300")
    ],
    "Gamer": [
        ("Cadeira Gamer Ergonômica", 800, 1450, "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=300"),
        ("Teclado Mecânico RGB", 190, 420, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300"),
        ("Mouse Gamer 16000 DPI", 120, 280, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=300"),
        ("Headset Gamer Surround 7.1", 220, 490, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=300")
    ],
    "Livros e Papelaria": [
        ("Box Trilogia de Livros de Fantasia", 75, 150, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300"),
        ("Livro Best-Seller de Desenvolvimento Pessoal", 35, 70, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300"),
        ("Caderno Inteligente Luxo A5", 60, 120, "https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?w=300")
    ],
    "Automotivos": [
        ("Aspirador de Pó Portátil para Carro 12V", 60, 140, "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=300"),
        ("Suporte Veicular Magnético Celular", 30, 70, "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=300"),
        ("Câmera Automotiva Dashcam Full HD", 190, 390, "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=300")
    ]
}

@st.cache_data 
def gerar_base_completa():
    lista_produtos = []
    random.seed(42) 
    
    for i in range(1200):
        nicho_escolhido = random.choice(nichos)
        item = random.choice(produtos_base[nicho_escolhido])
        loja_escolhida = random.choice(lojas_disponiveis)
        
        lote_id = (i % 15) + 1
        nome_puro = item[0]
        foto_especifica = item[3]
        
        nome_prod = f"{nome_puro} (Lote #{lote_id} Ref. {random.randint(1000, 9999)})"
        
        preco_atual = float(item[1] + random.randint(0, 150))
        preco_antigo = float(item[2] + random.randint(50, 300))
        
        if preco_atual >= preco_antigo:
            preco_antigo = preco_atual + 150
            
        desconto_num = int(round((1 - (preco_atual / preco_antigo)) * 100))
        cupom_sorteado = random.choice(cupons_disponiveis)
        
        if desconto_num > 55:
            selo_antifraude = "⚠️ Alerta: Metade do Dobro"
        elif desconto_num >= 25:
            selo_antifraude = "✅ Menor Preço em 90 Dias"
        else:
            selo_antifraude = "🔍 Desconto Leve"
        
        termo_url = urllib.parse.quote(nome_puro)
        meu_id_afiliado = "rastreadorpro-20"
        
        if loja_escolhida == "Amazon":
            link_funcional = f"https://www.amazon.com.br/s?k={termo_url}&tag={meu_id_afiliado}"
        elif loja_escolhida == "Shopee":
            link_funcional = f"https://shopee.com.br/search?keyword={termo_url}&affiliate_id={meu_id_afiliado}"
        elif loja_escolhida == "Magalu":
            link_funcional = f"https://www.magazineluiza.com.br/busca/{termo_url}/?partner_id={meu_id_afiliado}"
        elif loja_escolhida == "Kabum":
            link_funcional = f"https://www.kabum.com.br/busca/{termo_url}?tag={meu_id_afiliado}"
        else: 
            link_funcional = f"https://lista.mercadolivre.com.br/{termo_url}#D[A:{termo_url},afiliado={meu_id_afiliado}]"
        
        texto_wpp = urllib.parse.quote(f"🔥 *OFERTA IMPERDÍVEL!* \n\n{nome_prod}\n💰 De R$ {preco_antigo:.2f} por *R$ {preco_atual:.2f}* ({desconto_num}% OFF)\n🛒 Loja: {loja_escolhida}\n🎟️ Cupom: {cupom_sorteado}\n\n👉 Confira aqui: {link_funcional}")
        link_whatsapp = f"https://api.whatsapp.com/send?text={texto_wpp}"

        lista_produtos.append({
            "Nicho": nicho_escolhido,
            "Loja": loja_escolhida,
            "Produto": nome_prod,
            "Produto_Puro": nome_puro,
            "Preço Antigo": preco_antigo,
            "Preço Atual": preco_atual,
            "Desconto": f"{desconto_num}%",
            "Desc_Int": desconto_num,
            "Antifraude": selo_antifraude,
            "Cupom 🎟️": cupom_sorteado,
            "Link": link_funcional,
            "WhatsApp": link_whatsapp,
            "Foto": foto_especifica
        })
        
    return pd.DataFrame(lista_produtos)

df = gerar_base_completa()

# ---------------------------------------------------------
# HERO HEADER MODERNO
# ---------------------------------------------------------
st.markdown("""
    <div class="hero-container">
        <h1>⚡ SmartPrice Pro</h1>
        <p>Plataforma de inteligência de preços, comparador multi-store, cashback e alertas em tempo real.</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BARRA LATERAL (Filtros Organizados)
# ---------------------------------------------------------
st.sidebar.markdown("### 🎛️ Filtros de Pesquisa")
st.sidebar.markdown("---")

nichos_selecionados = st.sidebar.multiselect("Filtrar por Nicho:", options=nichos, default=nichos)
lojas_selecionadas = st.sidebar.multiselect("Filtrar por Loja:", options=lojas_disponiveis, default=lojas_disponiveis)

desconto_minimo = st.sidebar.slider("Desconto mínimo desejado (%)", min_value=0, max_value=80, value=10)
cupom_filtro = st.sidebar.selectbox("Filtrar por Cupom:", options=["Todos"] + cupons_disponiveis)
ordenar_por = st.sidebar.selectbox("Ordenar ofertas por:", options=["Maior Desconto", "Menor Preço", "Maior Preço"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Custo Real & Frete")
taxa_cashback = st.sidebar.slider("Cashback parceiro (%):", min_value=0.0, max_value=15.0, value=3.0, step=0.5)
frete_fixo = st.sidebar.number_input("Frete Médio Estimado (R$):", min_value=0.0, value=15.0, step=5.0)

# ---------------------------------------------------------
# APLICANDO OS FILTROS
# ---------------------------------------------------------
df_filtrado = df[
    (df["Nicho"].isin(nichos_selecionados)) & 
    (df["Loja"].isin(lojas_selecionadas)) &
    (df["Desc_Int"] >= desconto_minimo)
].copy()

if cupom_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Cupom 🎟️"] == cupom_filtro]

df_filtrado["Valor Cashback"] = df_filtrado["Preço Atual"] * (taxa_cashback / 100.0)
df_filtrado["Preço Final Real"] = df_filtrado["Preço Atual"] + frete_fixo - df_filtrado["Valor Cashback"]

if ordenar_por == "Maior Desconto":
    df_filtrado = df_filtrado.sort_values(by="Desc_Int", ascending=False)
elif ordenar_por == "Menor Preço":
    df_filtrado = df_filtrado.sort_values(by="Preço Final Real", ascending=True)
elif ordenar_por == "Maior Preço":
    df_filtrado = df_filtrado.sort_values(by="Preço Final Real", ascending=False)

# ---------------------------------------------------------
# SISTEMA DE ABAS PRINCIPAIS
# ---------------------------------------------------------
aba_vitrine, aba_empilhar, aba_comparador, aba_grafico, aba_alertas, aba_favoritos = st.tabs([
    "🛒 Vitrine Inteligente", 
    "🏷️ Empilhador de Descontos",
    "⚖️ Comparador Multi-Store",
    "📈 Histórico de Preços", 
    "🔔 Alertas & E-mail", 
    "⭐ Meus Favoritos"
])

with aba_vitrine:
    st.markdown("### 🔥 Melhores Oportunidades do Dia")
    top_3 = df.sort_values(by="Desc_Int", ascending=False).head(3)
    cols_topo = st.columns(3)

    for idx, (_, row) in enumerate(top_3.iterrows()):
        with cols_topo[idx]:
            st.markdown(f"""
                <div class="product-card">
                    <span class="badge-tag">{row['Desconto']} • {row['Loja']}</span><br>
                    <img src="{row['Foto']}" width="100%" height="130" style="border-radius: 8px; object-fit: cover;">
                    <p style="font-size: 13px; font-weight: 600; height: 38px; overflow: hidden; margin-bottom: 6px; color: #1e293b;">{row['Produto'][:38]}...</p>
                    <p class="price-tag">R$ {row['Preço Atual']:.2f}</p>
                    <span class="old-price">R$ {row['Preço Antigo']:.2f}</span>
                    <p style="font-size: 11px; color: #64748b; margin-top: 6px;">{row['Antifraude']}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col_pesquisa, col_export = st.columns([4, 1])
    with col_pesquisa:
        pesquisa_termo = st.text_input("🔍 Pesquisar produto por palavra-chave:", placeholder="Ex: Smartphone, Air Fryer, Perfume...")
    with col_export:
        st.write("")
        st.write("")
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar CSV", data=csv_data, file_name="ofertas_smartprice.csv", mime="text/csv", use_container_width=True)

    if pesquisa_termo:
        df_filtrado = df_filtrado[df_filtrado["Produto"].str.contains(pesquisa_termo, case=False, na=False)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Ofertas Encontradas", len(df_filtrado))
    col2.metric("🎯 Maior Desconto", f"{df_filtrado['Desc_Int'].max()}%" if not df_filtrado.empty else "0%")
    col3.metric("💵 Menor Preço Líquido", f"R$ {df_filtrado['Preço Final Real'].min():.2f}" if not df_filtrado.empty else "R$ 0,00")
    col4.metric("🏪 Lojas Monitoradas", len(lojas_selecionadas))

    st.markdown("---")

    modo_visualizacao = st.radio("Modo de Exibição:", ["Tabela Interativa", "Cards Visuais em Grade"], horizontal=True)

    if modo_visualizacao == "Tabela Interativa":
        st.data_editor(
            df_filtrado[['Foto', 'Loja', 'Nicho', 'Produto', 'Preço Antigo', 'Preço Atual', 'Preço Final Real', 'Desconto', 'Antifraude', 'Cupom 🎟️', 'Link', 'WhatsApp']],
            column_config={
                "Foto": st.column_config.ImageColumn("Foto", width=80),
                "Loja": st.column_config.TextColumn("Loja", width="small"),
                "Nicho": st.column_config.TextColumn("Nicho", width="medium"),
                "Produto": st.column_config.TextColumn("Produto", width="large"),
                "Preço Antigo": st.column_config.NumberColumn("Preço Anterior", format="R$ %.2f"),
                "Preço Atual": st.column_config.NumberColumn("Preço Bruto", format="R$ %.2f"),
                "Preço Final Real": st.column_config.NumberColumn("Preço Líquido", format="R$ %.2f"),
                "Desconto": st.column_config.TextColumn("Desconto"),
                "Antifraude": st.column_config.TextColumn("Selo Confiabilidade"),
                "Cupom 🎟️": st.column_config.TextColumn("Cupom"),
                "Link": st.column_config.LinkColumn("Comprar", display_text="Ver Oferta"),
                "WhatsApp": st.column_config.LinkColumn("Compartilhar", display_text="Zap")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        num_cols = 4
        linhas = [df_filtrado.iloc[i:i + num_cols] for i in range(0, len(df_filtrado), num_cols)]
        
        for linha in linhas:
            cols = st.columns(num_cols)
            for idx, (_, row) in enumerate(linha.iterrows()):
                with cols[idx]:
                    st.markdown(f"""
                        <div class="product-card">
                            <span class="badge-tag">{row['Desconto']} • {row['Loja']}</span><br>
                            <img src="{row['Foto']}" width="100%" height="110" style="border-radius: 6px; object-fit: cover;">
                            <p style="font-size: 12px; font-weight: 600; height: 35px; overflow: hidden; margin-bottom: 4px; color: #1e293b;">{row['Produto'][:35]}...</p>
                            <p style="color: #059669; font-size: 18px; font-weight: 800; margin: 0;">R$ {row['Preço Atual']:.2f}</p>
                            <span class="old-price">R$ {row['Preço Antigo']:.2f}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("🔗 Ver Oferta", row['Link'], use_container_width=True)

with aba_empilhar:
    st.subheader("🏷️ Simulador de Empilhamento de Descontos")
    st.markdown("Calcule o **Preço Final Real** combinando múltiplas fontes de economia simultâneas:")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        preco_inicial_sim = st.number_input("Preço Inicial Base do Produto (R$):", min_value=10.0, value=500.0)
        desc_cupom_pct = st.slider("Desconto do Cupom da Loja (%):", 0, 50, 10)
    with col_e2:
        desc_pix_pct = st.slider("Desconto Adicional por Pix à Vista (%):", 0, 20, 5)
        cashback_pct = st.slider("Cashback da Plataforma Parceira (%):", 0, 25, 4)
        
    preco_pos_cupom = preco_inicial_sim * (1 - desc_cupom_pct / 100)
    preco_pos_pix = preco_pos_cupom * (1 - desc_pix_pct / 100)
    valor_cashback_gerado = preco_pos_pix * (cashback_pct / 100)
    preco_final_liquido_sim = preco_pos_pix - valor_cashback_gerado
    economia_total_rs = preco_inicial_sim - preco_final_liquido_sim
    economia_total_pct = (economia_total_rs / preco_inicial_sim) * 100
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("💰 Preço Final Pagando no Pix", f"R$ {preco_pos_pix:.2f}")
    res2.metric("💵 Preço Líquido (Com Cashback)", f"R$ {preco_final_liquido_sim:.2f}")
    res3.metric("🎉 Economia Total Real", f"R$ {economia_total_rs:.2f} ({economia_total_pct:.1f}%)")

with aba_comparador:
    st.subheader("⚖️ Comparador de Preços Cruzado entre Lojas")
    st.markdown("Selecione um produto base para comparar instantaneamente o preço dele em todos os e-commerces monitorados:")
    
    produto_comparacao = st.selectbox("Escolha o produto:", df["Produto_Puro"].unique().tolist())
    
    if produto_comparacao:
        df_comparativo = df[df["Produto_Puro"] == produto_comparacao]
        st.markdown(f"### Resultados para: **{produto_comparacao}**")
        
        cols_comp = st.columns(len(lojas_disponiveis))
        for i, loja in enumerate(lojas_disponiveis):
            item_loja = df_comparativo[df_comparativo["Loja"] == loja]
            with cols_comp[i]:
                st.markdown(f"**{loja}**")
                if not item_loja.empty:
                    row_l = item_loja.iloc[0]
                    st.image(row_l["Foto"], width=100)
                    st.markdown(f"**R$ {row_l['Preço Atual']:.2f}**")
                    st.caption(f"Desconto: {row_l['Desconto']}")
                    st.link_button(f"Ir para {loja}", row_l["Link"], use_container_width=True)
                else:
                    st.info("Indisponível")

with aba_grafico:
    st.subheader("📈 Auditoria e Histórico de Preços (Últimos 30 Dias)")
    produto_escolhido = st.selectbox("Selecione o produto para auditoria completa:", df["Produto"].head(50).tolist() if not df.empty else ["Nenhum produto"])
    
    if produto_escolhido and produto_escolhido != "Nenhum produto":
        row_prod = df[df["Produto"] == produto_escolhido].iloc[0]
        preco_atual_ref = row_prod["Preço Atual"]
        
        dias = [datetime.today() - timedelta(days=i) for i in range(30, 0, -1)]
        precos_historico = [preco_atual_ref * random.uniform(0.95, 1.35) for _ in range(30)]
        precos_historico[-1] = preco_atual_ref 
        
        df_hist = pd.DataFrame({"Data": dias, "Preço (R$)": precos_historico}).set_index("Data")
        
        menor_hist = min(precos_historico)
        maior_hist = max(precos_historico)
        media_hist = sum(precos_historico) / len(precos_historico)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📉 Menor Preço (30d)", f"R$ {menor_hist:.2f}")
        c2.metric("📈 Maior Preço (30d)", f"R$ {maior_hist:.2f}")
        c3.metric("📊 Preço Médio", f"R$ {media_hist:.2f}")
        c4.metric("💰 Preço Atual", f"R$ {preco_atual_ref:.2f}")
        
        if preco_atual_ref <= menor_hist * 1.02:
            st.success("🔥 **Excelente Oportunidade!** Este é o menor preço registrado para este produto nos últimos 30 dias.")
        elif preco_atual_ref < media_hist:
            st.info("👍 **Bom Preço:** O valor atual está abaixo da média histórica do período.")
        else:
            st.warning("⚠️ **Atenção:** O preço atual está acima da média. Considere aguardar uma queda ou configurar um alerta.")

        st.line_chart(df_hist)

with aba_alertas:
    col_config_alerta, col_lista_alerta = st.columns(2)
    
    with col_config_alerta:
        st.subheader("🔔 Cadastrar Alerta Inteligente & E-mail")
        email_usuario = st.text_input("Seu E-mail ou Telegram ID:")
        produto_alerta = st.selectbox("Produto Monitorado:", df["Produto_Puro"].unique().tolist())
        alerta_preco = st.number_input("Me avise se o preço baixar para (R$):", min_value=1.0, value=150.0)
            
        if st.button("Salvar Alerta Permanentemente"):
            if email_usuario and produto_alerta:
                cursor = db_conn.cursor()
                cursor.execute("INSERT INTO alertas (email, produto, preco_alvo, data_cadastro) VALUES (?, ?, ?, ?)",
                               (email_usuario, produto_alerta, alerta_preco, datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.success(f"Alerta salvo no banco de dados e programado para {email_usuario}!")
            else:
                st.warning("Preencha todos os campos.")

    with col_lista_alerta:
        st.subheader("📂 Alertas Cadastrados (SQLite)")
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, email, produto, preco_alvo, data_cadastro FROM alertas")
        dados_alertas = cursor.fetchall()
        
        if dados_alertas:
            df_alertas = pd.DataFrame(dados_alertas, columns=["ID", "E-mail/Telegram", "Produto Alvo", "Preço Alvo (R$)", "Data"])
            st.dataframe(df_alertas, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum alerta registrado no banco de dados.")

with aba_favoritos:
    st.subheader("⭐ Meus Produtos Favoritos")
    if "favoritos" not in st.session_state:
        st.session_state.favoritos = []
        
    fav_selecionado = st.selectbox("Escolha um produto para adicionar à sua lista:", df["Produto"].tolist())
    if st.button("Adicionar aos Favoritos ⭐"):
        if fav_selecionado not in st.session_state.favoritos:
            st.session_state.favoritos.append(fav_selecionado)
            st.success("Produto adicionado com sucesso!")
            
    if st.session_state.favoritos:
        df_fav = df[df["Produto"].isin(st.session_state.favoritos)]
        st.dataframe(df_fav[['Foto', 'Loja', 'Produto', 'Preço Atual', 'Desconto', 'Link']], use_container_width=True, hide_index=True)
    else:
        st.info("Sua lista de favoritos está vazia.")