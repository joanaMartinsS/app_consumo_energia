import psutil
import time
import threading
from scripts.mcohm import MCOHM

class MCal:

    # Inicializa o módulo de calibração com o MCOHM e as variáveis de resultado
    def __init__(self, mcohm):
        self.mcohm = self.mcohm
        self.coeficiente = None
        self.duracaoCalibracaoSegundos = 20

    # Estresa a CPU com cálculos matemáticos pesados para gerar leituras variadas
    def estressarCpu(self, duracaoSegundos):
        tempoFinal = time.time() + duracaoSegundos
        while time.time() < tempoFinal:
            x = 0
            for i in range(1, 100000):
                x += i ** 2.5

    # Coleta amostras de % CPU e Watts durante a calibração
    def coletarAmostras(self, duracaoSegundos):
        amostras = []
        tempoFinal = time.time() + duracaoSegundos
        while time.time() < tempoFinal:
            amostra = self.mwmi.coletarAmostra()
            amostras.append(amostra)
            time.sleep(1)
        return amostras

    # Calcula o coeficiente Watts por % de CPU a partir das amostras coletadas
    def calcularCoeficiente(self, amostras):
        leituras = [a for a in amostras if a["percentualCpu"] > 5]
        if not leituras:
            return None
        mediaWatts = sum(a["watts"] for a in leituras) / len(leituras)
        mediaCpu = sum(a["percentualCpu"] for a in leituras) / len(leituras)
        if mediaCpu == 0:
            return None
        return round(mediaWatts / mediaCpu, 4)

    # Executa o fluxo completo de calibração e retorna o coeficiente calculado
    def calibrar(self):
        print("Iniciando calibração... Por favor aguarde 20 segundos.")

        # Roda o estresse da CPU em paralelo com a coleta de amostras
        threadEstresse = threading.Thread(
            target=self.estressarCpu, args=(self.duracaoCalibracaoSegundos,)
        )
        threadEstresse.start()

        amostras = self.coletarAmostras(self.duracaoCalibracaoSegundos)
        threadEstresse.join()

        self.coeficiente = self.calcularCoeficiente(amostras)
        print(f"Calibração concluída! Coeficiente: {self.coeficiente} W/%CPU")
        return self.coeficiente


if __name__ == "__main__":
    mcohm = MCOHM()
    cal = MCal(mcohm)
    cal.calibrar()