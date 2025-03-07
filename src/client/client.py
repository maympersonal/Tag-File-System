import os
import sys
import json
import time
import socket
import threading
import ipaddress
<<<<<<< Updated upstream:src/client/client.py
=======
import base64
import ssl
>>>>>>> Stashed changes:src/Client/client.py


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

"""# Método para descubrir otros nodos en la red enviando broadcasts
def discover_nodes():
    #Envía broadcasts de forma continua para descubrir otros nodos en la red.
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(2)
            s.sendto(b"DISCOVER", ('<broadcast>', DEFAULT_BROADCAST_PORT))
            try:
                data, addr = s.recvfrom(1024)
                parts = data.decode().split()
                if len(parts) == 2 and parts[0] == "NODE":
                    print(f"Nodo encontrado {addr[0]}")
                    return(addr[0])
            except socket.timeout:
                print(f"no encontró otros nodos activos. Reintentando...")
        time.sleep(10)  # Reintenta cada 10 segundos"""


"""def discover_nodes():
    #Envía broadcasts a la red de los servidores para descubrir nodos.
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(2)

            # Enviar broadcast a la red de los servidores
            s.sendto(b"DISCOVER", ('255.255.255', DEFAULT_BROADCAST_PORT))

            try:
                data, addr = s.recvfrom(1024)
                parts = data.decode().split()
                if len(parts) == 2 and parts[0] == "NODE":
                    print(f"✅ Nodo encontrado en {addr[0]}")
                    return addr[0]  # Retorna la IP del nodo encontrado
            except socket.timeout:
                print(f"⚠️ No encontró nodos activos en la red de servidores. Reintentando...")

        time.sleep(10)  # Reintenta cada 10 segundos"""


DISCOVERY_IP = "10.0.1.250"  # IP del discovery server
DISCOVERY_PORT = 6000  # Puerto donde escucha el discovery

def get_server_ip():
    """El cliente se conecta a 10.0.1.250 y recibe la IP de un servidor."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((DISCOVERY_IP, DISCOVERY_PORT))
            server_ip = s.recv(1024).decode().strip()
            print(f"✅ Servidor asignado: {server_ip}")
            return server_ip
        except Exception as e:
            print(f"❌ Error al conectar con el discovery server: {e}")
            return None


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
<<<<<<< Updated upstream:src/client/client.py
=======
        self.context = context
    
>>>>>>> Stashed changes:src/Client/client.py
        self.start()

    def start(self):
        """Muestra los comandos disponibles y espera la entrada del usuario"""
        info = """COMANDOS DISPONIBLES
add           <lista-archivos>  <lista-etiquetas>
delete        <consulta-etiqueta>
list          <consulta-etiqueta>
add-tags      <consulta-etiqueta>  <lista-etiquetas>
delete-tags   <consulta-etiqueta>  <lista-etiquetas>
download      <consulta-etiqueta>
inspect-tag   <etiqueta>
inspect-file  <nombre-archivo>
info          
exit          
"""
        print(info)

        

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

<<<<<<< Updated upstream:src/client/client.py
=======
                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
<<<<<<< Updated upstream:src/client/client.py

=======
                        s.sendall('CONECT'.encode('utf-8'))

                        data = s.recv(1024).decode('utf-8').split()

                        msg = decrypt_message(data[2],  SECRET_KEY)
                        s.sendall(msg.encode('utf-8'))
                        
                        # Esperar confirmacion
                        ack = s.recv(1024).decode('utf-8')
                        if ack != f"{OK}":
                            raise Exception("ACK negativo")
                        
                        s = self.context.wrap_socket(s, server_hostname="MAYM")
>>>>>>> Stashed changes:src/Client/client.py
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
        nueva_ip = get_server_ip()
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






if __name__ == "__main__":
    """
    Punto de entrada del cliente.
    Descubre automáticamente un nodo en la red o se conecta a una IP específica proporcionada como argumento.
    """
<<<<<<< Updated upstream:src/client/client.py
=======
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #context.set_ciphers("NULL")  # Sin cifrado
    context.load_verify_locations("cert.pem")
    
>>>>>>> Stashed changes:src/Client/client.py

    # Obtener la IP del cliente
    ip = socket.gethostbyname(socket.gethostname())
    print(f"Dirección IP del cliente: {ip}")

<<<<<<< Updated upstream:src/client/client.py
    # Si no se proporciona una IP, buscar un nodo en la red
    if len(sys.argv) == 1:
        print("Buscando nodos en la red...")
        target_ip =  get_server_ip()
        if target_ip:
            print(f"Dirección IP del servidor: {target_ip}")
            # Iniciar el cliente con la IP encontrada
            Client(None, target_ip=target_ip)
        else:
            print(f"Servidor no encontrado. No he podido conectarme...")
    # Conectar a una IP específica proporcionada como argumento
    elif len(sys.argv) == 2:
        target_ip = sys.argv[1]
        try:
            # Validar que la IP es válida
            ipaddress.ip_address(target_ip)
        except:
            raise Exception(f"{target_ip} no es una dirección IP válida")
        print(f"Dirección IP del servidor: {target_ip}")
        # Iniciar el cliente con la IP dada
        Client(None, target_ip=target_ip)
=======
    server_ip = find_active_server("10.0.11.1", "10.0.11.20", 8003)
    #server_ip = find_active_server("10.0.1.1", "10.0.1.20", 8003)
    if server_ip:
        print(f"🎯 Servidor disponible en: {server_ip}")
        Client(context, None, target_ip=server_ip,target_port=8003)
    else:
        print("⚠️ Ningún servidor está disponible en el rango.")
>>>>>>> Stashed changes:src/Client/client.py




        