def mlt_3(binary):
    codif=[]
    estados=[0,1,0,-1]
    j=0

    for i in binary:
        
        if i== '0':
            codif.append(estados[j])
        else:
            j=(j+1)%4
            codif.append(estados[j])

    return codif

def desmlt_3(codif): # by sarah có
    binary = ""
    nivel_anterior = 0 

    for i in codif:
        if i == nivel_anterior:
            binary += "0" 
        else:
            binary += "1" 
            
        nivel_anterior = i 

    return binary
