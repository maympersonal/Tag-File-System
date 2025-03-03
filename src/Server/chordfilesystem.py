import json
import os
import sys
import socket
import threading
import ipaddress
import time
from const import *
from chordnodeobject import ChordNodeObject
from chordnode import ChordNode
from storage import Storage
from utils import *


class FileSystemNode(ChordNode):
    def __init__(self, ip: str):
        """
        Inicializa un nodo del sistema de archivos en la red Chord.

        Parámetros:
        ip (str): Dirección IP del nodo.
        """
        super().__init__(ip, update_replication=self.update_replication)

        self.data_port = DEFAULT_DATA_PORT
        self.Storage = Storage(ip)
        print("******** STORAGE **********")

        print("******** PADRE **********")
        # Iniciar servidores en hilos separados
        threading.Thread(target=self.start_data_server, daemon=True).start()

        self.green_ligth = True

        print("******** DATA **********")
        threading.Thread(target=self.start_query_server, daemon=True).start()
        print("******** QUERY **********")



    def _query_add(self, files_names: list[str], files_bins: list[bytes], tags: list[str]):
        """
        Agrega archivos al sistema de almacenamiento distribuido.

        Parámetros:
        files_names (list[str]): Lista de nombres de archivos.
        files_bins (list[bytes]): Lista de contenidos de archivos en binario.
        tags (list[str]): Lista de etiquetas asociadas a los archivos.

        Retorna:
        dict: Diccionario con los resultados de la operación.
        """
        response: dict = {
            'failed': [],
            'succeded': [],
            'failed_msg': [],
            'msg': "Acción completada"
        }

        def callback_func():
            # Copiar cada archivo en el sistema
            for i in range(len(files_names)):
                print("***************************************")
                file_name = files_names[i]
                file_bin = files_bins[i]
                success, fail_msg = self.copy(file_name, file_bin, tags)
                if not success:
                    response['failed'].append(file_name)
                    response['failed_msg'].append(fail_msg)
                else:
                    response['succeded'].append(file_name)
            print("**************FINAL CALBACK*************************")

        success = self._request(tags, files_names, [], callback=callback_func)
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response

    def _query_delete(self, query_tags: list[str]):
        """
        Elimina archivos basados en etiquetas.

        Parámetros:
        query_tags (list[str]): Lista de etiquetas utilizadas para encontrar los archivos a eliminar.

        Retorna:
        dict: Diccionario con los resultados de la operación.
        """
        response: dict = {
            'failed': [],
            'succeded': [],
            'failed_msg': [],
            'msg': "Acción completada"
        }

        def callback_func():
            files_to_delete = self.tag_query(query_tags)
            for file in files_to_delete:
                success, fail_msg = self.remove(file)
                if not success:
                    response['failed'].append(file)
                    response['failed_msg'].append(fail_msg)
                else:
                    response['succeded'].append(file)

        success = self._request([], [], query_tags, callback=callback_func)
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response

    def _query_list(self, query_tags: list[str]):
        """
        Lista archivos basados en etiquetas.

        Parámetros:
        query_tags (list[str]): Lista de etiquetas utilizadas para encontrar los archivos.

        Retorna:
        dict: Diccionario con los nombres de archivos y etiquetas asociadas.
        """
        response: dict = {
            'files_name': [],
            'tags': [],
            'msg': ""
        }

        def callback_func():
            files_to_list = self.tag_query(query_tags)
            for file in files_to_list:
                tags = self.inspect(file)
                response['files_name'].append(file)
                response['tags'].append(tags)

        success = self._request([], [], query_tags, callback=callback_func)
        response['msg'] = f"{len(response['files_name'])} archivos recuperados"
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response

    def _query_add_tags(self, query_tags: list[str], tags: list[str]):
        """
        Agrega etiquetas a archivos existentes.

        Parámetros:
        query_tags (list[str]): Lista de etiquetas utilizadas para encontrar los archivos.
        tags (list[str]): Lista de etiquetas a añadir.

        Retorna:
        dict: Diccionario con los resultados de la operación.
        """
        response: dict = {
            'failed': [],
            'succeded': [],
            'failed_msg': [],
            'msg': "Acción completada"
        }

        def callback_func():
            files_to_edit = self.tag_query(query_tags)
            for file in files_to_edit:
                success, fail_msg = self.add_tags(file, tags)
                if not success:
                    response['failed'].append(file)
                    response['failed_msg'].append(fail_msg)
                else:
                    response['succeded'].append(file)

        success = self._request(tags, [], query_tags, callback=callback_func)
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response



    def _query_delete_tags(self, query_tags: list[str], tags: list[str]):
        """
        Elimina etiquetas de archivos existentes.

        Parámetros:
        query_tags (list[str]): Lista de etiquetas utilizadas para encontrar los archivos.
        tags (list[str]): Lista de etiquetas a eliminar.

        Retorna:
        dict: Diccionario con los resultados de la operación.
        """
        response: dict = {
            'failed': [],
            'succeded': [],
            'failed_msg': [],
            'msg': "Acción completada"
        }

        def callback_func():
            files_to_edit = self.tag_query(query_tags)
            for file in files_to_edit:
                success, fail_msg = self.delete_tags(file, tags)
                if not success:
                    response['failed'].append(file)
                    response['failed_msg'].append(fail_msg)
                else:
                    response['succeded'].append(file)

        success = self._request(tags, [], query_tags, callback=callback_func)
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response


    def _query_download(self, query_tags: list[str]):
        """
        Descarga archivos basados en etiquetas.

        Parámetros:
        query_tags (list[str]): Lista de etiquetas utilizadas para encontrar los archivos.

        Retorna:
        dict: Diccionario con los nombres de archivos y su contenido binario.
        """
        response: dict = {
            'files_name': [],
            'bins': []
        }

        def callback_func():
            files_to_download = self.tag_query(query_tags)
            for file_name in files_to_download:
                response['files_name'].append(file_name)
                bin = self.download(file_name)
                response['bins'].append(bin)

        success = self._request([], [], query_tags, callback=callback_func)
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response



    def _query_inspect_tag(self, tag: str):
        """
        Inspecciona los archivos asociados a una etiqueta.

        Parámetros:
        tag (str): Etiqueta a inspeccionar.

        Retorna:
        dict: Diccionario con la lista de archivos asociados a la etiqueta.
        """
        response: dict = {
            'file_names': [],
            'tag': tag
        }

        def callback_func():
            files_by_tag = self.tag_query([tag])
            response['file_names'] = files_by_tag

        success = self._request([tag], [], [], callback=callback_func)
        response['msg'] = f"{len(response['file_names'])} archivos recuperados"
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response


    def _query_inspect_file(self, file_name: str):
        """
        Inspecciona las etiquetas asociadas a un archivo.

        Parámetros:
        file_name (str): Nombre del archivo a inspeccionar.

        Retorna:
        dict: Diccionario con la lista de etiquetas asociadas al archivo.
        """
        response: dict = {
            'file_name': file_name,
            'tags': []
        }

        def callback_func():
            tags_by_file = self.inspect(file_name)
            response['tags'] = tags_by_file

        success = self._request([], [file_name], [], callback=callback_func)
        response['msg'] = f"{len(response['tags'])} etiquetas recuperadas"
        if not success:
            response['msg'] = "Fallo de envío de respuesta"
        return response


    # Servidor de consultas
    def start_query_server(self):
        """
        Inicia el servidor que maneja las consultas de archivos y etiquetas.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, DEFAULT_QUERY_PORT))
            s.listen(10)

            while True:
                client_socket, client_address = s.accept()
                data = client_socket.recv(1024).decode('utf-8')
                if data == "CONECT":
                    msg = generate_password(12)
                    encrypted_msg = encrypt_message(msg, CLIENT_SECRET_KEY)
                    response = f"NODE {self.id} {encrypted_msg}".encode()  
                    client_socket.sendall(response) 
                    rmsg = client_socket.recv(1024).decode('utf-8')
                    if msg == rmsg:
                        client_socket.sendall(f"{OK}".encode('utf-8'))    
                        threading.Thread(target=self.handle_request, args=(client_socket, client_address), daemon=True).start()


    def handle_request(self, client_socket: socket.socket, client_addr):
        """
        Maneja las solicitudes de los clientes.

        Parámetros:
        client_socket (socket): Socket del cliente.
        client_addr: Dirección del cliente.
        """
        with client_socket:
            # Recibir operación
            operation = client_socket.recv(1024).decode('utf-8')

            print(f"{client_addr[0]} solicita {operation}")

            # Enviar ACK si la operación es válida
            if operation in {'add', 'delete', 'list', 'add-tags', 'delete-tags', 'download', 'inspect-tag', 'inspect-file'}:
                client_socket.sendall(f"{OK}".encode('utf-8'))
            else:
                client_socket.sendall(f"Operación no reconocida: {operation}".encode('utf-8'))
                return

            response = {}

            if operation == 'add':
                files_names = []
                files_bins = []

                while True:
                    file_name = client_socket.recv(1024).decode('utf-8')
                    print(f"****************** {file_name} *********************************")
                    if file_name == f"{END}":
                        print("****************** SALIENDO CICLO *********************************")
                        break

                    # Enviar ACK de recepción del nombre de archivo
                    client_socket.sendall(f"{OK}".encode('utf-8'))

                    file_bin = b''
                    end_file = f"{END_FILE}".encode('utf-8')
                    while True:
                        fragment = client_socket.recv(1024)
                        if end_file in fragment:
                            file_bin += fragment.split(end_file)[0]
                            break
                        else:
                            file_bin += fragment

                    # Enviar ACK de recepción del contenido del archivo
                    client_socket.sendall(f"{OK}".encode('utf-8'))

                    files_names.append(file_name)
                    files_bins.append(file_bin)

                client_socket.sendall(f"{OK}".encode('utf-8'))
                tags = client_socket.recv(1024).decode('utf-8').split(';')
                print(f"****************** ANTES *********************************")
                response = self._query_add(files_names, files_bins, tags)
                print(f"****************** {response} *********************************")
            elif operation == 'delete':
                query_tags = client_socket.recv(1024).decode('utf-8').split(';')
                response = self._query_delete(query_tags)

            elif operation == 'list':
                query_tags = client_socket.recv(1024).decode('utf-8').split(';')
                response = self._query_list(query_tags)

            elif operation == 'add-tags':
                query_tags = client_socket.recv(1024).decode('utf-8').split(';')
                client_socket.sendall(f"{OK}".encode('utf-8'))
                tags = client_socket.recv(1024).decode('utf-8').split(';')
                response = self._query_add_tags(query_tags, tags)

            elif operation == 'delete-tags':
                query_tags = client_socket.recv(1024).decode('utf-8').split(';')
                client_socket.sendall(f"{OK}".encode('utf-8'))
                tags = client_socket.recv(1024).decode('utf-8').split(';')
                response = self._query_delete_tags(query_tags, tags)

            elif operation == 'download':
                query_tags = client_socket.recv(1024).decode('utf-8').split(';')
                file_resp = self._query_download(query_tags)
                file_names = file_resp['files_name']
                file_bins = file_resp['bins']

                for i in range(len(file_names)):
                    client_socket.sendall(file_names[i].encode('utf-8'))

                    ack = client_socket.recv(1024).decode('utf-8')
                    if ack != f"{OK}": raise Exception("ACK negativo")

                    client_socket.sendall(file_bins[i])
                    client_socket.sendall(f"{END_FILE}".encode('utf-8'))

                    ack = client_socket.recv(1024).decode('utf-8')
                    if ack != f"{OK}": raise Exception("ACK negativo")

                client_socket.sendall(f"{END}".encode('utf-8'))

                # Esperar confirmación final
                ack = client_socket.recv(1024).decode('utf-8')
                if ack != f"{OK}": raise Exception("ACK negativo")
                return

            elif operation == 'inspect-tag':
                tag = client_socket.recv(1024).decode('utf-8')
                response = self._query_inspect_tag(tag)

            elif operation == 'inspect-file':
                file_name = client_socket.recv(1024).decode('utf-8')
                response = self._query_inspect_file(file_name)


            response_str = json.dumps(response)
            print(f"****************** {response_str} *********************************")
            client_socket.sendall(str(response_str).encode('utf-8'))

    def _pack_request(self, tags: list[str], files_names: list[str], query_tags: list[str]) -> bytes:
        """
        Empaqueta los datos de la solicitud de permiso en formato JSON.

        Parámetros:
        tags (list[str]): Lista de etiquetas.
        files_names (list[str]): Lista de nombres de archivos.
        query_tags (list[str]): Lista de etiquetas de consulta.

        Retorna:
        bytes: Cadena JSON codificada en bytes.
        """
        data = {
            'tags': tags,
            'files': files_names,
            'query_tags': query_tags
        }
        return json.dumps(data).encode('utf-8')

####################### Functions to use from upper layer ############################
    def tag_query(self, tags: list[str]) -> list[str]:
        """
        Retorna todos los nombres de archivos que contienen todas las etiquetas dadas.

        Parámetros:
        tags (list[str]): Lista de etiquetas a buscar.

        Retorna:
        list[str]: Lista de nombres de archivos que contienen todas las etiquetas especificadas.
        """
        all_files_list: list[list[str]] = []
        for tag in tags:
            tag_hash = getShaRepr(tag)
            owner = self.lookup(tag_hash)
            files_list = owner.retrieve_tag(tag)
            all_files_list.append(files_list)

        if all_files_list == []:
            return []

        # Intersección de todas las listas
        intersection = list(set.intersection(*map(set, all_files_list)))
        return intersection


    def copy(self, file_name: str, bin: bytes, tags: list[str]) -> bool:
        """
        Copia un archivo al sistema. Retorna False si el archivo ya existe.

        Parámetros:
        file_name (str): Nombre del archivo.
        bin (bytes): Contenido binario del archivo.
        tags (list[str]): Lista de etiquetas asociadas al archivo.

        Retorna:
        bool: True si la copia se realiza correctamente, False si el archivo ya existe.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        # Verificar si el archivo ya existe
        if file_owner.owns_file(file_name):
            return False, f"Un archivo llamado {file_name} ya existe en el sistema"

        # Copiar el archivo binario
        file_owner.insert_bin(file_name, bin)

        # Copiar el nombre del archivo y sus etiquetas
        self.handle_insert_file(file_name)
        for tag in tags:
            # Asociar cada etiqueta al archivo
            self.handle_append_tag(file_name, tag)

            # Asociar el nombre del archivo a cada etiqueta
            self.handle_insert_tag(tag)
            self.handle_append_file(tag, file_name)

        return True, ""


    def remove(self, file_name: str) -> bool:
        """
        Elimina un archivo del sistema. Retorna False si el archivo no existe.

        Parámetros:
        file_name (str): Nombre del archivo a eliminar.

        Retorna:
        bool: True si el archivo se elimina correctamente, False si no existe.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        # Verificar si el archivo no existe
        if not file_owner.owns_file(file_name):
            return False, f"No existe un archivo llamado {file_name} en el sistema"

        # Eliminar el archivo binario
        file_owner.delete_bin(file_name)

        # Eliminar el nombre del archivo de todas las etiquetas asociadas
        tags = file_owner.retrieve_file(file_name)
        for tag in tags:
            self.handle_remove_file(tag, file_name)

        # Eliminar el nombre del archivo y sus etiquetas asociadas
        self.handle_delete_file(file_name)

        return True, ""


    def inspect(self, file_name: str) -> list[str]:
        """
        Retorna la lista de etiquetas asociadas a un archivo dado.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        list[str]: Lista de etiquetas asociadas al archivo.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        tags = file_owner.retrieve_file(file_name)
        return tags


    def add_tags(self, file_name: str, tags: list[str]) -> bool:
        """
        Agrega etiquetas a un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tags (list[str]): Lista de etiquetas a agregar.

        Retorna:
        bool: True si las etiquetas se agregan correctamente, False si alguna ya existe.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        current_file_tags = self.inspect(file_name)
        for tag in tags:
            if tag in current_file_tags:
                return False, f"La etiqueta ({tag}) ya existe en este archivo"

        for tag in tags:
            # Agregar el nombre del archivo a las etiquetas
            self.handle_insert_tag(tag)
            self.handle_append_file(tag, file_name)

            # Agregar las etiquetas a la lista de etiquetas del archivo
            file_owner.append_tag(file_name, tag)

        return True, ""


    def delete_tags(self, file_name: str, tags: list[str]):
        """
        Elimina etiquetas de un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tags (list[str]): Lista de etiquetas a eliminar.

        Retorna:
        bool: True si las etiquetas se eliminan correctamente, False si alguna no existe.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        current_file_tags = self.inspect(file_name)
        for tag in tags:
            if tag not in current_file_tags:
                return False, f"La etiqueta ({tag}) no está asociada a este archivo"

        if len(current_file_tags) == len(tags):
            return False, "El archivo no puede quedarse sin etiquetas"

        for tag in tags:
            # Eliminar el nombre del archivo de la etiqueta
            self.handle_remove_file(tag, file_name)

            # Eliminar la etiqueta de la lista de etiquetas del archivo
            file_owner.remove_tag(file_name, tag)

        return True, ""


    def download(self, file_name: str) -> bytes:
        """
        Retorna el contenido binario de un archivo dado.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        bytes: Contenido binario del archivo.
        """
        file_name_hash = getShaRepr(file_name)
        file_owner = self.lookup(file_name_hash)

        bin = file_owner.retrieve_bin(file_name)
        return bin

    ######################################################################################






    def update_replication(self, delegate_data: bool = False, pull_data: bool = True,
                       assume_data: bool = False, is_pred: bool = True,
                       case_2: bool = False, assume_predpred: str = None):
        """
        Actualiza la replicación de datos en la red Chord.

        Parámetros:
        delegate_data (bool): Si se deben delegar datos al sucesor.
        pull_data (bool): Si se deben obtener datos del predecesor.
        assume_data (bool): Si se deben asumir datos de otro nodo.
        is_pred (bool): Si la operación se realiza con el predecesor.
        case_2 (bool): Caso especial de replicación.
        assume_predpred (str): Dirección IP del nodo predpred para asumir datos.
        """
        print(f"****** TAGS {len(self.Storage.tags)} ********")

        if delegate_data:
            if len(self.Storage.tags) > 0:
                self.Storage.delegate_data(self.pred.ip, self.succ.ip, self.pred.ip, case_2)

        if pull_data:
            if len(self.Storage.tags) > 0:
                if is_pred:
                    self.Storage.pull_replication(self.pred.ip, True)
                else:
                    self.Storage.pull_replication(self.succ.ip, False)

        if assume_data:
            succ_ip = self.succ.ip
            pred_ip = self.pred.ip if self.pred else None
            # print(f"Se llama a asumir con succ: {succ_ip} y pred: {pred_ip}")
            self.Storage.assume_data(succ_ip, pred_ip, assume_predpred)


    def request_data_handler(self, conn: socket.socket, addr, data: list):
        """
        Maneja las solicitudes de datos entrantes y ejecuta la operación correspondiente.

        Parámetros:
        conn (socket): Conexión del cliente.
        addr: Dirección del cliente.
        data (list): Datos recibidos de la solicitud.
        """
        response = None
        option = int(data[0])

        # Selección de la operación a ejecutar según la opción recibida
        if option == INSERT_TAG:
            response = self.handle_insert_tag(data[1])

        elif option == DELETE_TAG:
            response = self.handle_delete_tag(data[1])

        elif option == APPEND_FILE:
            response = self.handle_append_file(data[1], data[2])

        elif option == REMOVE_FILE:
            response = self.handle_remove_file(data[1], data[2])

        elif option == RETRIEVE_TAG:
            response = self.handle_retrieve_tag(data[1])

        elif option == INSERT_FILE:
            response = self.handle_insert_file(data[1])

        elif option == DELETE_FILE:
            response = self.handle_delete_file(data[1])

        elif option == APPEND_TAG:
            response = self.handle_append_tag(data[1], data[2])

        elif option == REMOVE_TAG:
            response = self.handle_remove_tag(data[1], data[2])

        elif option == RETRIEVE_FILE:
            response = self.handle_retrieve_file(data[1])

        elif option == OWNS_FILE:
            owns_file = self.Storage.owns_file(data[1])
            response = "1" if owns_file else "0"

        elif option == INSERT_BIN:

            """conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            conn.sendall(f"{OK}".encode('utf-8'))"""

            """bin_data = b''
            end_file = f"{END_FILE}".encode('utf-8')
            while True:
                fragment = conn.recv(1024)
                if end_file in fragment:
                    bin_data += fragment.split(end_file)[0]
                    break
                bin_data += fragment"""
            file_name, bin_data = recv_bin(conn)
            response = self.handle_insert_bin(file_name, bin_data)
            conn.sendall(response.encode('utf-8'))

        elif option == DELETE_BIN:
            response = self.handle_delete_bin(data[1])

        elif option == RETRIEVE_BIN:
            file_name = data[1]
            file_bin = self.Storage.retrieve_bin(file_name)
            file_bin = b''
            conn.sendall(file_bin)
            conn.sendall(f"{END_FILE}".encode('utf-8'))

        # Enviar respuesta si se generó alguna
        if response:
            response = response.encode('utf-8')
            conn.sendall(response)
        conn.close()

    def start_data_server(self):
        """
        Inicia el servidor que maneja las solicitudes de transferencia de datos en la red Chord.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.data_port))
            s.listen(10)

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024).decode('utf-8').split(',')

                # Maneja la solicitud en un nuevo hilo
                threading.Thread(target=self.request_data_handler, args=(conn, addr, data)).start()
    





    ############################### HANDLERS ###############################
    def handle_insert_tag(self, tag: str):
        """
        Inserta una nueva etiqueta en el sistema.

        Parámetros:
        tag (str): Etiqueta a insertar.

        Retorna:
        str: Mensaje de éxito o error.
        """
        tag_hash = getShaRepr(tag)
        owner = self.lookup(tag_hash)

        # Si este nodo es el propietario de la etiqueta
        if owner.id == self.id:
            if self.Storage.owns_tag(tag):
                return "OK,La etiqueta ya existe"
            else:
                self.Storage.store_tag(tag, self.succ.ip, self.pred.ip if self.pred else None)
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.insert_tag(tag)
            return response


    def handle_delete_tag(self, tag: str):
        """
        Elimina una etiqueta del sistema.

        Parámetros:
        tag (str): Etiqueta a eliminar.

        Retorna:
        str: Mensaje de éxito o error.
        """
        tag_hash = getShaRepr(tag)
        owner = self.lookup(tag_hash)

        # Si este nodo es el propietario de la etiqueta
        if owner.id == self.id:
            if not self.Storage.owns_tag(tag):
                return "OK,La clave no existe"
            else:
                self.Storage.delete_tag(tag, self.succ.ip, self.pred.ip if self.pred else None)
                return "OK,Dato eliminado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.delete_tag(tag)
            return response


    def handle_append_file(self, tag: str, file_name: str):
        """
        Agrega un archivo a una etiqueta.

        Parámetros:
        tag (str): Etiqueta a la que se agregará el archivo.
        file_name (str): Nombre del archivo.

        Retorna:
        str: Mensaje de éxito.
        """
        tag_hash = getShaRepr(tag)
        owner = self.lookup(tag_hash)

        # Si este nodo es el propietario de la etiqueta
        if owner.id == self.id:
            self.Storage.append_file(tag, file_name, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Dato agregado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.append_file(tag, file_name)
            return response


    def handle_remove_file(self, tag: str, file_name: str):
        """
        Elimina un archivo de una etiqueta.

        Parámetros:
        tag (str): Etiqueta de la que se eliminará el archivo.
        file_name (str): Nombre del archivo a eliminar.

        Retorna:
        str: Mensaje de éxito.
        """
        tag_hash = getShaRepr(tag)
        owner = self.lookup(tag_hash)

        # Si este nodo es el propietario de la etiqueta
        if owner.id == self.id:
            self.Storage.remove_file(tag, file_name, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Dato eliminado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.remove_file(tag, file_name)
            return response


    def handle_retrieve_tag(self, tag: str):
        """
        Recupera la lista de archivos asociados a una etiqueta.

        Parámetros:
        tag (str): Etiqueta a consultar.

        Retorna:
        list[str]: Lista de archivos asociados a la etiqueta.
        """
        return self.Storage.retrieve_tag(tag)


    def handle_insert_file(self, file_name: str):
        """
        Inserta un archivo en el sistema.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        str: Mensaje de éxito o error.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            if self.Storage.owns_file(file_name):
                return "OK,El archivo ya existe"
            else:
                self.Storage.store_file(file_name, self.succ.ip, self.pred.ip if self.pred else None)
                return "OK,Dato insertado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.insert_file(file_name)
            return response


    def handle_delete_file(self, file_name: str):
        """
        Elimina un archivo del sistema.

        Parámetros:
        file_name (str): Nombre del archivo a eliminar.

        Retorna:
        str: Mensaje de éxito o error.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            if not self.Storage.owns_file(file_name):
                return "OK,La clave no existe"
            else:
                self.Storage.delete_file(file_name, self.succ.ip, self.pred.ip if self.pred else None)
                return "OK,Dato eliminado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.delete_file(file_name)
            return response


    def handle_append_tag(self, file_name: str, tag: str):
        """
        Agrega una etiqueta a un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tag (str): Etiqueta a agregar.

        Retorna:
        str: Mensaje de éxito.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            self.Storage.append_tag(file_name, tag, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Dato agregado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.append_tag(file_name, tag)
            return response


    def handle_remove_tag(self, file_name: str, tag: str):
        """
        Elimina una etiqueta de un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tag (str): Etiqueta a eliminar.

        Retorna:
        str: Mensaje de éxito.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            self.Storage.remove_tag(file_name, tag, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Dato eliminado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.remove_tag(file_name, tag)
            return response


    def handle_retrieve_file(self, file_name: str):
        """
        Recupera la lista de etiquetas asociadas a un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        list[str]: Lista de etiquetas asociadas al archivo.
        """
        return self.Storage.retrieve_file(file_name)


    def handle_insert_bin(self, file_name: str, bin: bytes):
        """
        Inserta un archivo binario en el sistema.

        Parámetros:
        file_name (str): Nombre del archivo.
        bin (bytes): Contenido binario del archivo.

        Retorna:
        str: Mensaje de éxito.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            self.Storage.store_bin(file_name, bin, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Archivo binario insertado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.insert_bin(file_name, bin)
            return response


    def handle_delete_bin(self, file_name: str):
        """
        Elimina un archivo binario del sistema.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        str: Mensaje de éxito.
        """
        file_name_hash = getShaRepr(file_name)
        owner = self.lookup(file_name_hash)

        # Si este nodo es el propietario del archivo
        if owner.id == self.id:
            self.Storage.delete_bin(file_name, self.succ.ip, self.pred.ip if self.pred else None)
            return "OK,Archivo binario eliminado"
        # Si no es el propietario, reenviar la solicitud
        else:
            response = owner.delete_bin(file_name)
            return response
        
    def _request(self, tags, files_names, query_tags, callback):
        """
        Maneja la solicitud de forma distribuida sin permiso de líder.
        Si los recursos están localmente, ejecuta el callback.
        Si no, redirige la consulta al nodo responsable.
        """
        

        # 🔍 Obtener el nodo responsable de las etiquetas o archivos
        print(f"JSON: {json.dumps(tags + files_names + query_tags)}")
        key = getShaRepr(json.dumps(tags + files_names + query_tags))
        print(f"Key: {key}")
        responsible_node = self.lookup(key)
        print(f"Nodo responsable: {responsible_node}")

        node_ip = responsible_node.ip
        node_port = DEFAULT_DB_PORT

        # Enviar solicitud al líder
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((node_ip, node_port))

            # Enviar los datos empaquetados
            packed_request = self._pack_request(tags, files_names, query_tags)
            s.sendall(packed_request)

            # Esperar confirmación del líder
            """permission = s.recv(1024).decode('utf-8')
            print(f" ********** permiso: {permission}")
            if permission != "2": #f"{OK}":
                raise Exception(f"No se ha enviado permiso, el líder envió: {permission}")
            print(f"***************{permission}**********")"""
            # Llamar a la función de callback
            callback()
            print(f"*************** DESPUES **********")
            # Finalizar la operación
            s.sendall(f"{END}".encode('utf-8'))
            print(f"*************** ESTO ES EL FIN **********")

        """print("************* NODO RESPONSABLE*******************")
        print(responsible_node)
        # 🟢 Si el nodo actual es el responsable, resolver localmente
        if responsible_node.id == self.id:
            print("🔎 Recursos locales, ejecutando callback...")
            callback()  # Ejecutar el callback localmente

        # 🔴 Si otro nodo es el responsable, redirigir la consulta
        else:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((responsible_node.ip, self.chord_port))
                    s.sendall(json.dumps(request_payload).encode('utf-8'))
                    data = s.recv(4096)
                    response = json.loads(data.decode('utf-8'))
                    return response
            except Exception as e:
                print(f"❌ Error al contactar con el nodo responsable: {e}")
                return {
                    'msg': f"Error al contactar con el nodo responsable: {e}"
                }"""
        return True
    
        
    
