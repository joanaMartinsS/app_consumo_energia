import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

class MI:

    # Inicializa a interface com o controlador e configura a janela principal
    def __init__(self, mc):
        self.mc = mc
        self.janela = tk.Tk()
        self.janela.title("Watts por Site")
        self.janela.geometry("1100x700")
        self.janela.configure(bg="#FFFFFF")
        self.janela.resizable(False, False)

        self.framePrincipal = None
        self.configurarLayout()
        self.mostrarInicio()

    # Configura o layout base com sidebar e área principal
    def configurarLayout(self):
        # Sidebar cinza à esquerda
        self.sidebar = tk.Frame(self.janela, bg="#F0F0F0", width=100)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo no topo da sidebar
        labelLogo = tk.Label(self.sidebar, text="W", bg="#CCCCCC",
                             font=("Arial", 18, "bold"), width=3, height=2)
        labelLogo.pack(pady=(20, 30), padx=20)

        # Botões de navegação da sidebar
        self.botaoInicio = tk.Button(
            self.sidebar, text="🏠\nInício", bg="#F0F0F0", relief="flat",
            font=("Arial", 9), command=self.mostrarInicio, cursor="hand2"
        )
        self.botaoInicio.pack(pady=5, padx=10, fill="x")

        self.botaoCalibragem = tk.Button(
            self.sidebar, text="🔄\nCalibragem", bg="#F0F0F0", relief="flat",
            font=("Arial", 9), command=self.mostrarCalibragem, cursor="hand2"
        )
        self.botaoCalibragem.pack(pady=5, padx=10, fill="x")

        self.botaoHistorico = tk.Button(
            self.sidebar, text="📊\nHistórico", bg="#F0F0F0", relief="flat",
            font=("Arial", 9), command=self.mostrarHistorico, cursor="hand2"
        )
        self.botaoHistorico.pack(pady=5, padx=10, fill="x")

        # Área principal branca à direita
        self.areaPrincipal = tk.Frame(self.janela, bg="#FFFFFF")
        self.areaPrincipal.pack(side="left", fill="both", expand=True)

    # Limpa a área principal para trocar de tela
    def limparAreaPrincipal(self):
        for widget in self.areaPrincipal.winfo_children():
            widget.destroy()

    # Destaca o botão da tela ativa na sidebar
    def destacarBotao(self, botaoAtivo):
        for botao in [self.botaoInicio, self.botaoCalibragem, self.botaoHistorico]:
            botao.configure(bg="#F0F0F0")
        botaoAtivo.configure(bg="#D8F5D8")

    # Cria uma barra de progresso colorida com valor e label
    def criarBarra(self, parent, label, valor, maximo, cor):
        frameItem = tk.Frame(parent, bg="#FFFFFF")
        frameItem.pack(fill="x", pady=2)

        tk.Label(frameItem, text=label, bg="#FFFFFF",
                 font=("Arial", 9), anchor="w").pack(fill="x")

        frameBarra = tk.Frame(frameItem, bg="#E0E0E0", height=22)
        frameBarra.pack(fill="x")
        frameBarra.pack_propagate(False)

        proporcao = min(valor / maximo, 1.0) if maximo > 0 else 0
        larguraBarra = int(proporcao * 700)

        if larguraBarra > 0:
            framePreenchimento = tk.Frame(frameBarra, bg=cor, height=22)
            framePreenchimento.place(x=0, y=0, width=larguraBarra, height=22)

        textoValor = f"{valor:.1f}%" if "CPU" in label else f"{valor:.6f} kWh"
        tk.Label(frameBarra, text=textoValor, bg=cor if larguraBarra > 50 else "#E0E0E0",
                 font=("Arial", 9, "bold"), anchor="w").place(x=5, y=2)

    # Exibe a tela inicial com os sites em uso agora
    def mostrarInicio(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoInicio)

        # Se não tiver coeficiente, redireciona pra calibragem
        if not self.mc.coeficiente:
            self.mostrarCalibragem()
            return


        # Cabeçalho
        tk.Label(self.areaPrincipal, text="Watts por Site", bg="#FFFFFF",
                 font=("Arial", 24, "bold"), anchor="w").pack(padx=30, pady=(30, 5), fill="x")
        tk.Label(self.areaPrincipal, text="Veja quanto cada site aberto consome de energia no seu computador.",
                 bg="#FFFFFF", font=("Arial", 11), anchor="w", wraplength=700).pack(padx=30, fill="x")

        tk.Label(self.areaPrincipal, text="Sites em uso agora", bg="#FFFFFF",
                 font=("Arial", 16, "bold"), anchor="w").pack(padx=30, pady=(30, 10), fill="x")

        # Frame com scroll para lista de sites
        frameScroll = tk.Frame(self.areaPrincipal, bg="#FFFFFF")
        frameScroll.pack(padx=30, fill="both", expand=True)

        canvas = tk.Canvas(frameScroll, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frameScroll, orient="vertical", command=canvas.yview)
        frameLista = tk.Frame(canvas, bg="#FFFFFF")

        frameLista.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frameLista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Busca dados reais do banco
        dadosAtuais = self.mc.mah.buscarRanking(diasAtras=1) if self.mc.mah else []

        if not dadosAtuais:
            tk.Label(frameLista, text="Nenhum dado coletado ainda. Aguarde a próxima coleta.",
                     bg="#FFFFFF", font=("Arial", 11), fg="#888888").pack(pady=20)
        else:
            maxKwh = max(r[2] for r in dadosAtuais) if dadosAtuais else 1
            for site, url, totalKwh in dadosAtuais:
                frameSite = tk.Frame(frameLista, bg="#FFFFFF")
                frameSite.pack(fill="x", pady=10)

                tk.Label(frameSite, text=site[:30], bg="#FFFFFF",
                         font=("Arial", 11, "bold"), anchor="w").pack(fill="x")
                self.criarBarra(frameSite, "kWh consumidos", totalKwh, maxKwh, "#4AE54A")

        # Botão de atualizar
        tk.Button(self.areaPrincipal, text="🔄 Atualizar", bg="#4AE54A",
                  font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.mostrarInicio).pack(pady=10)

    # Exibe a tela de calibragem
    def mostrarCalibragem(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoCalibragem)

        tk.Label(self.areaPrincipal, text="Calibragem", bg="#FFFFFF",
                 font=("Arial", 24, "bold"), anchor="w").pack(padx=30, pady=(30, 20), fill="x")

        textoCalibragem = (
            "A calibragem permite que o aplicativo entenda com mais precisão como seu "
            "computador consome energia enquanto você navega. Esse processo ajusta os "
            "parâmetros internos de medição para que os resultados apresentados sejam "
            "mais confiáveis e compatíveis com o seu uso real.\n\n"
            "Ao realizar a calibragem, você ajuda o sistema a identificar padrões de "
            "desempenho, estimar o consumo de CPU e energia e garantir que as análises "
            "reflitam seu cenário de navegação. Quando estiver pronto, clique no botão "
            "abaixo para iniciar a calibragem."
        )

        tk.Label(self.areaPrincipal, text=textoCalibragem, bg="#FFFFFF",
                 font=("Arial", 11), anchor="w", justify="left",
                 wraplength=750).pack(padx=30, fill="x")

        # Status da calibragem
        self.labelStatusCalibragem = tk.Label(
            self.areaPrincipal, text="", bg="#FFFFFF",
            font=("Arial", 11), fg="#555555"
        )
        self.labelStatusCalibragem.pack(pady=10)

        tk.Button(self.areaPrincipal, text="Iniciar calibragem",
                  bg="#4AE54A", font=("Arial", 13, "bold"),
                  relief="flat", cursor="hand2", padx=30, pady=12,
                  command=self.iniciarCalibragem).pack(pady=40)

    # Inicia a calibragem em thread separada para não travar a interface
    def iniciarCalibragem(self):
        self.labelStatusCalibragem.config(text="Calibrando... Por favor aguarde 20 segundos.")
        threading.Thread(target=self.executarCalibragem, daemon=True).start()

    # Executa a calibragem e exibe o popup de conclusão
    def executarCalibragem(self):
        self.mc.executarCalibracao()
        self.janela.after(0, self.mostrarPopupCalibracaoConcluida)

    # Exibe o popup verde de calibragem concluída
    def mostrarPopupCalibracaoConcluida(self):
        popup = tk.Toplevel(self.janela)
        popup.title("")
        popup.geometry("600x400")
        popup.configure(bg="#4AE54A")
        popup.resizable(False, False)

        tk.Label(popup, text="Calibragem concluída com sucesso!",
                 bg="#4AE54A", font=("Arial", 16, "bold")).pack(pady=(30, 20), padx=30)

        instrucoes = (
            "Para garantir medições mais precisas, recomendamos que você:\n\n"
            "1 - Reinicie o computador após a calibragem.\n\n"
            "2 - Deixe o app em segundo plano para que a coleta de dados continue normalmente.\n\n"
            "3 - Evite fechar o aplicativo durante o uso diário para manter as medições consistentes.\n\n"
            "Esses passos ajudam o app a registrar seu consumo de forma contínua e confiável."
        )

        tk.Label(popup, text=instrucoes, bg="#4AE54A",
                 font=("Arial", 10), justify="left", wraplength=520).pack(padx=30, fill="x")

        tk.Button(popup, text="Voltar", bg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=8,
                  command=popup.destroy).pack(pady=20)

    # Exibe a tela de histórico com ranking e filtro de datas
    def mostrarHistorico(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoHistorico)

        tk.Label(self.areaPrincipal, text="Seu consumo", bg="#FFFFFF",
                font=("Arial", 24, "bold"), anchor="w").pack(padx=30, pady=(30, 10), fill="x")

        # Frame principal dividido em lista e filtro
        frameConteudo = tk.Frame(self.areaPrincipal, bg="#FFFFFF")
        frameConteudo.pack(padx=30, fill="both", expand=True)

        # Lista de ranking à esquerda
        self.frameListaHistorico = tk.Frame(frameConteudo, bg="#FFFFFF")
        self.frameListaHistorico.pack(side="left", fill="both", expand=True)

        tk.Label(self.frameListaHistorico, text="Maior consumo semanal", bg="#FFFFFF",
                font=("Arial", 14, "bold"), anchor="w").pack(fill="x", pady=(0, 10))

        # Área com scroll para a lista
        self.canvasHistorico = tk.Canvas(self.frameListaHistorico, bg="#FFFFFF", highlightthickness=0)
        scrollbarHistorico = ttk.Scrollbar(self.frameListaHistorico, orient="vertical",
                                            command=self.canvasHistorico.yview)
        self.frameItensHistorico = tk.Frame(self.canvasHistorico, bg="#FFFFFF")

        self.frameItensHistorico.bind("<Configure>",
            lambda e: self.canvasHistorico.configure(
                scrollregion=self.canvasHistorico.bbox("all")))
        self.canvasHistorico.create_window((0, 0), window=self.frameItensHistorico, anchor="nw")
        self.canvasHistorico.configure(yscrollcommand=scrollbarHistorico.set)

        self.canvasHistorico.pack(side="left", fill="both", expand=True)
        scrollbarHistorico.pack(side="right", fill="y")

        # Filtro à direita
        frameFiltro = tk.Frame(frameConteudo, bg="#FFFFFF", width=200)
        frameFiltro.pack(side="right", fill="y", padx=(20, 0))
        frameFiltro.pack_propagate(False)

        tk.Label(frameFiltro, text="Filtro", bg="#FFFFFF",
                font=("Arial", 13, "bold"), anchor="w").pack(fill="x")
        tk.Label(frameFiltro, text="Data de início", bg="#FFFFFF",
                font=("Arial", 10), anchor="w").pack(fill="x", pady=(10, 2))

        self.entradaDataInicio = tk.Entry(frameFiltro, font=("Arial", 10),
                                        bg="#F0F0F0", relief="flat")
        self.entradaDataInicio.insert(0, "DD/MM/AAAA")
        self.entradaDataInicio.pack(fill="x", ipady=8)

        tk.Label(frameFiltro, text="Data de fim", bg="#FFFFFF",
                font=("Arial", 10), anchor="w").pack(fill="x", pady=(10, 2))

        self.entradaDataFim = tk.Entry(frameFiltro, font=("Arial", 10),
                                        bg="#F0F0F0", relief="flat")
        self.entradaDataFim.insert(0, "DD/MM/AAAA")
        self.entradaDataFim.pack(fill="x", ipady=8)

        tk.Button(frameFiltro, text="Filtrar", bg="#4AE54A",
                font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
                command=self.filtrarHistorico).pack(pady=10, fill="x")

        tk.Button(frameFiltro, text="Limpar filtro", bg="#F0F0F0",
                font=("Arial", 10), relief="flat", cursor="hand2",
                command=self.limparFiltroHistorico).pack(fill="x")

        # Carrega dados padrão da semana
        self.atualizarHistorico()

    # Aplica o filtro de data no histórico
    def filtrarHistorico(self):
        dataInicio = self.entradaDataInicio.get()
        dataFim = self.entradaDataFim.get()

        # Valida o formato das datas
        try:
            dataInicioFormatada = datetime.strptime(dataInicio, "%d/%m/%Y").strftime("%Y-%m-%d")
            dataFimFormatada = datetime.strptime(dataFim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            tk.Label(self.frameItensHistorico, text="Data inválida! Use o formato DD/MM/AAAA.",
                    bg="#FFFFFF", font=("Arial", 10), fg="red").pack(pady=5)
            return

        ranking = self.mc.mah.buscarRankingPorPeriodo(dataInicioFormatada, dataFimFormatada)
        self.atualizarHistorico(ranking)

    # Limpa o filtro e volta pro padrão semanal
    def limparFiltroHistorico(self):
        self.entradaDataInicio.delete(0, tk.END)
        self.entradaDataInicio.insert(0, "DD/MM/AAAA")
        self.entradaDataFim.delete(0, tk.END)
        self.entradaDataFim.insert(0, "DD/MM/AAAA")
        self.atualizarHistorico()

    # Atualiza a lista de histórico com os dados fornecidos ou busca padrão semanal
    def atualizarHistorico(self, ranking=None):
        # Limpa os itens da lista
        for widget in self.frameItensHistorico.winfo_children():
            widget.destroy()

        if ranking is None:
            ranking = self.mc.mah.buscarRanking(diasAtras=7) if self.mc.mah else []

        maxKwh = max(r[2] for r in ranking) if ranking else 1

        if not ranking:
            tk.Label(self.frameItensHistorico, text="Nenhum dado encontrado.",
                    bg="#FFFFFF", font=("Arial", 11), fg="#888888").pack(pady=20)
            return

        for site, url, totalKwh in ranking:
            frameSite = tk.Frame(self.frameItensHistorico, bg="#FFFFFF")
            frameSite.pack(fill="x", pady=8)

            tk.Label(frameSite, text=site[:40], bg="#FFFFFF",
                    font=("Arial", 11, "bold"), anchor="w").pack(fill="x")

            proporcaoKwh = totalKwh / maxKwh if maxKwh > 0 else 0
            largura = max(int(proporcaoKwh * 550), 30)

            frameBarra = tk.Frame(frameSite, bg="#E0E0E0", height=22)
            frameBarra.pack(fill="x")
            frameBarra.pack_propagate(False)

            tk.Frame(frameBarra, bg="#4AE54A", width=largura, height=22).place(x=0, y=0)
            tk.Label(frameBarra, text=f"{totalKwh:.6f} kWh",
                    bg="#4AE54A" if largura > 80 else "#E0E0E0",
                    font=("Arial", 9, "bold")).place(x=5, y=2)

    # Inicia o loop principal da interface
    def iniciar(self):
        self.janela.mainloop()


if __name__ == "__main__":
    # Teste da interface sem o controlador completo
    class MCFake:
        mah = None
        def executarCalibracao(self):
            import time
            time.sleep(3)

    mi = MI(MCFake())
    mi.iniciar()