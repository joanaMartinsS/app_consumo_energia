import wmi
import psutil
import time

class MWMI:

    # Inicializa o módulo e testa se o OpenHardwareMonitor está disponível
    def __init__(self):
        self.conexaoWmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        self.usarOhm = self.testarOhm()

    # Testa se o OpenHardwareMonitor está rodando e acessível via WMI
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


if __name__ == "__main__":
    print("Testando MWMI...")
    modulo = MWMI()
    print(f"Usando OpenHardwareMonitor: {modulo.usarOhm}")
    for i in range(5):
        amostra = modulo.coletarAmostra()
        print(f"Amostra {i+1}: CPU {amostra['percentualCpu']}% → {amostra['watts']}W")
        time.sleep(1)