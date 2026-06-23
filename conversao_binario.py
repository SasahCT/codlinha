def texto_para_binario(mensagem):
    if not mensagem:
        return ""
        
    binario = ''.join(format(ord(char), '08b') for char in mensagem)
    
    return binario

def binario_para_texto(sequencia_binaria):
    if not sequencia_binaria:
        return ""
        
    texto_decodificado = ""
    
    for i in range(0, len(sequencia_binaria), 8):
        byte = sequencia_binaria[i:i+8]
        
        caractere = chr(int(byte, 2))
        texto_decodificado += caractere
        
    return texto_decodificado