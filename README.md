# 📡 Comunicação MLT-3 Criptografada via ESP-NOW

Este projeto implementa um sistema completo de comunicação e transmissão de dados simulando a camada física e de enlace. Ele integra uma interface gráfica em Python com microcontroladores ESP32 comunicando-se via rádio (ESP-NOW).

## 🚀 Visão Geral
O sistema permite enviar mensagens de texto de um computador para outro utilizando ondas MLT-3. O fluxo de dados realiza o seguinte caminho:

1. **Python (Host Tx):** Recebe o texto, criptografa (Cifra de César), converte para Binário e depois para níveis de tensão (Codificação de Linha MLT-3).
2. **Cabo USB:** O Python envia a onda em formato de texto para o ESP32 conectado.
3. **ESP32 (Tx -> Rx):** O transmissor envia os níveis via protocolo **ESP-NOW** para o receptor usando endereço de Broadcast.
4. **Python (Host Rx):** Recebe os dados, plota o gráfico da onda em tempo real, decodifica, descriptografa e revela a mensagem e o remetente (ex: `esp1`).

## 🛠️ Tecnologias Utilizadas
* **Hardware:** Microcontroladores ESP32 (Wi-Fi/ESP-NOW).
* **Software:** C/C++ (Arduino IDE) e Python 3.
* **Bibliotecas Python:** `PyQt6` (Interface GUI), `pyqtgraph` (Gráficos), `pyserial` (Comunicação USB).

## 💻 Como Instalar e Rodar

### 1. Configurando o Hardware (ESP32)
1. Abra a IDE do Arduino.
2. Carregue o código fonte do ESP32 nas suas placas.
3. Certifique-se de alterar a variável que define o remetente em cada placa (se necessário, para identificar `esp1`, `esp2`, etc.).

### 2. Configurando o Computador (Python)
Abra o terminal na pasta raiz do projeto e instale as dependências:
```bash
pip install -r requirements.txt