import json
import os
import sys
import socket
import threading
import ipaddress
import time
from const import *
from leader import Leader
from chordnodeobject import ChordNodeObject
from chordfilesystem import FileSystemNode


DISCOVERY_IP = "10.0.1.250"  # IP de descubrimiento
DISCOVERY_PORT = 6000  # Puerto de escucha

def discovery_server(server_ip):
    """Servidor que escucha en 10.0.1.250 y responde con su IP a los clientes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((DISCOVERY_IP, DISCOVERY_PORT))
        s.listen(5)
        print(f"📡 Servidor escuchando conexiones en {DISCOVERY_IP}:{DISCOVERY_PORT}...")

        while True:
            conn, addr = s.accept()
            print(f"🔗 Conexión de cliente desde {addr}")

            # Enviar la IP del servidor que lo está atendiendo
            conn.sendall(server_ip.encode())
            conn.close()

# 🛠 Iniciar el hilo de descubrimiento en cada servidor
def start_discovery_thread(server_ip):
    """Inicia el hilo del servidor de descubrimiento."""
    threading.Thread(target=discovery_server, args=(server_ip,), daemon=True).start()

if __name__ == "__main__":
    # Obtener la dirección IP actual
    ip = socket.gethostbyname(socket.gethostname())
    # ip = socket.gethostbyname_ex(socket.gethostname())[-1][0]

    # Caso de primer nodo en la red
    if len(sys.argv) == 1:
        # Crear nodo
        node = FileSystemNode(ip)
        print(f"Dirección IP del nodo: {ip}")
        time.sleep(4)
        node.discover_Succ()

    # Caso de unión a la red con un nodo existente
    elif len(sys.argv) == 2:
        target_ip = sys.argv[1]
        try:
            ipaddress.ip_address(target_ip)
        except:
            raise Exception(f"{target_ip} no es una dirección IP válida")

        # Crear nodo y unirse a la red
        node = FileSystemNode(ip)
        print(f"Dirección IP del nodo: {ip}")
        node.join(ChordNodeObject(target_ip))
    
    else:
        raise Exception("Parámetros incorrectos")

    start_discovery_thread(ip)
    # Bucle infinito para imprimir el predecesor y sucesor periódicamente
    counter = 0
    while True:
        if counter % 1000000 == 0:
            print(f"Predecesor: {str(node.succ).split(',')[0] if node.succ != None else None},Sucesor: {str(node.pred).split(',')[0] if node.pred != None else None}")
        
        counter += 1
        pass

