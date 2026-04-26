import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime

# Paleta de cores do tema escuro com verde esmeralda
CORES = {
    "fundo": "#0F1117",
    "sidebar": "#1A1D27",
    "card": "#1E2130",
    "borda": "#2A2D3E",
    "verde": "#2ECC71",
    "verde_escuro": "#27AE60",
    "verde_fundo": "#1A3A2A",
    "texto": "#E8ECF0",
    "texto_secundario": "#8892A4",
    "branco": "#FFFFFF",
    "erro": "#E74C3C",
    "azul_barra": "#3498DB",
}

class MI:

    # Inicializa a interface com o controlador e configura a janela principal
    def __init__(self, mc):
        self.mc = mc
        self.janela = tk.Tk()
        self.janela.title("Watts por Site")
        self.janela.geometry("1100x700")
        self.janela.configure(bg=CORES["fundo"])
        self.janela.resizable(False, False)

        self.configurarLayout()
        self.mostrarInicio()

    # Configura o layout base com sidebar e área principal
    def configurarLayout(self):
        # Sidebar escura à esquerda
        self.sidebar = tk.Frame(self.janela, bg=CORES["sidebar"], width=170)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo no topo da sidebar
        frameLogo = tk.Frame(self.sidebar, bg=CORES["verde"], width=170, height=60)
        frameLogo.pack(fill="x")
        frameLogo.pack_propagate(False)
        tk.Label(frameLogo, text="W⚡S", bg=CORES["verde"],
                 fg=CORES["fundo"], font=("Courier", 14, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Separador
        tk.Frame(self.sidebar, bg=CORES["borda"], height=1).pack(fill="x", pady=(0, 10))

        # Botões de navegação
        self.botaoInicio = self.criarBotaoNav("🏠  Início", self.mostrarInicio)
        self.botaoCalibragem = self.criarBotaoNav("⚙  Calibragem", self.mostrarCalibragem)
        self.botaoHistorico = self.criarBotaoNav("📊  Histórico", self.mostrarHistorico)

        # Rodapé da sidebar
        tk.Label(self.sidebar, text="v1.0", bg=CORES["sidebar"],
                 fg=CORES["texto_secundario"], font=("Courier", 8)).pack(side="bottom", pady=10)

        # Área principal
        self.areaPrincipal = tk.Frame(self.janela, bg=CORES["fundo"])
        self.areaPrincipal.pack(side="left", fill="both", expand=True)

    # Cria um botão de navegação padronizado na sidebar
    def criarBotaoNav(self, texto, comando):
        botao = tk.Button(
            self.sidebar, text=texto, bg=CORES["sidebar"],
            fg=CORES["texto_secundario"], font=("Courier", 10),
            relief="flat", anchor="w", padx=15, pady=10,
            activebackground=CORES["verde_fundo"],
            activeforeground=CORES["verde"],
            cursor="hand2", command=comando
        )
        botao.pack(fill="x", padx=8, pady=2)
        return botao

    # Limpa a área principal para trocar de tela
    def limparAreaPrincipal(self):
        for widget in self.areaPrincipal.winfo_children():
            widget.destroy()

    # Destaca o botão da tela ativa na sidebar
    def destacarBotao(self, botaoAtivo):
        for botao in [self.botaoInicio, self.botaoCalibragem, self.botaoHistorico]:
            botao.configure(bg=CORES["sidebar"], fg=CORES["texto_secundario"])
        botaoAtivo.configure(bg=CORES["verde_fundo"], fg=CORES["verde"])

    # Cria um card com fundo escuro e borda sutil
    def criarCard(self, parent, pady=8):
        card = tk.Frame(parent, bg=CORES["card"],
                        highlightbackground=CORES["borda"],
                        highlightthickness=1)
        card.pack(fill="x", pady=pady, padx=2)
        return card

    # Cria uma barra de progresso estilizada
    def criarBarra(self, parent, valor, maximo, cor, altura=18):
        frameBarra = tk.Frame(parent, bg=CORES["borda"], height=altura)
        frameBarra.pack(fill="x", pady=(4, 0))
        frameBarra.pack_propagate(False)

        proporcao = min(valor / maximo, 1.0) if maximo > 0 else 0
        largura = int(proporcao * 850)

        if largura > 0:
            tk.Frame(frameBarra, bg=cor, height=altura, width=largura).place(x=0, y=0)

        return frameBarra

    # Exibe a tela inicial com os sites em uso agora
    def mostrarInicio(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoInicio)

        # Redireciona pra calibragem se não tiver coeficiente
        if not self.mc.coeficiente:
            self.mostrarCalibragem()
            return

        # Cabeçalho
        frameHeader = tk.Frame(self.areaPrincipal, bg=CORES["fundo"])
        frameHeader.pack(fill="x", padx=30, pady=(30, 5))

        tk.Label(frameHeader, text="Sites em uso agora", bg=CORES["fundo"],
                 fg=CORES["branco"], font=("Courier", 20, "bold"), anchor="w").pack(side="left")

        tk.Label(self.areaPrincipal,
                 text="Estimativa de consumo energético por aba aberta no navegador",
                 bg=CORES["fundo"], fg=CORES["texto_secundario"],
                 font=("Courier", 9), anchor="w").pack(fill="x", padx=30, pady=(0, 20))
        
        # Botões de ação no cabeçalho
        frameBotoes = tk.Frame(frameHeader, bg=CORES["fundo"])
        frameBotoes.pack(side="right")

        tk.Button(frameBotoes, text="⚡ Coletar agora", bg=CORES["verde"],
                fg=CORES["fundo"], font=("Courier", 9, "bold"),
                relief="flat", cursor="hand2", padx=12, pady=6,
                command=self.coletarAgora).pack(side="left", padx=(0, 8))

        tk.Button(frameBotoes, text="↻ Atualizar", bg=CORES["borda"],
                fg=CORES["texto"], font=("Courier", 9),
                relief="flat", cursor="hand2", padx=12, pady=6,
                command=self.mostrarInicio).pack(side="left")

        # Linha separadora
        tk.Frame(self.areaPrincipal, bg=CORES["borda"], height=1).pack(fill="x", padx=30, pady=(0, 15))

        # Frame com scroll
        frameScroll = tk.Frame(self.areaPrincipal, bg=CORES["fundo"])
        frameScroll.pack(padx=30, fill="both", expand=True)

        canvas = tk.Canvas(frameScroll, bg=CORES["fundo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frameScroll, orient="vertical", command=canvas.yview)
        frameLista = tk.Frame(canvas, bg=CORES["fundo"])

        frameLista.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frameLista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dados reais
        dadosAtuais = self.mc.mah.buscarRanking(diasAtras=1) if self.mc.mah else []

        if not dadosAtuais:
            tk.Label(frameLista,
                     text="Nenhum dado coletado ainda.\nAguarde a próxima coleta (a cada 5 minutos).",
                     bg=CORES["fundo"], fg=CORES["texto_secundario"],
                     font=("Courier", 11), justify="center").pack(pady=40)
        else:
            maxKwh = max(r[2] for r in dadosAtuais)
            for i, (site, url, totalKwh) in enumerate(dadosAtuais):
                card = self.criarCard(frameLista)
                frameInner = tk.Frame(card, bg=CORES["card"])
                frameInner.pack(fill="x", padx=15, pady=12)

                # Número do ranking
                tk.Label(frameInner, text=f"#{i+1:02d}", bg=CORES["card"],
                         fg=CORES["verde"], font=("Courier", 11, "bold")).pack(side="left", padx=(0, 12))

                # Info do site
                frameInfo = tk.Frame(frameInner, bg=CORES["card"])
                frameInfo.pack(side="left", fill="both", expand=True)

                tk.Label(frameInfo, text=site[:50], bg=CORES["card"],
                         fg=CORES["texto"], font=("Courier", 11, "bold"),
                         anchor="w").pack(fill="x")

                tk.Label(frameInfo, text=url[:60], bg=CORES["card"],
                         fg=CORES["texto_secundario"], font=("Courier", 8),
                         anchor="w").pack(fill="x")

                self.criarBarra(frameInfo, totalKwh, maxKwh, CORES["verde"])

                # Valor kWh
                tk.Label(frameInner, text=f"{totalKwh:.6f}\nkWh",
                         bg=CORES["card"], fg=CORES["verde"],
                         font=("Courier", 10, "bold"), justify="right").pack(side="right", padx=(12, 0))

    # Exibe a tela de calibragem
    def mostrarCalibragem(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoCalibragem)

        # Cabeçalho
        tk.Label(self.areaPrincipal, text="Calibragem", bg=CORES["fundo"],
                 fg=CORES["branco"], font=("Courier", 20, "bold"),
                 anchor="w").pack(padx=30, pady=(30, 5), fill="x")

        tk.Frame(self.areaPrincipal, bg=CORES["borda"], height=1).pack(fill="x", padx=30, pady=(0, 20))

        # Card de explicação
        cardExplicacao = tk.Frame(self.areaPrincipal, bg=CORES["card"],
                                   highlightbackground=CORES["borda"],
                                   highlightthickness=1)
        cardExplicacao.pack(fill="x", padx=30, pady=(0, 20))

        texto = (
            "A calibragem permite que o aplicativo entenda com mais precisão como seu computador\n"
            "consome energia enquanto você navega. Esse processo ajusta os parâmetros internos\n"
            "de medição para que os resultados apresentados sejam mais confiáveis.\n\n"
            "Durante os 20 segundos de calibragem, a CPU será estressada para obter leituras\n"
            "precisas do sensor de energia. Feche outros programas pesados antes de iniciar."
        )
        tk.Label(cardExplicacao, text=texto, bg=CORES["card"],
                 fg=CORES["texto_secundario"], font=("Courier", 10),
                 justify="left", anchor="w").pack(padx=20, pady=20, fill="x")

        # Status
        self.labelStatusCalibragem = tk.Label(
            self.areaPrincipal, text="", bg=CORES["fundo"],
            fg=CORES["verde"], font=("Courier", 11)
        )
        self.labelStatusCalibragem.pack(pady=10)

        # Botão
        tk.Button(self.areaPrincipal, text="▶  Iniciar calibragem",
                  bg=CORES["verde"], fg=CORES["fundo"],
                  font=("Courier", 13, "bold"),
                  relief="flat", cursor="hand2", padx=30, pady=14,
                  activebackground=CORES["verde_escuro"],
                  command=self.iniciarCalibragem).pack(pady=20)

    # Inicia a calibragem em thread separada para não travar a interface
    def iniciarCalibragem(self):
        self.labelStatusCalibragem.config(
            text="⏳ Calibrando... Por favor aguarde 20 segundos.")
        threading.Thread(target=self.executarCalibragem, daemon=True).start()

    # Executa a calibragem e exibe o popup de conclusão
    def executarCalibragem(self):
        self.mc.executarCalibracao()
        self.janela.after(0, self.mostrarPopupCalibracaoConcluida)

    # Exibe o popup de calibragem concluída
    def mostrarPopupCalibracaoConcluida(self):
        popup = tk.Toplevel(self.janela)
        popup.title("")
        popup.geometry("580x380")
        popup.configure(bg=CORES["card"])
        popup.resizable(False, False)

        tk.Frame(popup, bg=CORES["verde"], height=4).pack(fill="x")

        tk.Label(popup, text="✓ Calibragem concluída com sucesso!",
                 bg=CORES["card"], fg=CORES["verde"],
                 font=("Courier", 15, "bold")).pack(pady=(25, 15), padx=30)

        instrucoes = (
            "Para garantir medições mais precisas, recomendamos:\n\n"
            "  1 — Reinicie o computador após a calibragem.\n\n"
            "  2 — Deixe o app em segundo plano durante o uso.\n\n"
            "  3 — Evite fechar o aplicativo durante o dia a dia."
        )
        tk.Label(popup, text=instrucoes, bg=CORES["card"],
                 fg=CORES["texto_secundario"], font=("Courier", 10),
                 justify="left").pack(padx=40, fill="x")

        tk.Button(popup, text="Ir para o início →",
                  bg=CORES["verde"], fg=CORES["fundo"],
                  font=("Courier", 11, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10,
                  command=lambda: [popup.destroy(), self.mostrarInicio()]).pack(pady=25)

    # Dispara uma coleta imediata e atualiza a tela após 4 segundos
    def coletarAgora(self):
        self.mc.coletarAgora()
        self.janela.after(4000, self.mostrarInicio)


    # Exibe a tela de histórico com ranking e filtro de datas
    def mostrarHistorico(self):
        self.limparAreaPrincipal()
        self.destacarBotao(self.botaoHistorico)

        tk.Label(self.areaPrincipal, text="Seu consumo", bg=CORES["fundo"],
                 fg=CORES["branco"], font=("Courier", 20, "bold"),
                 anchor="w").pack(padx=30, pady=(30, 5), fill="x")
        tk.Frame(self.areaPrincipal, bg=CORES["borda"], height=1).pack(fill="x", padx=30, pady=(0, 15))

        frameConteudo = tk.Frame(self.areaPrincipal, bg=CORES["fundo"])
        frameConteudo.pack(padx=30, fill="both", expand=True)

        # Lista à esquerda
        self.frameListaHistorico = tk.Frame(frameConteudo, bg=CORES["fundo"])
        self.frameListaHistorico.pack(side="left", fill="both", expand=True)

        tk.Label(self.frameListaHistorico, text="Maior consumo semanal",
                 bg=CORES["fundo"], fg=CORES["texto_secundario"],
                 font=("Courier", 10), anchor="w").pack(fill="x", pady=(0, 10))

        self.canvasHistorico = tk.Canvas(self.frameListaHistorico, bg=CORES["fundo"],
                                          highlightthickness=0)
        scrollbarH = ttk.Scrollbar(self.frameListaHistorico, orient="vertical",
                                    command=self.canvasHistorico.yview)
        self.frameItensHistorico = tk.Frame(self.canvasHistorico, bg=CORES["fundo"])

        self.frameItensHistorico.bind("<Configure>",
            lambda e: self.canvasHistorico.configure(
                scrollregion=self.canvasHistorico.bbox("all")))
        self.canvasHistorico.create_window((0, 0), window=self.frameItensHistorico, anchor="nw")
        self.canvasHistorico.configure(yscrollcommand=scrollbarH.set)
        self.canvasHistorico.pack(side="left", fill="both", expand=True)
        scrollbarH.pack(side="right", fill="y")

        # Filtro à direita
        frameFiltro = tk.Frame(frameConteudo, bg=CORES["sidebar"],
                                highlightbackground=CORES["borda"],
                                highlightthickness=1, width=200)
        frameFiltro.pack(side="right", fill="y", padx=(20, 0))
        frameFiltro.pack_propagate(False)

        tk.Label(frameFiltro, text="FILTRO", bg=CORES["sidebar"],
                 fg=CORES["verde"], font=("Courier", 10, "bold"),
                 anchor="w").pack(fill="x", padx=15, pady=(15, 10))

        tk.Label(frameFiltro, text="Data de início", bg=CORES["sidebar"],
                 fg=CORES["texto_secundario"], font=("Courier", 9),
                 anchor="w").pack(fill="x", padx=15, pady=(5, 2))

        self.entradaDataInicio = tk.Entry(frameFiltro, font=("Courier", 10),
                                           bg=CORES["card"], fg=CORES["texto"],
                                           insertbackground=CORES["verde"],
                                           relief="flat", bd=5)
        self.entradaDataInicio.insert(0, "DD/MM/AAAA")
        self.entradaDataInicio.pack(fill="x", padx=15)

        tk.Label(frameFiltro, text="Data de fim", bg=CORES["sidebar"],
                 fg=CORES["texto_secundario"], font=("Courier", 9),
                 anchor="w").pack(fill="x", padx=15, pady=(10, 2))

        self.entradaDataFim = tk.Entry(frameFiltro, font=("Courier", 10),
                                        bg=CORES["card"], fg=CORES["texto"],
                                        insertbackground=CORES["verde"],
                                        relief="flat", bd=5)
        self.entradaDataFim.insert(0, "DD/MM/AAAA")
        self.entradaDataFim.pack(fill="x", padx=15)

        tk.Button(frameFiltro, text="▶ Filtrar",
                  bg=CORES["verde"], fg=CORES["fundo"],
                  font=("Courier", 10, "bold"), relief="flat",
                  cursor="hand2", pady=8,
                  command=self.filtrarHistorico).pack(fill="x", padx=15, pady=10)

        tk.Button(frameFiltro, text="✕ Limpar",
                  bg=CORES["borda"], fg=CORES["texto_secundario"],
                  font=("Courier", 9), relief="flat",
                  cursor="hand2", pady=6,
                  command=self.limparFiltroHistorico).pack(fill="x", padx=15)

        self.atualizarHistorico()

    # Aplica o filtro de data no histórico
    def filtrarHistorico(self):
        dataInicio = self.entradaDataInicio.get()
        dataFim = self.entradaDataFim.get()
        try:
            dataInicioFormatada = datetime.strptime(dataInicio, "%d/%m/%Y").strftime("%Y-%m-%d")
            dataFimFormatada = datetime.strptime(dataFim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            tk.Label(self.frameItensHistorico,
                     text="⚠ Data inválida! Use DD/MM/AAAA.",
                     bg=CORES["fundo"], fg=CORES["erro"],
                     font=("Courier", 10)).pack(pady=10)
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

    # Atualiza a lista de histórico
    def atualizarHistorico(self, ranking=None):
        for widget in self.frameItensHistorico.winfo_children():
            widget.destroy()

        if ranking is None:
            ranking = self.mc.mah.buscarRanking(diasAtras=7) if self.mc.mah else []

        if not ranking:
            tk.Label(self.frameItensHistorico, text="Nenhum dado encontrado.",
                     bg=CORES["fundo"], fg=CORES["texto_secundario"],
                     font=("Courier", 11)).pack(pady=20)
            return

        maxKwh = max(r[2] for r in ranking)
        for i, (site, url, totalKwh) in enumerate(ranking):
            card = tk.Frame(self.frameItensHistorico, bg=CORES["card"],
                            highlightbackground=CORES["borda"], highlightthickness=1)
            card.pack(fill="x", pady=5, padx=2)

            frameInner = tk.Frame(card, bg=CORES["card"])
            frameInner.pack(fill="x", padx=15, pady=10)

            tk.Label(frameInner, text=f"#{i+1:02d}", bg=CORES["card"],
                     fg=CORES["verde"], font=("Courier", 10, "bold")).pack(side="left", padx=(0, 10))

            frameInfo = tk.Frame(frameInner, bg=CORES["card"])
            frameInfo.pack(side="left", fill="both", expand=True)

            tk.Label(frameInfo, text=site[:45], bg=CORES["card"],
                     fg=CORES["texto"], font=("Courier", 10, "bold"),
                     anchor="w").pack(fill="x")

            proporcao = totalKwh / maxKwh if maxKwh > 0 else 0
            largura = max(int(proporcao * 500), 20)
            frameBarra = tk.Frame(frameInfo, bg=CORES["borda"], height=14)
            frameBarra.pack(fill="x", pady=(4, 0))
            frameBarra.pack_propagate(False)
            tk.Frame(frameBarra, bg=CORES["verde"], width=largura, height=14).place(x=0, y=0)

            tk.Label(frameInner, text=f"{totalKwh:.6f} kWh",
                     bg=CORES["card"], fg=CORES["verde"],
                     font=("Courier", 9, "bold")).pack(side="right", padx=(10, 0))

    # Inicia o loop principal da interface
    def iniciar(self):
        self.janela.mainloop()


if __name__ == "__main__":
    class MCFake:
        coeficiente = 0.75
        class mah:
            @staticmethod
            def buscarRanking(diasAtras=7):
                return [
                    ("YouTube", "https://youtube.com", 0.00042),
                    ("ChatGPT", "https://chatgpt.com", 0.00031),
                    ("Google", "https://google.com", 0.00018),
                ]
            @staticmethod
            def buscarRankingPorPeriodo(i, f): return []
        def executarCalibracao(self):
            import time; time.sleep(3)

    mi = MI(MCFake())
    mi.iniciar()