class MEE:

    # Inicializa o módulo com o coeficiente de calibração e o intervalo de coleta
    def __init__(self, coeficiente, intervaloMinutos=5):
        self.coeficiente = coeficiente
        self.intervaloHoras = intervaloMinutos / 60

    # Calcula os Watts consumidos por uma aba a partir do seu % de CPU
    def calcularWatts(self, percentualCpu):
        return round(percentualCpu * self.coeficiente, 4)

    # Calcula o kWh consumido por uma aba no intervalo de coleta
    def calcularKwh(self, watts):
        return round((watts * self.intervaloHoras) / 1000, 8)

    # Estima o consumo de energia de cada aba e retorna a lista com os resultados
    def estimarConsumo(self, dadosAbas):
        resultados = []
        for aba in dadosAbas:
            watts = self.calcularWatts(aba["percentualCpu"])
            kwh = self.calcularKwh(watts)
            resultados.append({
                "titulo": aba["titulo"],
                "url": aba["url"],
                "percentualCpu": aba["percentualCpu"],
                "watts": watts,
                "kwh": kwh
            })
        return resultados


if __name__ == "__main__":
    # Simula dados vindos do MGC e coeficiente vindo do MCal
    coeficienteSimulado = 0.6402
    dadosSimulados = [
        {"titulo": "Google", "url": "https://www.google.com", "percentualCpu": 5.62},
        {"titulo": "ChatGPT", "url": "https://chatgpt.com", "percentualCpu": 5.61},
        {"titulo": "YouTube", "url": "https://www.youtube.com", "percentualCpu": 5.57},
    ]

    mee = MEE(coeficienteSimulado)
    resultados = mee.estimarConsumo(dadosSimulados)

    print("Estimativa de consumo por aba:")
    for r in resultados:
        print(f"  - {r['titulo']}: {r['percentualCpu']}% CPU → {r['watts']}W → {r['kwh']} kWh")