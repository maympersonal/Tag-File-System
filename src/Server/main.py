import socket
import threading
import time
import sys
import ipaddress
from const import *
from chordfilesystem import FileSystemNode
from chordnodeobject import ChordNodeObject
from chordnode import ChordNode
from storage import Storage



"""if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    
    if len(sys.argv) == 1:
        print("🟢 Creando nodo como primer miembro de la red Chord")
        node = FileSystemNode(ip)
        node.join(ChordNodeObject("192.168.1.103"))

        time.sleep(2)
        #node.discover_Succ()

    elif len(sys.argv) == 2:
        target_ip = sys.argv[1]
        try:
            ipaddress.ip_address(target_ip)
        except ValueError:
            raise Exception(f"❌ {target_ip} no es una dirección IP válida")

        print("🟡 Conectando a la red existente...")
        node = FileSystemNode(ip)
        node.join(ChordNodeObject(target_ip))

    else:
        raise Exception("❌ Parámetros incorrectos")

    #start_discovery_thread(ip)

    while True:
        #time.sleep(5)  # ⏳ Reduce la frecuencia del monitoreo
        print(f"🔍 Estado del nodo → Predecesor: {node.pred.ip if node.pred else None}, Sucesor: {node.succ.ip if node.succ else None}")
"""

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())

    # Crear nodo

    node = FileSystemNode(ip)
    #node = ChordNode(ip)
    print(f"Dirección IP del nodo: {ip}")
    #node.join(ChordNodeObject(ip))
    #node.discover_Succ()

    # Bucle infinito para imprimir el predecesor y sucesor periódicamente
    counter = 0
    while True:
        if counter % 1000000 == 0:
            print(f"Predecesor: {str(node.pred).split(',')[0] if node.pred != None else None}, Nodo: {node.id}, Sucesor: {str(node.succ).split(',')[0] if node.succ != None else None}")
        counter += 1