def cifra_cesar(msg):
    key=21
    msg_cript=""

    for c in msg:
        msg_cript+= chr((ord(c)+key)%256)
        #ord transforma o caracter para seu numero equivalente na tabela ASCII
        #chr retorna o numero em letra

    return msg_cript
    

def descript (msg_cript):
    key=21
    msg=""

    for c in msg_cript:
        msg+=chr((ord(c)-key)%256)

    return msg