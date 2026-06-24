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
        
        self.tabs.addTab(self.aba_host_a, "Host A (Envio)")
        self.tabs.addTab(self.aba_host_b, "Host B (Recepção)")
        
        self.configurar_host_a()
        self.configurar_host_b()

        # Timer que vai checar a porta USB a cada 100 milissegundos
        self.timer_serial = QTimer()
        self.timer_serial.timeout.connect(self.verificar_porta_serial)
        self.timer_serial.start(100) 
        try:
            self.conexao_serial = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.1)
        except Exception as e:
            self.conexao_serial = None
            print(f"Aviso: Não foi possível abrir a porta Serial: {e}")

    def configurar_host_a(self):
        # Layout principal do Host A
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
        self.btn_enviar.setStyleSheet("background-color: pink; color: white;")
        self.btn_enviar.clicked.connect(self.acao_enviar_botao)
        layout.addWidget(self.btn_enviar)
        
        self.aba_host_a.setLayout(layout)

    def configurar_host_b(self):
        # Layout principal do Host B (Recepção)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h3>Aguardando dados da rede...</h3>"))
        
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
        
        # Ajusta os limites visuais do gráfico para não ficar colado nas bordas
        self.grafico_a.setYRange(-1.5, 1.5)  # Eixo Y vai de -1.5V até +1.5V
        self.grafico_a.setXRange(0, len(mensagem_binaria))  # Eixo X acompanha o tamanho da mensagem

    def acao_enviar_botao(self):
        
        # Validação 1: O usuário clicou em Enviar antes de Processar?
        if self.dados_para_envio is None:
            QMessageBox.warning(self, "Aviso", "Por favor, digite e Processe uma mensagem primeiro!")
            return

        # Validação 2: A porta USB está aberta/disponível?
        if self.conexao_serial is None or not self.conexao_serial.is_open:
            QMessageBox.critical(self, "Erro de Conexão", "O ESP32 não está conectado na porta Serial (COM)!")
            return

        try:
            #em caso de sucesso, é feito o envio dos dados
            com_esp.envio_dados(self.dados_para_envio, self.conexao_serial)
            QMessageBox.information(self, "Sucesso", "Dados transmitidos para o ESP32 com sucesso!")
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
        # Verifica se a conexão existe e está aberta
        if hasattr(self, 'conexao_serial') and self.conexao_serial and self.conexao_serial.is_open:
            try:
                linha_recebida=com_esp.recebimento_dados(self.conexao_serial)
                if linha_recebida.startswith("RX:"):
                    dados_limpos = linha_recebida.replace("RX:", "")
                        
                    # Manda a string "0,1,0,-1..." para a função que atualiza a tela
                    self.processar_dados_recebidos(dados_limpos)
                        
            except Exception as e:
                print(f"Erro silencioso na leitura serial: {e}")

    def processar_dados_recebidos(self, dados_string):
        """
        Recebe a string limpa do ESP32 e faz o caminho: 
        Gráfico -> MLT-3 -> Binário -> Cripto -> Texto Original
        """
        try:
            # 1. Mostra a string crua recebida na tela
            self.txt_mlt3_b.setText(dados_string)
            
            # Converte a string "0,1,0,-1" de volta para uma lista de inteiros [0, 1, 0, -1]
            niveis_mlt3 = [int(x) for x in dados_string.split(",")]
            
            # 2. Desenha o gráfico da onda recebida (Em AZUL para o Host B)
            self.grafico_b.clear()
            x_plot = []
            y_plot = []
            for i, nivel in enumerate(niveis_mlt3):
                x_plot.extend([i, i + 1])
                y_plot.extend([nivel, nivel])
                
            self.grafico_b.plot(x_plot, y_plot, pen=pg.mkPen('b', width=3)) # 'b' de Blue
            self.grafico_b.setYRange(-1.5, 1.5)
            self.grafico_b.setXRange(0, len(niveis_mlt3))
            
            # 3. Decodifica MLT-3 para Binário
            # Presume que no arquivo mlt3.py exista uma função chamada decodificar_mlt3
            mensagem_binaria = mlt3.desmlt_3(niveis_mlt3)
            self.txt_binario_b.setText(mensagem_binaria)
            
            # 4. Decodifica Binário para Texto Criptografado
            # Presume que em conversao_binario.py exista uma função binario_para_texto
            texto_cripto = conversao_binario.binario_para_texto(mensagem_binaria)
            texto_com_simbolos = bytes(ord(c) for c in texto_cripto).decode('cp437', errors='replace')
            self.txt_cripto_b.setText(texto_com_simbolos)
            
            # 5. Descriptografa a Cifra de César
            # Presume que no arquivo cript.py exista uma função decifra_cesar
            texto_original = cript.descript(texto_cripto)
            self.txt_original_b.setText(texto_original)
            
        except Exception as e:
            print(f"Aviso: Dados corrompidos recebidos pela rede. Ignorando pacote. Erro: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = LineCodingApp()
    janela.show()
    sys.exit(app.exec())
