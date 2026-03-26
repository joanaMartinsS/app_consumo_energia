import psutil
import time
import pandas as pd
from datetime import datetime

# Função que monitora o processo por um determinado tempo
def monitorar_processo(nome_processo, duracao_segundos=30):
    dados = []
    print(f"--- Monitorando: {nome_processo} por {duracao_segundos}s ---")
    
    # Tenta encontrar o processo pelo nome
    processos = [p for p in psutil.process_iter(['name']) if nome_processo.lower() in p.info['name'].lower()]
    
    # Erro caso o processo não esteja funcionando
    if not processos:
        print(f"❌ Processo '{nome_processo}' não encontrado. Certifique-se de que ele está aberto.")
        return

    proc = processos[0] # Pega a primeira instância encontrada
    pid = proc.pid
    print(f"✅ Monitorando PID: {pid} ({proc.info['name']})")

    try:
        for _ in range(duracao_segundos):
            # Captura métricas específicas do processo
            with proc.oneshot():
                cpu = proc.cpu_percent(interval=1)
                ram = proc.memory_info().rss / (1024 * 1024) # Converte para MB
                timestamp = datetime.now().strftime("%H:%M:%S")
                
            dados.append({"hora": timestamp, "cpu_pct": cpu, "ram_mb": ram})
            print(f"[{timestamp}] CPU: {cpu}% | RAM: {ram:.2f} MB")
            
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print("Interrompido: O processo foi fechado ou o acesso foi negado.")

    # Salva o resultado
    df = pd.DataFrame(dados)
    nome_arquivo = f"data/consumo_{nome_processo}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(nome_arquivo, index=False)
    print(f"\n📊 Dados salvos em: {nome_arquivo}")

if __name__ == "__main__":
    # O
    monitorar_processo("chrome", duracao_segundos=15)