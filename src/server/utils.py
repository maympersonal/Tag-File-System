import hashlib
import socket
from const import OK, END, END_FILE
from typing import Dict, List

# Función para calcular el hash SHA-1 de una cadena y devolver su representación entera
def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode('utf-8')).hexdigest(), 16)


# Función para verificar si un ID está entre otros dos ID en el anillo de Chord
def inbetween(k: int, start: int, end: int) -> bool:
    """
    Verifica si un ID k está en el intervalo entre start y end en un anillo Chord.

    Parámetros:
    k (int): ID a verificar.
    start (int): ID de inicio del intervalo.
    end (int): ID de fin del intervalo.

    Retorna:
    bool: True si k está en el intervalo, False en caso contrario.
    """
    if start < end:
        return start < k <= end
    else:  # El intervalo cruza el 0
        return start < k or k <= end


# Función para enviar dos mensajes a través de un socket y esperar confirmación de OK
def send_2(first_msg: str, second_msg: str, target_ip: str, target_port: int):
    """
    Envía dos mensajes al nodo de destino y espera confirmación de OK antes de continuar.

    Parámetros:
    first_msg (str): Primer mensaje a enviar.
    second_msg (str): Segundo mensaje a enviar.
    target_ip (str): Dirección IP de destino.
    target_port (int): Puerto de destino.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            s.sendall(first_msg.encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != f"{OK}":
                raise Exception("ACK negativo")

            s.sendall(second_msg.encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != f"{OK}":
                raise Exception("ACK negativo")
    except:
        print(f"{target_ip} no está disponible")


# Función para abrir un socket y enviar un archivo binario
def send_bin(op: str, file_name: str, bin: bytes, target_ip: str, target_port: int, end_msg: bool = False):
    """
    Envía un archivo binario a un nodo de destino a través de un socket.

    Parámetros:
    op (str): Código de operación.
    file_name (str): Nombre del archivo.
    bin (bytes): Contenido binario del archivo.
    target_ip (str): Dirección IP de destino.
    target_port (int): Puerto de destino.
    end_msg (bool): Si se debe enviar un mensaje de finalización.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((target_ip, target_port))

        s.sendall(op.encode('utf-8'))

        ack = s.recv(1024).decode('utf-8')
        if ack != f"{OK}":
            raise Exception("ACK negativo")

        s.sendall(file_name.encode('utf-8'))

        ack = s.recv(1024).decode('utf-8')
        if ack != f"{OK}":
            raise Exception("ACK negativo")

        s.sendall(bin)

        if end_msg:
            s.sendall(f"{END_FILE}".encode('utf-8'))

        return s.recv(1024)


# Función para enviar múltiples archivos binarios utilizando un socket específico
def send_bins(s: socket.socket, files_to_send: dict, path: str):
    """
    Envía múltiples archivos binarios a través de un socket.

    Parámetros:
    s (socket): Socket utilizado para la transmisión.
    files_to_send (dict): Diccionario con los nombres de archivo y sus datos.
    path (str): Ruta del directorio donde están los archivos.
    """
    for file_name, _ in files_to_send.items():
        file_path = f"{path}/{file_name}"

        s.sendall(file_name.encode('utf-8'))

        ack = s.recv(1024).decode('utf-8')
        if ack != f"{OK}":
            raise Exception("ACK negativo")

        with open(file_path, 'rb') as file:
            while True:
                data = file.read(1024)

                if not data:
                    break
                s.sendall(data)

                ack = s.recv(1024).decode('utf-8')
                if ack != f"{OK}":
                    raise Exception("ACK negativo")

            s.sendall(f"{END_FILE}".encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != f"{OK}":
                raise Exception("ACK negativo")
    
    s.sendall(f"{END}".encode('utf-8'))

    ack = s.recv(1024).decode('utf-8')
    if ack != f"{OK}":
        raise Exception("ACK negativo")


# Función para recibir múltiples archivos binarios y guardarlos en un directorio
def recv_write_bins(s: socket.socket, dest_dir: str):
    """
    Recibe múltiples archivos binarios y los guarda en un directorio.

    Parámetros:
    s (socket): Socket utilizado para la recepción.
    dest_dir (str): Directorio donde se almacenarán los archivos recibidos.
    """
    while True:
        data = s.recv(1024)
        if data.decode('utf-8') == f"{END}":
            break

        file_name = data.decode('utf-8')
        s.sendall(f"{OK}".encode('utf-8'))

        file_content = []
        while True:
            data = s.recv(1024)
            if data.decode('utf-8') == f"{END_FILE}":
                file_bin = b''.join(file_content)

                # Guardar el archivo binario en el directorio de destino
                with open(f"{dest_dir}/{file_name}", 'wb') as file:
                    file.write(file_bin)

                file_content = []
                break
            file_content.append(data)
            s.sendall(f"{OK}".encode('utf-8'))

        s.sendall(f"{OK}".encode('utf-8'))


