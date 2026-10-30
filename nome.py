import pandas as pd

# Criando os dados estruturados lado a lado (linha por linha)
# A chave é o nome da coluna, e o valor é uma lista contendo o valor da linha 2
dados = {
    'A': [2],
    'B': [3],
    'C': [4],
    'D': [5],
    'E': ['=(A2*B2+C2)/D2']  # Fórmula do Excel aplicada na coluna E
}

# Criando o DataFrame
df = pd.DataFrame(dados)

# Salvando em Excel
nome_arquivo = "calculo_lado_a_lado.xlsx"
df.to_excel(nome_arquivo, index=False)

print(f"Planilha criada com sucesso! Arquivo: {nome_arquivo}")