import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QTabWidget)
import pyqtgraph as pg
import conversao_binario

class LineCodingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codificador de Linha & Criptografia - Redes")
        self.setGeometry(100, 100, 900, 600)
        
        # Criando abas para separar o Host A (Envio) e Host B (Recepção)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.aba_host_a = QWidget()
        self.aba_host_b = QWidget()
        
        self.tabs.addTab(self.aba_host_a, "Host A (Envio)")
        self.tabs.addTab(self.aba_host_b, "Host B (Recepção)")
        
        self.configurar_host_a()
        self.configurar_host_b()

    def configurar_host_a(self):
        # Layout principal do Host A
        layout = QVBoxLayout()
        
        # Campo para digitar o texto original
        layout.addWidget(QLabel("<b>1. Mensagem Escrita (Texto Original):</b>"))
        self.txt_original_a = QLineEdit()
        layout.addWidget(self.txt_original_a)
        
        # Botão para processar (Criptografar -> Binário -> Codificar)
        self.btn_processar = QPushButton("Processar e Gerar Gráfico")
        layout.addWidget(self.btn_processar)
        
        # Campos de exibição dos resultados (Exigência T1)
        layout.addWidget(QLabel("<b>2. Mensagem Criptografada:</b>"))
        self.txt_cripto_a = QLineEdit()
        self.txt_cripto_a.setReadOnly(True)
        layout.addWidget(self.txt_cripto_a)
        
        layout.addWidget(QLabel("<b>3. Mensagem em Binário (ASCII Estendido):</b>"))
        self.txt_binario_a = QLineEdit()
        self.txt_binario_a.setReadOnly(True)
        layout.addWidget(self.txt_binario_a)
        
        # Área do Gráfico da Forma de Onda (Exigência T2)
        layout.addWidget(QLabel("<b>4. Gráfico da Codificação de Linha:</b>"))
        self.grafico_a = pg.PlotWidget()
        self.grafico_a.setBackground('w') # Fundo branco para melhor leitura
        self.grafico_a.showGrid(x=True, y=True)
        layout.addWidget(self.grafico_a)
        
        # Botão para enviar pela rede (T7)
        self.btn_enviar = QPushButton("Enviar para o Host B")
        self.btn_enviar.setStyleSheet("background-color: green; color: white;")
        layout.addWidget(self.btn_enviar)
        
        self.aba_host_a.setLayout(layout)

    def configurar_host_b(self):
        # Layout principal do Host B (Recepção)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h3>Aguardando dados da rede...</h3>"))
        
        # Gráfico invertido (T2)
        layout.addWidget(QLabel("<b>Gráfico da Onda Recebida:</b>"))
        self.grafico_b = pg.PlotWidget()
        self.grafico_b.setBackground('w')
        self.grafico_b.showGrid(x=True, y=True)
        layout.addWidget(self.grafico_b)
        
        # Campos de decodificação reversa
        layout.addWidget(QLabel("<b>Binário Extraído da Onda:</b>"))
        self.txt_binario_b = QLineEdit()
        self.txt_binario_b.setReadOnly(True)
        layout.addWidget(self.txt_binario_b)
        
        layout.addWidget(QLabel("<b>Texto Criptografado Desconvertido:</b>"))
        self.txt_cripto_b = QLineEdit()
        self.txt_cripto_b.setReadOnly(True)
        layout.addWidget(self.txt_cripto_b)
        
        layout.addWidget(QLabel("<b>Mensagem Original Decifrada (Resultado Final):</b>"))
        self.txt_original_b = QLineEdit()
        self.txt_original_b.setReadOnly(True)
        self.txt_original_b.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.txt_original_b)
        
        self.aba_host_b.setLayout(layout)

    def acao_apertar_botao(self):

        texto_original = self.txt_original_a.text()
        
        if not texto_original:
            return
            
        # ETAPA 1: CRIPTOGRAFIA
        #texto_cifrado = self.cripto.criptografar(texto_original)
        #self.txt_cripto_a.setText(texto_cifrado)
        
        # ETAPA 2: CONVERSÃO BINÁRIA (usando o arquivo correto agora!)
        #mensagem_binaria = conversao_binario.texto_para_binario(texto_cifrado)
        #self.txt_binario_a.setText(mensagem_binaria)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = LineCodingApp()
    janela.show()
    sys.exit(app.exec())
