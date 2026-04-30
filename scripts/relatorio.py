import sqlite3
import os
import tkinter as tk
from PIL import ImageGrab

# Caminho do banco de dados
caminhoBanco = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dados", "historico.db"
)

# Busca e imprime o coeficiente de calibração
def imprimirCoeficiente():
    conexao = sqlite3.connect(caminhoBanco)
    cursor = conexao.cursor()
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'coeficiente'")
    resultado = cursor.fetchone()
    conexao.close()
    if resultado:
        print(f"\n=== CALIBRAÇÃO ===")
        print(f"Coeficiente: {resultado[0]} W/%CPU")
        print(f"Significa: para cada 1% de CPU usada, esta máquina consome {resultado[0]} Watts")

# Busca e imprime os principais dados coletados
def imprimirDadosColetados():
    conexao = sqlite3.connect(caminhoBanco)
    cursor = conexao.cursor()

    # Total de amostras
    cursor.execute("SELECT COUNT(*) FROM historico")
    totalAmostras = cursor.fetchone()[0]

    # Total de kWh acumulado
    cursor.execute("SELECT SUM(kwh) FROM historico")
    totalKwh = cursor.fetchone()[0]

    # Ranking geral
    cursor.execute("""
        SELECT site, url, SUM(kwh) as totalKwh
        FROM historico
        GROUP BY url
        ORDER BY totalKwh DESC
        LIMIT 10
    """)
    ranking = cursor.fetchall()

    # Primeira e última coleta
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM historico")
    primeiraColeta, ultimaColeta = cursor.fetchone()

    conexao.close()

    print(f"\n=== DADOS COLETADOS ===")
    print(f"Total de amostras coletadas: {totalAmostras}")
    print(f"Total de kWh acumulado: {totalKwh:.8f} kWh")
    print(f"Primeira coleta: {primeiraColeta}")
    print(f"Última coleta: {ultimaColeta}")

    print(f"\n=== RANKING GERAL (todos os dados) ===")
    for i, (site, url, totalKwh) in enumerate(ranking, 1):
        print(f"  {i}. {site}: {totalKwh:.8f} kWh")
        print(f"     {url}")

if __name__ == "__main__":
    imprimirCoeficiente()
    imprimirDadosColetados()