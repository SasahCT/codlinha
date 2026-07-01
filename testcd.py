#Feito com auxilio do Google Gemini
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QTabWidget, QMessageBox)

from PyQt6.QtCore import QTimer
import pyqtgraph as pg
import conversao_binario
import cript
import mlt3
import com_esp
import time
import serial

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

        self.dados_para_envio = None
        self.meu_id = "esp1"

        self.tabs.addTab(self.aba_host_a, "Host A (Envio)")
        self.tabs.addTab(self.aba_host_b, "Host B (Recepção)")
        
        self.configurar_host_a()
        self.configurar_host_b()

        # Timer que vai checar a porta USB
        self.timer_serial = QTimer()
        self.timer_serial.timeout.connect(self.verificar_porta_serial)
        self.timer_serial.start(100) 
        try:
            self.conexao_serial = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
        except Exception as e:
            self.conexao_serial = None
            print(f"Aviso: Não foi possível abrir a porta Serial: {e}")

    def configurar_host_a(self):
        # Layout do Host A
        layout = QVBoxLayout()
        
        # Campo para digitar o texto original
        layout.addWidget(QLabel("<b>1. Mensagem Escrita (Texto Original):</b>"))
        self.txt_original_a = QLineEdit()
        layout.addWidget(self.txt_original_a)
        
        # Botão para processar (tradução)
        self.btn_processar = QPushButton("Processar e Gerar Gráfico")
        self.btn_processar.clicked.connect(self.acao_apertar_botao)
        layout.addWidget(self.btn_processar)
        
        layout.addWidget(QLabel("<b>2. Mensagem Criptografada:</b>"))
        self.txt_cripto_a = QLineEdit()
        self.txt_cripto_a.setReadOnly(True)
        layout.addWidget(self.txt_cripto_a)
        
        layout.addWidget(QLabel("<b>3. Mensagem em Binário (ASCII Estendido):</b>"))
        self.txt_binario_a = QLineEdit()
        self.txt_binario_a.setReadOnly(True)
        layout.addWidget(self.txt_binario_a)

        layout.addWidget(QLabel("<b>4. Níveis de Tensão da Codificação (MLT-3):</b>"))
        self.txt_mlt3_a = QLineEdit()
        self.txt_mlt3_a.setReadOnly(True)
        layout.addWidget(self.txt_mlt3_a)
        
        # Gráfico
        layout.addWidget(QLabel("<b>4. Gráfico da Codificação de Linha:</b>"))
        self.grafico_a = pg.PlotWidget()
        self.grafico_a.setBackground('w')
        self.grafico_a.showGrid(x=True, y=True)
        layout.addWidget(self.grafico_a)
        
        # Botão para enviar pela rede 
        self.btn_enviar = QPushButton("Enviar para o Host B")
        self.btn_enviar.setStyleSheet("background-color: purple; color: white;")
        self.btn_enviar.clicked.connect(self.acao_enviar_botao)
        layout.addWidget(self.btn_enviar)
        
        self.aba_host_a.setLayout(layout)

    def configurar_host_b(self):
        # Layout do Host B
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h3>Aguardando dados da rede...</h3>"))

        layout.addWidget(QLabel("<b>Mensagem Recebida de (Origem):</b>"))
        self.txt_origem_b = QLineEdit()
        self.txt_origem_b.setReadOnly(True)
        self.txt_origem_b.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.txt_origem_b)
        
        # Gráfico invertido 
        layout.addWidget(QLabel("<b>Gráfico da Onda Recebida:</b>"))
        self.grafico_b = pg.PlotWidget()
        self.grafico_b.setBackground('w')
        self.grafico_b.showGrid(x=True, y=True)
        layout.addWidget(self.grafico_b)
        
        layout.addWidget(QLabel("<b>Níveis de Tensão Extraídos (MLT-3):</b>"))
        self.txt_mlt3_b = QLineEdit()
        self.txt_mlt3_b.setReadOnly(True)
        self.txt_mlt3_b.setStyleSheet("color: darkred; font-weight: bold;")
        layout.addWidget(self.txt_mlt3_b)

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
        #aqui é feita a "tradução"
        texto_original = self.txt_original_a.text()
        
        if not texto_original:
            return
            
        texto_cifrado = cript.cifra_cesar(texto_original)

        #ASCII extendido
        texto_com_simbolos = bytes(ord(c) for c in texto_cifrado).decode('cp437', errors='replace')
        self.txt_cripto_a.setText(texto_com_simbolos)
        
        mensagem_binaria = conversao_binario.texto_para_binario(texto_cifrado)

        self.txt_binario_a.setText(mensagem_binaria)

        niveis_mlt3 = mlt3.mlt_3(mensagem_binaria)
        texto_formatado = ", ".join(f"+{n}" if n > 0 else str(n) for n in niveis_mlt3)
        self.txt_mlt3_a.setText(texto_formatado)

        #a sequência de valores de tensão é transformada em string
        self.dados_para_envio = ",".join(map(str, niveis_mlt3))

        x_plot = []
        y_plot = []
        
        #parte responsável pelo desenho do gráfico
        for i, nivel in enumerate(niveis_mlt3):
            x_plot.extend([i, i + 1])
            y_plot.extend([nivel, nivel])
            
        #limpa qualquer desenho anterior do gráfico
        self.grafico_a.clear()
        
        #desenho da linha vermelha
        self.grafico_a.plot(x_plot, y_plot, pen=pg.mkPen('r', width=3))
        
        #ajusta os limites do gráfico para não ficar colado nas bordas
        self.grafico_a.setYRange(-1.5, 1.5) 
        self.grafico_a.setXRange(0, len(mensagem_binaria))  

    def acao_enviar_botao(self):
        if self.dados_para_envio is None:
            QMessageBox.warning(self, "Aviso", "Por favor, digite e Processe uma mensagem primeiro!")
            return

        if self.conexao_serial is None or not self.conexao_serial.is_open:
            QMessageBox.critical(self, "Erro de Conexão", "O ESP32 não está conectado na porta Serial (COM)!")
            return

        try:
            dados_com_protocolo = f"{self.meu_id}:{self.dados_para_envio}"
            
            com_esp.envio_dados(dados_com_protocolo, self.conexao_serial)
            QMessageBox.information(self, "Sucesso", f"Dados transmitidos como {self.meu_id} com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro no Envio", f"Falha ao enviar dados pelo cabo USB: {e}")

    def closeEvent(self, event):
        #essa função é responsável por terminar com a conexão estabelecida
        print("Fechando o aplicativo...")
        
        #para o timer
        if hasattr(self, 'timer_serial'):
            self.timer_serial.stop()
            
        #fecha a porta serial definitivamente    
        if hasattr(self, 'conexao_serial') and self.conexao_serial and self.conexao_serial.is_open:
            self.conexao_serial.close()
            print("Porta Serial liberada com sucesso!")
            
        event.accept()

    def verificar_porta_serial(self):
        if hasattr(self, 'conexao_serial') and self.conexao_serial and self.conexao_serial.is_open:
            try:
                if self.conexao_serial.in_waiting > 0:
                    linha_recebida = com_esp.recebimento_dados(self.conexao_serial)
                    
                    #envia para processamento se a linha for válida e completa
                    if linha_recebida and linha_recebida.startswith("RX:"):
                        dados_limpos = linha_recebida.replace("RX:", "")
                        self.processar_dados_recebidos(dados_limpos)
                        
            except Exception as e:
                print(f"Erro na leitura serial: {e}")

    def processar_dados_recebidos(self, dados_string):
        
        try:
            dados_string = dados_string.strip()
            print(f"Dados brutos recebidos: '{dados_string}'")
            
            if dados_string.startswith("RX:"):
                dados_string = dados_string[3:].strip()
            
            if ":" in dados_string:
                quem_mandou, apenas_niveis = dados_string.split(":", 1)
                quem_mandou = quem_mandou.strip()
                apenas_niveis = apenas_niveis.strip()
            else:
                quem_mandou = "Desconhecido"
                apenas_niveis = dados_string
                
            print(f"-> 3. Remetente identificado: '{quem_mandou}'")
            print(f"-> 4. String contendo apenas níveis: '{apenas_niveis}'")

            if hasattr(self, 'txt_origem_b'):
                self.txt_origem_b.setText(quem_mandou)
            
            elementos = [x.strip() for x in apenas_niveis.split(",") if x.strip()]
            niveis_mlt3 = [int(x) for x in elementos]
            
            if not niveis_mlt3:
                print("[AVISO] A lista de níveis MLT-3 ficou vazia.")
                return

            print(f"-> 5. Níveis convertidos com sucesso ({len(niveis_mlt3)} pontos).")

            self.txt_mlt3_b.setText(", ".join(map(str, niveis_mlt3)))
            
            #desenha o gráfico
            self.grafico_b.clear()
            x_plot = []
            y_plot = []
            for i, nivel in enumerate(niveis_mlt3):
                x_plot.extend([i, i + 1])
                y_plot.extend([nivel, nivel])
                
            self.grafico_b.plot(x_plot, y_plot, pen=pg.mkPen('b', width=3)) 
            self.grafico_b.setYRange(-1.5, 1.5)
            self.grafico_b.setXRange(0, len(niveis_mlt3))
            
            #decodificações
            mensagem_binaria = mlt3.desmlt_3(niveis_mlt3)
            self.txt_binario_b.setText(mensagem_binaria)
            
            texto_cripto = conversao_binario.binario_para_texto(mensagem_binaria)
            texto_com_simbolos = bytes(ord(c) for c in texto_cripto).decode('cp437', errors='replace')
            self.txt_cripto_b.setText(texto_com_simbolos)
            
            texto_original = cript.descript(texto_cripto)
            self.txt_original_b.setText(texto_original)
            print(f"sucesso\n")
            
        except Exception as e:
            import traceback
            print(f"\n[erro]:")
            traceback.print_exc()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = LineCodingApp()
    janela.show()
    sys.exit(app.exec())
