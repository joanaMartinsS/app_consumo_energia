import wmi
import psutil
import time
import os
import ctypes

class MWMI:

    # Inicializa o módulo, abre o OHM se necessário e testa a conexão
    def __init__(self):
        self.caminhoOhm = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "ferramentas", "openHardwareMonitor", "OpenHardwareMonitor.exe"
        )
        self.abrirOhm()
        time.sleep(3)
        self.conexaoWmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        self.usarOhm = self.testarOhm()

    # Verifica se o OpenHardwareMonitor já está rodando nos processos do sistema
    def ohmJaEstaRodando(self):
        for processo in psutil.process_iter(['name']):
            if 'OpenHardwareMonitor' in processo.info['name']:
                return True
        return False

    # Abre o OpenHardwareMonitor com privilégios de administrador apenas se não estiver rodando
    def abrirOhm(self):
        if self.ohmJaEstaRodando():
            print("OHM já está rodando!")
            return
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", self.caminhoOhm, None, None, 1
            )
            print("OHM aberto com sucesso!")
        except Exception as erro:
            print(f"Erro ao abrir o OpenHardwareMonitor: {erro}")

    # Testa se o OpenHardwareMonitor está acessível via WMI e retorna True ou False
    def testarOhm(self):
        try:
            sensores = self.conexaoWmi.Sensor()
            return len(sensores) > 0
        except Exception:
            return False

    # Retorna o consumo atual da CPU em Watts
    # Se o OpenHardwareMonitor não estiver disponível, estima via psutil
    def coletarWatts(self):
        if self.usarOhm:
            return self.wattsViaOhm()
        else:
            return self.wattsViaPsutil()

    # Lê os Watts diretamente do OpenHardwareMonitor via WMI
    def wattsViaOhm(self):
        try:
            sensores = self.conexaoWmi.Sensor()
            for sensor in sensores:
                if sensor.SensorType == "Power" and "CPU" in sensor.Name:
                    return float(sensor.Value)
        except Exception:
            pass
        return self.wattsViaPsutil()

    # Estima os Watts a partir do percentual de uso da CPU
    # Faixa típica: ocioso ~15W, carga máxima ~65W
    def wattsViaPsutil(self):
        percentualCpu = psutil.cpu_percent(interval=1)
        wattsOcioso = 15.0
        wattsMaximo = 65.0
        wattsEstimado = wattsOcioso + (wattsMaximo - wattsOcioso) * (percentualCpu / 100.0)
        return round(wattsEstimado, 2)

    # Coleta e retorna o percentual de CPU e os Watts no momento atual
    def coletarAmostra(self):
        percentualCpu = psutil.cpu_percent(interval=1)
        watts = self.coletarWatts()
        return {
            "percentualCpu": percentualCpu,
            "watts": watts
        }

    # Adiciona a pasta do OHM nas exceções do Windows Defender via PowerShell
    def adicionarExcecaoDefender(self):
        pastaOhm = os.path.dirname(self.caminhoOhm)
        try:
            subprocess.run(
                ["powershell", "-Command", 
                f"Add-MpPreference -ExclusionPath '{pastaOhm}'"],
                capture_output=True
            )
            print("Exceção do Windows Defender adicionada!")
        except Exception as erro:
            print(f"Erro ao adicionar exceção: {erro}")
            
# Inicializa o módulo, abre o OHM com admin e testa a conexão
def __init__(self):
    self.caminhoOhm = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "ferramentas", "openHardwareMonitor", "OpenHardwareMonitor.exe"
    )
    self.adicionarExcecaoDefender()
    self.abrirOhm()
    time.sleep(3)
    self.conexaoWmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
    self.usarOhm = self.testarOhm()