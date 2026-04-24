import time
import psutil
from playwright.sync_api import sync_playwright

class MGC:

    # Inicializa o módulo com as configurações do Chromium
    def __init__(self):
        self.portaDepuracao = 9222
        self.playwright = None
        self.navegador = None
        self.contexto = None

    # Verifica se o Chromium já está rodando nos processos do sistema
    def chromiumJaEstaRodando(self):
        for processo in psutil.process_iter(['name']):
            if 'chromium' in processo.info['name'].lower():
                return True
        return False

    # Abre o Chromium com a porta de depuração ativa para comunicação via CDP
    def abrirChromium(self):
        if self.chromiumJaEstaRodando():
            print("Chromium já está rodando!")
            return
        self.playwright = sync_playwright().start()
        self.navegador = self.playwright.chromium.launch(
            headless=False,
            args=[
                f"--remote-debugging-port={self.portaDepuracao}",
                "--remote-allow-origins=*"
            ]
        )
        self.contexto = self.navegador.new_context()
        print("Chromium aberto com sucesso!")

    # Abre uma nova aba com a URL informada
    def abrirAba(self, url):
        pagina = self.contexto.new_page()
        pagina.goto(url)
        return pagina

    # Coleta o % de CPU de cada aba aberta via CDP
    def coletarDadosPorAba(self):
        dadosAbas = []

        # Pega o % de CPU total do Chromium via psutil
        # Primeira chamada descartada pois o psutil precisa de intervalo para medir
        percentualCpuTotal = 0
        processosChromiun = [p for p in psutil.process_iter(['name', 'cpu_percent']) 
                            if p.info['name'].lower() == 'chrome.exe']
        time.sleep(1)
        for processo in processosChromiun:
            percentualCpuTotal += processo.cpu_percent()

        # Coleta o tempo de uso de cada aba via CDP pra distribuir proporcionalmente
        paginasComTempo = []
        tempoTotal = 0
        for contexto in self.navegador.contexts:
            for pagina in contexto.pages:
                try:
                    # Coleta o tempo acumulado de CPU da aba via performance API
                    tempoCpu = pagina.evaluate("""
                        () => {
                            const entries = performance.getEntriesByType('navigation');
                            if (entries.length > 0) {
                                return entries[0].duration + performance.now();
                            }
                            return performance.now();
                        }
                    """)
                    paginasComTempo.append({
                        "titulo": pagina.title(),
                        "url": pagina.url,
                        "tempoCpu": tempoCpu
                    })
                    tempoTotal += tempoCpu
                except Exception as erro:
                    print(f"Erro ao coletar dados da aba {pagina.url}: {erro}")

        # Distribui o % de CPU total proporcionalmente entre as abas
        for pagina in paginasComTempo:
            if tempoTotal > 0:
                proporcao = pagina["tempoCpu"] / tempoTotal
            else:
                proporcao = 1 / len(paginasComTempo) if paginasComTempo else 0
            dadosAbas.append({
                "titulo": pagina["titulo"],
                "url": pagina["url"],
                "percentualCpu": round(percentualCpuTotal * proporcao, 2)
            })

        return dadosAbas

    # Encerra a conexão com o Chromium
    def desconectar(self):
        try:
            if self.playwright:
                self.playwright.stop()
            print("Chromium encerrado!")
        except Exception:
            print("Chromium encerrado!")


if __name__ == "__main__":
    mgc = MGC()
    mgc.abrirChromium()

    mgc.abrirAba("https://www.google.com")
    mgc.abrirAba("https://chatgpt.com")
    mgc.abrirAba("https://www.youtube.com")

    print("Chromium aberto! Pressione Enter para coletar dados...")
    input()

    print("\nDados por aba:")
    dados = mgc.coletarDadosPorAba()
    for dado in dados:
        print(f"  - {dado['titulo']} → {dado['url']}: {dado['percentualCpu']}% CPU")

    mgc.desconectar()