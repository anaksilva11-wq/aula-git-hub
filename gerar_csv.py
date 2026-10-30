import pandas as pd
import random

# Fixando a semente para gerar os mesmos valores aleatórios sempre que rodar
random.seed(42)

quantidade = 10000

dados = []

for i in range(1, quantidade + 1):
    # Gerando valores numéricos aleatórios para as 4 primeiras colunas
    # Evitamos o 0 na coluna D para não dar erro matemático de divisão por zero
    val_a = random.randint(1, 50)
    val_b = random.randint(1, 20)
    val_c = random.randint(1, 100)
    val_d = random.randint(1, 15)  # Valores de 1 a 15 para D
    
    # Aplicando a lógica do sistema: (A * B + C) / D
    val_e = (val_a * val_b + val_c) / val_d

    dados.append({
        "A": val_a,
        "B": val_b,
        "C": val_c,
        "D": val_d,
        "E": round(val_e, 2)  # Arredondando para 2 casas decimais
    })

# Criando o DataFrame do Pandas
df = pd.DataFrame(dados)

# Salvando em formato CSV compatível com o Streamlit
nome_arquivo = "curriculos_teste.csv"
df.to_csv(
    nome_arquivo,
    index=False,
    encoding="utf-8-sig"
)

print("CSV gerado com sucesso!")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")
print(f"Arquivo salvo como: {nome_arquivo}")