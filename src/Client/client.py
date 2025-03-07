import os
import sys
import json
import time
import socket
import threading
import ipaddress
import base64
import ssl


# Ruta para recursos del cliente
RESOURCES_PATH = "resources/"

# Códigos de respuesta y finalización
OK = 0
END = 100
END_FILE = 200

# Códigos de descubrimiento de nodos en la red
DISCOVER = 13
ENTRY_POINT = 14
DEFAULT_BROADCAST_PORT = 8255
MULTICAST_GROUP = '224.0.0.1'  # Dirección de multicast local

SECRET_KEY = 'H#@:D6qd4SYv'  # Clave secreta para el cifrado


def xor_encrypt_decrypt(message, key):
    """Cifra o descifra un mensaje usando XOR con una clave secreta."""
    encrypted_bytes = bytes([ord(char) ^ ord(key[i % len(key)]) for i, char in enumerate(message)])
    return encrypted_bytes

def encrypt_message(message, key):
    """Cifra un mensaje y lo codifica en Base64 para evitar caracteres no imprimibles."""
    encrypted_bytes = xor_encrypt_decrypt(message, key)
    return base64.b64encode(encrypted_bytes).decode()

def decrypt_message(encrypted_b64, key):
    """Descifra un mensaje codificado en Base64."""
    encrypted_bytes = base64.b64decode(encrypted_b64)
    decrypted_message = ''.join(chr(byte ^ ord(key[i % len(key)])) for i, byte in enumerate(encrypted_bytes))
    return decrypted_message


