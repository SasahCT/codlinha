def cifra_cesar(msg):
    key=21
    msg_cript=""

    for c in msg:
        msg_cript+= chr(ord(c)+key)
        #ord transforma o caracter para seu numero equivalente na tabela ASCII
        #chr retorna o numero em letra

    return msg_cript
    

    