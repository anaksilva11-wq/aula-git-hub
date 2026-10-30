
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Analisador de Currículos",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Analisador de Currículos")
st.write(
    "Envie um arquivo CSV para visualizar os currículos, "
    "gerar quatro gráficos e converter os dados para JSON."
)

arquivo = st.file_uploader(
    "Envie seu arquivo CSV",
    type=["csv"]
)


def ler_csv(arquivo):
    """Lê o CSV tentando detectar o separador e a codificação."""
    conteudo = arquivo.getvalue()

    for encoding in ["utf-8-sig", "latin-1"]:
        try:
            from io import BytesIO

            return pd.read_csv(
                BytesIO(conteudo),
                sep=None,
                engine="python",
                encoding=encoding,
                dtype=str,
                keep_default_na=False
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("Não foi possível ler o arquivo CSV.")


def gerar_frequencia(df, coluna):
    """Conta as categorias mais frequentes de uma coluna."""
    valores = df[coluna].astype(str).str.strip()
    valores = valores[valores != ""]

    # Divide habilidades separadas por vírgulas ou ponto e vírgula
    valores = valores.str.split(r"[,;]")
    valores = valores.explode().str.strip()
    valores = valores[valores != ""]

    return valores.value_counts().head(10)


if arquivo is not None:
    try:
        df = ler_csv(arquivo)

        if len(df.columns) == 0:
            st.warning("O arquivo não contém colunas.")
            st.stop()

        st.success("Arquivo carregado com sucesso!")

        # Indicadores gerais
        col1, col2, col3 = st.columns(3)

        col1.metric("Registros", len(df))
        col2.metric("Colunas", len(df.columns))
        col3.metric(
            "Campos preenchidos",
            int(df.astype(str).apply(
                lambda coluna: coluna.str.strip().ne("")
            ).sum().sum())
        )

        # Visualização dos dados
        st.subheader("📋 Dados dos currículos")
        st.dataframe(df, use_container_width=True)

        colunas = list(df.columns)

        st.divider()
        st.subheader("📊 Gráficos dos currículos")

        # GRÁFICO 1 — PIZZA
        st.markdown("### 🥧 Gráfico 1 — Distribuição por categoria")

        campo1 = st.selectbox(
            "Escolha a coluna para o gráfico de pizza",
            colunas,
            key="pizza"
        )

        freq1 = gerar_frequencia(df, campo1)

        if not freq1.empty:
            pizza = pd.DataFrame({
                "Categoria": freq1.index,
                "Quantidade": freq1.values
            })

            st.vega_lite_chart(
                pizza,
                {
                    "mark": {
                        "type": "arc",
                        "tooltip": True
                    },
                    "encoding": {
                        "theta": {
                            "field": "Quantidade",
                            "type": "quantitative"
                        },
                        "color": {
                            "field": "Categoria",
                            "type": "nominal",
                            "legend": {"title": "Categorias"}
                        },
                        "tooltip": [
                            {
                                "field": "Categoria",
                                "type": "nominal"
                            },
                            {
                                "field": "Quantidade",
                                "type": "quantitative"
                            }
                        ]
                    },
                    "view": {"stroke": None}
                },
                use_container_width=True
            )
        else:
            st.info("Não há dados para este gráfico.")

        # GRÁFICO 2 — BARRAS VERTICAIS
        st.markdown("### 📊 Gráfico 2 — Barras verticais")

        campo2 = st.selectbox(
            "Escolha a coluna para o gráfico de barras",
            colunas,
            key="barras"
        )

        freq2 = gerar_frequencia(df, campo2)

        if not freq2.empty:
            barras = freq2.rename_axis(
                "Categoria"
            ).reset_index(name="Quantidade")

            st.vega_lite_chart(
                barras,
                {
                    "mark": {
                        "type": "bar",
                        "tooltip": True
                    },
                    "encoding": {
                        "x": {
                            "field": "Categoria",
                            "type": "nominal",
                            "sort": "-y",
                            "axis": {"labelAngle": -45}
                        },
                        "y": {
                            "field": "Quantidade",
                            "type": "quantitative",
                            "title": "Quantidade"
                        },
                        "tooltip": [
                            {
                                "field": "Categoria",
                                "type": "nominal"
                            },
                            {
                                "field": "Quantidade",
                                "type": "quantitative"
                            }
                        ]
                    }
                },
                use_container_width=True
            )
        else:
            st.info("Não há dados para este gráfico.")

        # GRÁFICO 3 — LINHA
        st.markdown("### 📈 Gráfico 3 — Linha")

        campo3 = st.selectbox(
            "Escolha a coluna para o gráfico de linha",
            colunas,
            key="linha"
        )

        freq3 = gerar_frequencia(df, campo3)

        if not freq3.empty:
            linha = freq3.rename_axis(
                "Categoria"
            ).reset_index(name="Quantidade")

            st.vega_lite_chart(
                linha,
                {
                    "mark": {
                        "type": "line",
                        "point": True,
                        "tooltip": True
                    },
                    "encoding": {
                        "x": {
                            "field": "Categoria",
                            "type": "ordinal",
                            "axis": {"labelAngle": -45}
                        },
                        "y": {
                            "field": "Quantidade",
                            "type": "quantitative",
                            "title": "Quantidade"
                        },
                        "tooltip": [
                            {
                                "field": "Categoria",
                                "type": "ordinal"
                            },
                            {
                                "field": "Quantidade",
                                "type": "quantitative"
                            }
                        ]
                    }
                },
                use_container_width=True
            )
        else:
            st.info("Não há dados para este gráfico.")

        # GRÁFICO 4 — ÁREA
        st.markdown("### 📉 Gráfico 4 — Área")

        campo4 = st.selectbox(
            "Escolha a coluna para o gráfico de área",
            colunas,
            key="area"
        )

        freq4 = gerar_frequencia(df, campo4)

        if not freq4.empty:
            area = freq4.rename_axis(
                "Categoria"
            ).reset_index(name="Quantidade")

            st.vega_lite_chart(
                area,
                {
                    "mark": {
                        "type": "area",
                        "point": True,
                        "tooltip": True
                    },
                    "encoding": {
                        "x": {
                            "field": "Categoria",
                            "type": "ordinal",
                            "axis": {"labelAngle": -45}
                        },
                        "y": {
                            "field": "Quantidade",
                            "type": "quantitative",
                            "title": "Quantidade"
                        },
                        "tooltip": [
                            {
                                "field": "Categoria",
                                "type": "ordinal"
                            },
                            {
                                "field": "Quantidade",
                                "type": "quantitative"
                            }
                        ]
                    }
                },
                use_container_width=True
            )
        else:
            st.info("Não há dados para este gráfico.")

        # CONVERSÃO PARA JSON
        st.divider()
        st.subheader("🗂️ Converter para JSON")

        dados_json = df.to_json(
            orient="records",
            indent=2,
            force_ascii=False
        )

        st.download_button(
            label="⬇️ Baixar arquivo JSON",
            data=dados_json.encode("utf-8"),
            file_name=arquivo.name.rsplit(".", 1)[0] + ".json",
            mime="application/json"
        )

    except pd.errors.EmptyDataError:
        st.error("O arquivo CSV está vazio.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Faça upload de um arquivo CSV para começar.")