class Client:
    def __init__(self, context : ssl.SSLContext, self_disc_obj, target_ip=None, target_port=8003):
        """Inicializa el cliente con los parámetros de conexión y auto-descubrimiento"""
        self.ip = socket.gethostbyname(socket.gethostname())
        self.self_disc_object = self_disc_obj

        self.target_ip = target_ip
        self.target_port = target_port

        self.downloads_path = 'client/downloads'

        self.retry = False
        self.retry_cmd = ""
        self.context = context
    
        self.start()

    def start(self):
        """Muestra los comandos disponibles y espera la entrada del usuario"""
        
        info = """🎯COMANDOS DISPONIBLES
        📂add           <lista-archivos>  <lista-etiquetas>      - Agregar archivos con etiquetas
        🗑 delete        <consulta-etiqueta>                      - Eliminar archivos por etiqueta
        📜list          <consulta-etiqueta>                      - Listar archivos por etiqueta
        🏷️add-tags      <consulta-etiqueta>  <lista-etiquetas>   - Agregar etiquetas a archivos
        ✂️delete-tags   <consulta-etiqueta>  <lista-etiquetas>   - Eliminar etiquetas de archivos
        🔍inspect-tag   <etiqueta>                               - Inspeccionar archivos de una etiqueta
        📑inspect-file  <nombre-archivo>                         - Inspeccionar detalles de un archivo
        🔄reconnect                                              - Reconectar al servidor
         ℹ️ info                                                   - Mostrar este menú
        🚪 exit                                                  - Salir del cliente
        """
 

        print(info)
        print(f"Conectado a servidor: {self.target_ip}")
        

        while True:
            # Reintentar o pedir entrada del usuario
            if self.retry:
                user_input_str = self.retry_cmd
                self.retry = False
                self.retry_cmd = ""
            else:
                user_input_str = input("> ")

            if ',' in user_input_str:
                self.display_error("Error: No se permiten comas en nombres de archivos o etiquetas")
                continue

            user_input = user_input_str.split(" ")
            user_input = [x for x in user_input if x != ""]

            if len(user_input) == 0:
                self.display_error("Error: Entrada vacia")
                continue

            if len(user_input) == 1 and user_input[0] == "exit":
                break
            if len(user_input) == 1 and user_input[0] == "info":
                print(info)
                print(f"Conectado a servidor: {self.target_ip}")
                continue
            if len(user_input) == 1 and user_input[0] == "reconnect":
                nueva_ip = find_active_server("10.0.11.1", "10.0.11.20", 8003)
                self.target_ip = nueva_ip
                continue

            cmd = user_input[0]
            params = user_input[1:]


            if cmd == "add":
                if len(params) != 2: 
                    self.display_error(f"El comando 'add' requiere 2 parametros, pero se dieron {len(params)}")
                    continue

                files_name = params[0].split(';')
                files_bin, correct = self.load_bins(files_name)

                if not correct:
                    continue

                tags = params[1]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('add'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                    
                        if ack != f"{OK}":
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar cada archivo
                        for i in range(len(files_name)):
                            # Enviar nombre
                            s.sendall(files_name[i].encode('utf-8'))

                            # Esperar confirmacion
                            ack = s.recv(1024).decode('utf-8')
                            if ack != f"{OK}":
                                raise Exception("ACK negativo")

                            # Enviar contenido y marca de fin
                            s.sendall(files_bin[i])
                            s.sendall(f"{END_FILE}".encode('utf-8'))

                            # Esperar confirmacion
                            ack = s.recv(1024).decode('utf-8')
                            if ack != f"{OK}":
                                raise Exception("ACK negativo")

                        s.sendall(f"{END}".encode('utf-8'))

                        # Esperar confirmacion final
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")

                        # Enviar etiquetas
                        s.sendall(tags.encode('utf-8'))

                        print("ESPERANDO RESPUESTA")
                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        print("RESPUESTA RECIBIDA")
                        response = json.loads(response)
                        s.close()
                        self.show_results(response)
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")



            elif cmd == "delete":
                if len(params) != 1: 
                    self.display_error(f"El comando 'delete' requiere 1 parametro, pero se dieron {len(params)}")
                    continue

                tags_query = params[0]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        
                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('delete'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            print(ack) 
                            raise Exception("ACK negativo")

                        # Enviar etiquetas a eliminar
                        s.sendall(tags_query.encode('utf-8'))

                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        response = json.loads(response)
                        s.close()
                        self.show_results(response)
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")

            elif cmd == "list":
                if len(params) != 1: 
                    self.display_error(f"El comando 'list' requiere 1 parametro, pero se dieron {len(params)}")
                    continue

                tags_query = params[0]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('list'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar etiquetas para listar archivos
                        s.sendall(tags_query.encode('utf-8'))

                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        response = json.loads(response)
                        s.close()
                        self.show_list(response)
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")

            elif cmd == "add-tags":
                if len(params) != 2: 
                    self.display_error(f"El comando 'add-tags' requiere 2 parametros, pero se dieron {len(params)}")
                    continue

                tags_query = params[0]
                tags = params[1]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:


                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('add-tags'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar etiquetas de consulta
                        s.sendall(tags_query.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            raise Exception("ACK negativo")

                        # Enviar etiquetas a agregar
                        s.sendall(tags.encode('utf-8'))

                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        response = json.loads(response)
                        s.close()
                        self.show_results(response)
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")



            elif cmd == "delete-tags":
                if len(params) != 2: 
                    self.display_error(f"El comando 'delete-tags' requiere 2 parametros, pero se dieron {len(params)}")
                    continue

                tags_query = params[0]
                tags = params[1]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('delete-tags'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar etiquetas de consulta
                        s.sendall(tags_query.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            raise Exception("ACK negativo")

                        # Enviar etiquetas a eliminar
                        s.sendall(tags.encode('utf-8'))

                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        response = json.loads(response)
                        s.close()
                        self.show_results(response)
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")

            elif cmd == "download":
                if len(params) != 1: 
                    self.display_error(f"El comando 'download' requiere 1 parametro, pero se dieron {len(params)}")
                    continue

                tags_query = params[0]

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        print("Descargando...")
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('download'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar etiquetas de consulta
                        s.sendall(tags_query.encode('utf-8'))

                        # Esperar respuesta
                        while True:
                            file_name = s.recv(1024).decode('utf-8')
                            if file_name == f"{END}":
                                break

                            # Enviar confirmacion de recepcion del nombre del archivo
                            s.sendall(f"{OK}".encode('utf-8'))

                            file_content = b''
                            end_file = f"{END_FILE}".encode('utf-8')
                            while True:
                                fragment = s.recv(1024)
                                if end_file in fragment:
                                    file_content += fragment.split(end_file)[0]
                                    break
                                else:
                                    file_content += fragment

                            # Enviar confirmacion de recepcion del archivo
                            s.sendall(f"{OK}".encode('utf-8'))

                            # Guardar archivo en formato txt
                            self.save_file(file_name, file_content)

                        print("Descarga completada")
                        s.sendall(f"{OK}".encode('utf-8'))
                        s.close()
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")

            elif cmd == "inspect-tag":
                if len(params) != 1: 
                    self.display_error(f"El comando 'inspect-tag' requiere 1 parametro, pero se dieron {len(params)}")
                    continue

                tag: str = params[0]

                if len([tag]) != 1: 
                    self.display_error("El comando 'inspect-tag' solo es valido para recuperar nombres de archivos de una etiqueta especifica")
                    continue

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall('inspect-tag'.encode('utf-8'))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar etiqueta
                        s.sendall(tag.encode('utf-8'))

                        # Esperar respuesta
                        response = s.recv(1024).decode('utf-8')
                        response = json.loads(response)
                        s.close()
                        self.show_tag_file_relationship(response, 'files_by_tag')
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")



            elif cmd == "inspect-file":
                if len(params) != 1: 
                    self.display_error(f"El comando 'inspect-file' requiere 1 parametro, pero se dieron {len(params)}")
                    continue

                file_name: str = params[0]

                if len([file_name]) != 1: 
                    self.display_error("El comando 'inspect-file' solo es valido para recuperar etiquetas de un archivo especifico")
                    continue
                
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    

                        s.connect((self.target_ip, self.target_port))
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
                        # Enviar operacion
                        s.sendall("inspect-file".encode("utf-8"))

                        # Esperar confirmacion
                        ack = s.recv(1024).decode("utf-8")
                        if ack != f"{OK}": 
                            print(ack)
                            raise Exception("ACK negativo")

                        # Enviar nombre del archivo
                        s.sendall(file_name.encode("utf-8"))

                        # Esperar respuesta
                        response = s.recv(1024).decode("utf-8")
                        response = json.loads(response)
                        s.close()
                        self.show_tag_file_relationship(response, "tags_by_file")
                except Exception as e:
                    if isinstance(e, ConnectionRefusedError):
                        self.reconnect(user_input_str)
                        continue
                    else:
                        self.display_error("No se pudo completar la operacion exitosamente.")

            else:
                self.display_error("Comando no encontrado")
                continue

            print("")

    def reconnect(self, user_input):
        """
        Reintenta la conexión descubriendo una nueva IP de destino y reintentando el último comando.

        :param user_input: Último comando ingresado por el usuario.
        """
        nueva_ip = find_active_server("10.0.11.1", "10.0.11.20", 8003)
        self.target_ip = nueva_ip
        self.retry = True
        self.retry_cmd = user_input

    def display_error(self, msg: str):
        """
        Muestra un mensaje de error en la consola.

        :param msg: Mensaje de error a mostrar.
        """
        print("Error:", msg)

    def load_bins(self, nombres: list[str]) -> tuple[list[bytes], bool]:
        """
        Carga el contenido binario de una lista de archivos.

        :param nombres: Lista de nombres de archivos a cargar.
        :return: Una tupla con una lista de bytes y un booleano que indica éxito o fallo.
        """
        bins: list[bytes] = []

        # Verificar si los archivos existen
        for file_name in nombres:
            if not os.path.isfile(RESOURCES_PATH + file_name):
                self.display_error(f"Archivo {file_name} no encontrado")
                return [], False

        for file_name in nombres:
            contenido = []
            with open(RESOURCES_PATH + file_name, "rb") as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    contenido.append(data)
                bin_content = b"".join(contenido)
                bins.append(bin_content)

        return bins, True

    def show_list(self, data: dict):
        """
        Muestra en consola la lista de archivos y sus etiquetas asociadas.

        :param data: Diccionario con los nombres de los archivos y sus etiquetas.
        """
        mensaje: str = data["msg"]
        nombres_archivos: list = data["files_name"]
        etiquetas: list[list] = data["tags"]

        print(mensaje)
        for i in range(len(nombres_archivos)):
            print(f"{nombres_archivos[i]} : {etiquetas[i]}")

    def show_results(self, data: dict):
        """
        Muestra los resultados de una operación en el sistema.

        :param data: Diccionario con los mensajes de éxito y fallo de la operación.
        """
        mensaje: str = data["msg"]
        fallidos: list[str] = data["failed"]
        mensajes_fallidos: list[list] = data["failed_msg"]
        exitosos: list[str] = data["succeded"]

        print(mensaje)

        for archivo in exitosos:
            print(f"Exitoso: {archivo}")

        for i in range(len(fallidos)):
            print(f"Fallido: {fallidos[i]}\n  Motivo: {mensajes_fallidos[i]}")

    def save_file(self, nombre_archivo: str, contenido: bytes):
        """
        Guarda un archivo descargado en la carpeta de descargas.

        :param nombre_archivo: Nombre del archivo a guardar.
        :param contenido: Contenido binario del archivo.
        """
        carpeta_descargas = os.path.join(os.path.dirname(__file__), "downloads")

        ruta_archivo = os.path.join(carpeta_descargas, nombre_archivo)

        with open(ruta_archivo, "wb") as file:
            file.write(contenido)

    def show_tag_file_relationship(self, data: dict, modo: str):
        """
        Muestra la relación entre etiquetas y archivos.

        :param data: Diccionario con la información de archivos y etiquetas.
        :param modo: Modo de visualización, puede ser 'files_by_tag' o 'tags_by_file'.
        """
        if modo == "files_by_tag":
            nombres_archivos: list = data["file_names"]
            etiqueta: str = data["tag"]

            if not nombres_archivos:
                print(f"No se encontraron archivos para la etiqueta '{etiqueta}'.")
                return

            print(f"Archivos asociados con la etiqueta '{etiqueta}':")
            for nombre_archivo in nombres_archivos:
                print(nombre_archivo)

        elif modo == "tags_by_file":
            nombre_archivo: str = data["file_name"]
            etiquetas: list[str] = data["tags"]

            if not etiquetas:
                print(f"No se encontraron etiquetas para el archivo '{nombre_archivo}'.")
                return

            print(f"Etiquetas asociadas con el archivo '{nombre_archivo}':")
            for etiqueta in etiquetas:
                print(etiqueta)

        else:
            print(f"Modo invalido: {modo}")



def get_server_ip(ip):
    """Envía mensajes multicast para descubrir otros nodos en la red e integrarse en el anillo Chord."""

    multicast_group = (MULTICAST_GROUP, DEFAULT_BROADCAST_PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.settimeout(2)
        # 🔄 Enviar mensaje DISCOVER al grupo de multicast
        print(f"🌐 Cliente {ip} enviando mensaje DISCOVER en {MULTICAST_GROUP}")
        s.sendto(b"DISCOVER", multicast_group)
        data, addr = s.recvfrom(1024)
        print(f"📩 Recibido mensaje de {addr}: {data}")
        return addr[0]



import socket



def find_active_server(start_ip, end_ip, port, timeout=1):
    """
    Escanea un rango de direcciones IP buscando un servidor que responda en el puerto especificado.

    :param start_ip: IP inicial del rango (ej. "10.0.11.1")
    :param end_ip: IP final del rango (ej. "10.0.11.20")
    :param port: Puerto a probar en cada IP (ej. 8003)
    :param timeout: Tiempo máximo de espera por cada conexión (en segundos)
    :return: La IP del servidor encontrado o None si no se encontró ninguno
    """
    start_parts = list(map(int, start_ip.split('.')))
    end_parts = list(map(int, end_ip.split('.')))

    for last_octet in range(start_parts[3], end_parts[3] + 1):
        ip = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{last_octet}"
        
        try:
            with socket.create_connection((ip, port), timeout=timeout) as s:
                print(f"✅ Servidor encontrado en {ip}:{port}")
                return ip  # Devuelve la primera IP que responda correctamente
        
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass  # Ignora los errores y pasa a la siguiente IP

    print("❌ No se encontró ningún servidor en el rango especificado.")
    return None  # No se encontró ningún servidor

if __name__ == "__main__":
    """
    Punto de entrada del cliente.
    Descubre automáticamente un nodo en la red o se conecta a una IP específica proporcionada como argumento.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #context.set_ciphers("NULL")  # Sin cifrado
    context.load_verify_locations("cert.pem")
    

    # Obtener la IP del cliente
    ip = socket.gethostbyname(socket.gethostname())
    print(f"Dirección IP del cliente: {ip}")

    server_ip = find_active_server("10.0.11.1", "10.0.11.20", 8003)
    #server_ip = find_active_server("10.0.1.1", "10.0.1.20", 8003)
    if server_ip:
        print(f"🎯 Servidor disponible en: {server_ip}")
        Client(context, None, target_ip=server_ip,target_port=8003)
    else:
        print("⚠️ Ningún servidor está disponible en el rango.")


    #Client(None, target_ip="192.168.1.103",target_port=8003)