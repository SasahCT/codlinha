#o PY precisa saber onde o ESP está conectado(port): /dev/ttyUSB0
#Baud Rate: mesma velocidade dos dois lados
import serial
import time

#------------------------------------------------------------------------------
# A CONEXÃO É CRIADA FORA DA FUNÇÃO (Uma única vez no início do programa)
# Isso pode ficar no __init__ da sua interface gráfica
#------------------------------------------------------------------------------

# #criando objeto de conexão
# conexao=serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)

# #tempo para reiniciar o hardware
# time.sleep(2)
# #------------------------------------------------------------------------------
# conexao.close()



def envio_dados(msg, conexao):

    msg_final=msg+"\n"
#para enviar um dado para o ESP, usa-se .write()
#deve-se transformar os dados em uma sequência de bytes puros com .encode() -> apenas para strings
    conexao.write(msg_final.encode('utf-8'))



def recebimento_dados(conexao):
    # 1. Só tenta ler se houver bytes na fila
    if conexao.in_waiting > 0:
        dados_brutos = conexao.readline()

        # 2. SEgurança Máxima: Só aceita se a linha veio completa do ESP32 (termina com \n)
        if dados_brutos.endswith(b'\n'):
            msg = dados_brutos.decode('utf-8', errors='ignore').strip()
            return msg
            
    return "" # Retorna string vazia se o dado estiver incompleto ou não houver nada

