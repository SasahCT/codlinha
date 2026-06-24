#o PY precisa saber onde o ESP está conectado(port): /dev/ttyUSB0
#Baud Rate: mesma velocidade dos dois lados
import serial
import time

def envio_dados(msg, conexao):

    msg_final=msg+"\n"
#para enviar um dado para o ESP, usa-se .write()
#deve-se transformar os dados em uma sequência de bytes puros com .encode() -> apenas para strings
    conexao.write(msg_final.encode('utf-8'))



def recebimento_dados(conexao):
    #tenta ler se houver bytes na fila
    if conexao.in_waiting > 0:
        dados_brutos = conexao.readline()

        #aceita se a linha veio completa, ou seja, termina com \n
        if dados_brutos.endswith(b'\n'):
            msg = dados_brutos.decode('utf-8', errors='ignore').strip()
            return msg
            
    return "" 

