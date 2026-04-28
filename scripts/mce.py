import time
import psutil
from playwright.sync_api import sync_playwright

class MCE:

    # Inicializa o módulo com as configurações do navegador
    def __init__(self):
        self.portaDepuracao = 9222
        self.playwright = None
        self.navegador = None
        self.contexto = None

    # Verifica se o Edge já está rodando nos processos do sistema
    def navegadorJaEstaRodando(self):
        for processo in psutil.process_iter(['name']):
            if 'msedge' in processo.info['name'].lower():
                return True
        return False

    # Abre o Microsoft Edge real com a porta de depuração ativa via Playwright
    def abrirNavegador(self):
        # Fecha qualquer instância do Edge que esteja rodando
        for processo in psutil.process_iter(['name', 'pid']):
            if 'msedge' in processo.info['name'].lower():
                try:
                    processo.kill()
                except Exception:
                    pass
        time.sleep(2)

        self.playwright = sync_playwright().start()
        self.navegador = self.playwright.chromium.launch(
            channel="msedge",
            headless=False,
            args=[
                f"--remote-debugging-port={self.portaDepuracao}",
                "--remote-allow-origins=*",
                "--no-first-run",
                "--no-default-browser-check"
            ]
        )
        self.contexto = self.navegador.new_context(viewport=None)
        print("Edge aberto com sucesso!")

    # Abre uma nova aba com a URL informada
    def abrirAba(self, url):
        pagina = self.contexto.new_page()
        pagina.goto(url)
        return pagina

    # Pega o % de CPU total do Edge via psutil
    def coletarDadosPorAba(self):
        dadosAbas = []

        
        # Primeira chamada descartada pois o psutil precisa de intervalo para medir
        percentualCpuTotal = 0
        processosEdge = [p for p in psutil.process_iter(['name', 'cpu_percent'])
                         if 'msedge' in p.info['name'].lower()]
        time.sleep(1)
        for processo in processosEdge:
            percentualCpuTotal += processo.cpu_percent()

        # Coleta o tempo de uso de cada aba pra distribuir proporcionalmente
        paginasComTempo = []
        tempoTotal = 0
        for contexto in self.navegador.contexts:
            for pagina in contexto.pages:
                try:
                    # Ignora abas que estão carregando
                    if pagina.url == "about:blank":
                        continue
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
                except Exception:
                    # Ignora abas em navegação ou com contexto destruído
                    continue

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

    # Encerra a conexão com o navegador
    def desconectar(self):
        try:
            if self.playwright:
                self.playwright.stop()
            print("Navegador encerrado!")
        except Exception:
            print("Navegador encerrado!")