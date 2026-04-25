import time
import threading
from scripts.mwmi import MWMI
from scripts.mcal import MCal
from scripts.mgc import MGC
from scripts.mee import MEE
from scripts.mah import MAH
from playwright.sync_api import sync_playwright

class MC:

    # Inicializa o controlador com todos os módulos e variáveis de estado
    def __init__(self):
        self.mwmi = None
        self.mgc = None
        self.mee = None
        self.mah = None
        self.coeficiente = None
        self.emExecucao = False
        self.threadColeta = None
        self.intervaloSegundos = 300

    # Inicializa todos os módulos do sistema
    def inicializarModulos(self):
        print("Inicializando módulos...")
        self.mwmi = MWMI()
        self.mgc = MGC()
        self.mah = MAH()
        print("Módulos inicializados!")

    # Executa a calibração, salva o coeficiente e inicia a coleta
    def executarCalibracao(self):
        print("Executando calibração...")
        mcal = MCal(self.mwmi)
        self.coeficiente = mcal.calibrar()
        self.mee = MEE(self.coeficiente)
        self.mah.salvarCoeficiente(self.coeficiente)
        self.iniciarColeta()
        print(f"Calibração concluída! Coeficiente: {self.coeficiente} W/%CPU")

    # Executa um ciclo de coleta: pega dados das abas, estima e salva
    def executarCicloDeColeta(self):
        try:
            dadosAbas = self.mgc.coletarDadosPorAba()
            if not dadosAbas:
                print("Nenhuma aba encontrada!")
                return
            resultados = self.mee.estimarConsumo(dadosAbas)
            self.mah.salvarConsumo(resultados)
            print(f"Ciclo concluído: {len(resultados)} abas coletadas")
        except Exception as erro:
            print(f"Erro no ciclo de coleta: {erro}")

    # Loop de coleta contínua executado em segundo plano a cada 5 minutos
    def loopDeColeta(self):
        # Playwright precisa ser iniciado na mesma thread que vai usá-lo
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://localhost:{self.mgc.portaDepuracao}"
            )
            self.mgc.navegador = navegador
            while self.emExecucao:
                self.executarCicloDeColeta()
                time.sleep(self.intervaloSegundos)

    # Inicia o loop de coleta em uma thread separada
    def iniciarColeta(self):
        self.emExecucao = True
        self.threadColeta = threading.Thread(target=self.loopDeColeta, daemon=True)
        self.threadColeta.start()
        print("Coleta em segundo plano iniciada!")

    # Para o loop de coleta
    def pararColeta(self):
        self.emExecucao = False
        print("Coleta encerrada!")

   # Encerra todos os módulos do sistema
    def encerrar(self):
        self.pararColeta()
        print("Sistema encerrado!")

    # Fluxo principal: inicializa módulos, verifica calibração e abre interface
    def iniciar(self):
        self.inicializarModulos()
        self.mgc.abrirChromium()
        self.mgc.abrirAba("https://www.google.com")
        
        # Verifica se já existe coeficiente salvo
        coeficienteSalvo = self.mah.buscarCoeficiente()
        if coeficienteSalvo:
            print(f"Coeficiente encontrado: {coeficienteSalvo} W/%CPU")
            self.coeficiente = coeficienteSalvo
            self.mee = MEE(self.coeficiente)
            self.iniciarColeta()
        
        self.iniciarInterface()

    # Inicia a interface gráfica conectada ao controlador
    def iniciarInterface(self):
        from scripts.mi import MI
        self.mi = MI(self)
        self.mi.iniciar()


if __name__ == "__main__":
    mc = MC()
    mc.iniciar()