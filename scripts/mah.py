import sqlite3
import os
from datetime import datetime

class MAH:

    # Inicializa o módulo criando o banco de dados e a tabela se não existirem
    def __init__(self):
        self.caminhoBanco = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dados", "historico.db"
        )
        self.criarBanco()

    # Cria a pasta dados e o banco de dados com a tabela de histórico
    def criarBanco(self):
        os.makedirs(os.path.dirname(self.caminhoBanco), exist_ok=True)
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                url TEXT NOT NULL,
                kwh REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conexao.commit()
        conexao.close()
        print(f"Banco de dados pronto em: {self.caminhoBanco}")

    # Salva o consumo estimado de cada aba no banco de dados
    def salvarConsumo(self, resultados):
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for resultado in resultados:
            cursor.execute("""
                INSERT INTO historico (site, url, kwh, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                resultado["titulo"],
                resultado["url"],
                resultado["kwh"],
                timestamp
            ))
        conexao.commit()
        conexao.close()
        print(f"Consumo de {len(resultados)} abas salvo em {timestamp}")

    # Busca o histórico de consumo filtrado por período em dias
    def buscarHistorico(self, diasAtras=7):
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT site, url, kwh, timestamp
            FROM historico
            WHERE timestamp >= datetime('now', ?)
            ORDER BY timestamp DESC
        """, (f"-{diasAtras} days",))
        registros = cursor.fetchall()
        conexao.close()
        return registros

    # Busca o ranking dos sites que mais consumiram energia no período
    def buscarRanking(self, diasAtras=7):
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT site, url, SUM(kwh) as totalKwh
            FROM historico
            WHERE timestamp >= datetime('now', ?)
            GROUP BY url
            ORDER BY totalKwh DESC
        """, (f"-{diasAtras} days",))
        ranking = cursor.fetchall()
        conexao.close()
        return ranking

    # Salva o coeficiente de calibração no banco
    def salvarCoeficiente(self, coeficiente):
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO configuracoes (chave, valor)
            VALUES ('coeficiente', ?)
        """, (str(coeficiente),))
        conexao.commit()
        conexao.close()

    # Busca o coeficiente de calibração salvo, retorna None se não existir
    def buscarCoeficiente(self):
        try:
            conexao = sqlite3.connect(self.caminhoBanco)
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'coeficiente'")
            resultado = cursor.fetchone()
            conexao.close()
            return float(resultado[0]) if resultado else None
        except Exception:
            return None

    # Busca o ranking de consumo filtrado por data de início e fim
    def buscarRankingPorPeriodo(self, dataInicio, dataFim):
        conexao = sqlite3.connect(self.caminhoBanco)
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT site, url, SUM(kwh) as totalKwh
            FROM historico
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY url
            ORDER BY totalKwh DESC
        """, (dataInicio, dataFim + " 23:59:59"))
        ranking = cursor.fetchall()
        conexao.close()
        return ranking

if __name__ == "__main__":
    mah = MAH()

    # Simula dados vindos do MEE para testar o salvamento
    resultadosSimulados = [
        {"titulo": "Google", "url": "https://www.google.com", "kwh": 0.00029982},
        {"titulo": "ChatGPT", "url": "https://chatgpt.com", "kwh": 0.00029929},
        {"titulo": "YouTube", "url": "https://www.youtube.com", "kwh": 0.00029716},
    ]

    mah.salvarConsumo(resultadosSimulados)

    print("\nRanking da semana:")
    ranking = mah.buscarRanking()
    for i, (site, url, totalKwh) in enumerate(ranking, 1):
        print(f"  {i}. {site}: {totalKwh:.8f} kWh")

    print("\nHistórico dos últimos 7 dias:")
    historico = mah.buscarHistorico()
    for site, url, kwh, timestamp in historico:
        print(f"  - {timestamp} | {site}: {kwh:.8f} kWh")