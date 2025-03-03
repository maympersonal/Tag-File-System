import os
import shutil
import socket
import threading
import json
import time
from utils import *
from const import *
from typing import Dict, List



class Storage:
    """
    Clase que gestiona el almacenamiento de etiquetas y archivos en un nodo Chord.
    """

    def __init__(self, storage_ip: str, storage_port: str = DEFAULT_DB_PORT) -> None:
        """
        Inicializa el almacenamiento del nodo.

        Parámetros:
        db_ip (str): Dirección IP del nodo.
        db_port (str): Puerto del nodo de almacenamiento (por defecto DEFAULT_DB_PORT).
        """
        self.storage_ip = storage_ip
        self.storage_port = storage_port

        # Diccionarios para etiquetas y sus archivos correspondientes
        self.tags: Dict[str, List[str]] = {}
        self.replicated_pred_tags: Dict[str, List[str]] = {}
        self.replicated_pred2_tags: Dict[str, List[str]] = {}

        # Diccionarios para archivos y sus etiquetas correspondientes
        self.files: Dict[str, List[str]] = {}
        self.replicated_pred_files: Dict[str, List[str]] = {}
        self.replicated_pred2_files: Dict[str, List[str]] = {}

        # Rutas de almacenamiento
        self.dir_path = f"Storage/{self.storage_ip}"
        self.tags_path = f"{self.dir_path}/tags.json"
        self.files_path = f"{self.dir_path}/files.json"
        self.replicated_pred_tags_path = f"{self.dir_path}/replicated_pred_tags.json"
        self.replicated_pred2_tags_path = f"{self.dir_path}/replicated_pred2_tags.json"
        self.replicated_pred_files_path = f"{self.dir_path}/replicated_pred_files.json"
        self.replicated_pred2_files_path = f"{self.dir_path}/replicated_pred2_files.json"
        self.bins_path = f"{self.dir_path}/bins"
        self.replicated_pred_bins_path = f"{self.dir_path}/replicated_pred_bins"
        self.replicated_pred2_bins_path = f"{self.dir_path}/replicated_pred2_bins"

        # Control de acceso secuencial
        self.lock = threading.Lock()
        # Configurar el almacenamiento inicial
        self.set_up_storage()

        # Iniciar el hilo para la recepción de datos
        threading.Thread(target=self._recv, daemon=True).start()

    def set_up_storage(self):
        """
        Configura el almacenamiento del nodo, creando los archivos y directorios necesarios.
        """
        print("Configurando almacenamiento...")

        # Crear todos los archivos y directorios si no existen
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        # Manejo de archivos de almacenamiento de etiquetas
        if os.path.isfile(self.tags_path):
            os.remove(self.tags_path)
        with open(self.tags_path, 'w') as json_file:
            json.dump(self.tags, json_file, indent=4)

        if os.path.isfile(self.files_path):
            os.remove(self.files_path)
        with open(self.files_path, 'w') as json_file:
            json.dump(self.files, json_file, indent=4)

        # Manejo de archivos de replicación de etiquetas
        if os.path.isfile(self.replicated_pred_tags_path):
            os.remove(self.replicated_pred_tags_path)
        with open(self.replicated_pred_tags_path, 'w') as json_file:
            json.dump(self.replicated_pred_tags, json_file, indent=4)

        if os.path.isfile(self.replicated_pred2_tags_path):
            os.remove(self.replicated_pred2_tags_path)
        with open(self.replicated_pred2_tags_path, 'w') as json_file:
            json.dump(self.replicated_pred2_tags, json_file, indent=4)

        # Manejo de archivos de replicación de archivos
        if os.path.isfile(self.replicated_pred_files_path):
            os.remove(self.replicated_pred_files_path)
        with open(self.replicated_pred_files_path, 'w') as json_file:
            json.dump(self.replicated_pred_files, json_file, indent=4)

        if os.path.isfile(self.replicated_pred2_files_path):
            os.remove(self.replicated_pred2_files_path)
        with open(self.replicated_pred2_files_path, 'w') as json_file:
            json.dump(self.replicated_pred2_files, json_file, indent=4)

        # Configuración de almacenamiento binario
        if os.path.exists(self.bins_path):
            shutil.rmtree(self.bins_path)
        os.makedirs(self.bins_path)

        if os.path.exists(self.replicated_pred_bins_path):
            shutil.rmtree(self.replicated_pred_bins_path)
        os.makedirs(self.replicated_pred_bins_path)

        if os.path.exists(self.replicated_pred2_bins_path):
            shutil.rmtree(self.replicated_pred2_bins_path)
        os.makedirs(self.replicated_pred2_bins_path)

        print("Configuración de almacenamiento exitosa")



    def save_tags(self):
        """
        Guarda las etiquetas en un archivo JSON.
        """
        with open(self.tags_path, 'w') as json_file:
            json.dump(self.tags, json_file, indent=4)


    def save_files(self):
        """
        Guarda los archivos en un archivo JSON.
        """
        with open(self.files_path, 'w') as json_file:
            json.dump(self.files, json_file, indent=4)


    def save_replicated_pred_tags(self):
        """
        Guarda las etiquetas replicadas del predecesor en un archivo JSON.
        """
        with open(self.replicated_pred_tags_path, 'w') as json_file:
            json.dump(self.replicated_pred_tags, json_file, indent=4)


    def save_replicated_pred2_tags(self):
        """
        Guarda las etiquetas replicadas del sucesor en un archivo JSON.
        """
        with open(self.replicated_pred2_tags_path, 'w') as json_file:
            json.dump(self.replicated_pred2_tags, json_file, indent=4)


    def save_replicated_pred_files(self):
        """
        Guarda los archivos replicados del predecesor en un archivo JSON.
        """
        with open(self.replicated_pred_files_path, 'w') as json_file:
            json.dump(self.replicated_pred_files, json_file, indent=4)


    def save_replicated_pred2_files(self):
        """
        Guarda los archivos replicados del sucesor en un archivo JSON.
        """
        with open(self.replicated_pred2_files_path, 'w') as json_file:
            json.dump(self.replicated_pred2_files, json_file, indent=4)


    def owns_tag(self, tag: str) -> bool:
        """
        Verifica si la etiqueta pertenece al nodo actual.

        Parámetros:
        tag (str): Nombre de la etiqueta.

        Retorna:
        bool: True si el nodo es dueño de la etiqueta, False en caso contrario.
        """
        with self.lock:
            return tag in self.tags


    def contains_tag(self, tag: str) -> bool:
        """
        Verifica si la etiqueta existe en el nodo actual o en sus datos replicados.

        Parámetros:
        tag (str): Nombre de la etiqueta.

        Retorna:
        bool: True si la etiqueta está en el nodo o en su replicación, False en caso contrario.
        """
        with self.lock:
            return tag in self.tags or tag in self.replicated_pred_tags

    def store_tag(self, tag: str, successor_ip: str, successor2_ip: str = None):
      """
      Almacena una etiqueta de manera secuencial y la replica en el sucesor y sucesor del sucesor.

      Parámetros:
      tag (str): Nombre de la etiqueta a almacenar.
      successor_ip (str): IP del nodo sucesor para replicación.
      successor2_ip (str): IP del nodo sucesor del sucesor para replicación.
      """
      with self.lock:
          if tag not in self.tags:
              self.tags[tag] = []
              print(f"Etiqueta almacenada: {tag}")

              # Replicación en el sucesor
              if successor_ip:
                  op = f"{REPLICATE_PRED_STORE_TAG}"
                  send_2(op, tag, successor_ip, self.storage_port)

              # Replicación en el sucesor del sucesor
              if successor2_ip:
                  op2 = f"{REPLICATE_PRED2_STORE_TAG}"
                  send_2(op2, tag, successor2_ip, self.storage_port)

          else:
              print(f"Etiqueta '{tag}' ya existe")


    def append_file(self, tag: str, file_name: str, successor_ip: str, successor2_ip: str = None):
        """
        Agrega un archivo a la lista de una etiqueta en el almacenamiento.

        Parámetros:
        tag (str): Nombre de la etiqueta.
        file_name (str): Nombre del archivo a agregar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            self.tags[tag].append(file_name)
            self.save_tags()
            msg = f"{tag};{file_name}"
            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_APPEND_FILE}"
                send_2(op, msg, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_APPEND_FILE}"
                send_2(op2, msg, successor2_ip, self.storage_port)




    def delete_tag(self, tag: str, successor_ip: str, successor2_ip: str = None):
        """
        Elimina una etiqueta del almacenamiento.

        Parámetros:
        tag (str): Nombre de la etiqueta a eliminar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            del self.tags[tag]
            self.save_tags()

            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_DELETE_TAG}"
                send_2(op, tag, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_DELETE_TAG}"
                send_2(op2, tag, successor2_ip, self.storage_port)



    def remove_file(self, tag: str, file_name: str, successor_ip: str, successor2_ip: str = None):
        """
        Elimina un archivo de la lista de una etiqueta en el almacenamiento.

        Parámetros:
        tag (str): Nombre de la etiqueta.
        file_name (str): Nombre del archivo a eliminar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            self.tags[tag].remove(file_name)
            if len(self.tags[tag]) == 0:
                del self.tags[tag]
            self.save_tags()
            msg = f"{tag};{file_name}"
            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_REMOVE_FILE}"
                send_2(op, msg, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_REMOVE_FILE}"
                send_2(op2, msg, successor2_ip, self.storage_port)




    def retrieve_tag(self, tag: str) -> str:
        """
        Recupera la lista de archivos asociados a una etiqueta dada.

        Parámetros:
        tag (str): Nombre de la etiqueta.

        Retorna:
        str: JSON con la lista de archivos asociados a la etiqueta.
        """
        with self.lock:
            data = {}
            if tag in self.tags:
                value = self.tags[tag]
                data["data"] = value
            else:
                data["data"] = []
            return json.dumps(data)


    ########################
    # FILES
    def owns_file(self, file_name: str) -> bool:
        """
        Verifica si el archivo pertenece al nodo actual.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        bool: True si el nodo es dueño del archivo, False en caso contrario.
        """
        with self.lock:
            return file_name in self.files


    def contains_file(self, file_name: str) -> bool:
        """
        Verifica si el archivo existe en el nodo actual o en sus datos replicados.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        bool: True si el archivo está en el nodo o en su replicación, False en caso contrario.
        """
        with self.lock:
            return file_name in self.files or file_name in self.replicated_pred_files


    def store_file(self, file_name: str, successor_ip: str, successor2_ip: str = None):
        """
        Agrega un nuevo archivo al almacenamiento con una lista vacía.

        Parámetros:
        file_name (str): Nombre del archivo a almacenar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            self.files[file_name] = []
            self.save_files()
            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_STORE_FILE}"
                send_2(op, file_name, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_STORE_FILE}"
                send_2(op2, file_name, successor2_ip, self.storage_port)




    def append_tag(self, file_name: str, tag: str, successor_ip: str, successor2_ip: str = None):
        """
        Agrega una etiqueta al almacenamiento de un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tag (str): Etiqueta a agregar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            self.files[file_name].append(tag)
            self.save_files()
            msg = f"{tag};{file_name}"
            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_APPEND_TAG}"
                send_2(op, msg, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_APPEND_TAG}"
                send_2(op2, msg, successor2_ip, self.storage_port)




    def delete_file(self, file_name: str, successor_ip: str, successor2_ip: str = None):
        """
        Elimina un archivo del almacenamiento.

        Parámetros:
        file_name (str): Nombre del archivo a eliminar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            del self.files[file_name]
            self.save_files()

            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_DELETE_FILE}"
                send_2(op, file_name, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_DELETE_FILE}"
                send_2(op2, file_name, successor2_ip, self.storage_port)




    def remove_tag(self, file_name: str, tag: str, successor_ip: str, successor2_ip: str = None):
        """
        Elimina una etiqueta del almacenamiento de un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.
        tag (str): Etiqueta a eliminar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            self.files[file_name].remove(tag)
            self.save_files()
            msg = f"{tag};{file_name}"
            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_REMOVE_TAG}"
                send_2(op, msg, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_REMOVE_TAG}"
                send_2(op2, msg, successor2_ip, self.storage_port)




    def retrieve_file(self, file_name: str) -> str:
        """
        Recupera la lista de etiquetas asociadas a un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        str: JSON con la lista de etiquetas asociadas al archivo.
        """
        with self.lock:
            data = {}
            if file_name in self.files:
                value = self.files[file_name]
                data["data"] = value
            else:
                data["data"] = []
            return json.dumps(data)


    #######################
    # BINS
    def store_bin(self, file_name: str, bin: bytes, successor_ip: str, successor2_ip: str = None):
        """
        Almacena el contenido de un archivo binario.

        Parámetros:
        file_name (str): Nombre del archivo.
        bin (bytes): Contenido binario del archivo.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            file_path = f"{self.bins_path}/{file_name}"
            with open(file_path, 'wb') as file:
                file.write(bin)

            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_STORE_BIN}"
                send_bin(op, file_name, bin, successor_ip, self.storage_port)  # Replicar en el predecesor

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_STORE_BIN}"
                send_bin(op, file_name, bin, successor2_ip, self.storage_port)  # Replicar en el predecesor



    def delete_bin(self, file_name: str, successor_ip: str, successor2_ip: str = None):
        """
        Elimina el contenido de un archivo binario.

        Parámetros:
        file_name (str): Nombre del archivo a eliminar.
        successor_ip (str): IP del nodo sucesor para replicación.
        predecesor_ip (str, opcional): IP del nodo predecesor para replicación.
        """
        with self.lock:
            file_path = f"{self.bins_path}/{file_name}"
            os.remove(file_path)

            # Replicación en el sucesor
            if successor_ip:
                op = f"{REPLICATE_PRED_DELETE_BIN}"
                send_2(op, file_name, successor_ip, self.storage_port)

            # Replicación en el sucesor del sucesor
            if successor2_ip:
                op2 = f"{REPLICATE_PRED2_DELETE_BIN}"
                send_2(op2, file_name, successor2_ip, self.storage_port)



    def retrieve_bin(self, file_name: str) -> bytes:
        """
        Recupera el contenido binario de un archivo.

        Parámetros:
        file_name (str): Nombre del archivo.

        Retorna:
        bytes: Contenido binario del archivo.
        """
        with self.lock:
            file_path = f"{self.bins_path}/{file_name}"

            content = []
            with open(file_path, 'rb') as file:
                while True:
                    fragment = file.read(1024)
                    if not fragment:
                        break
                    content.append(fragment)
                bin = b''.join(content)

        return bin


    # Función para asumir datos de un nodo fallido anterior
    def assume_data(self, successor_ip: str, new_predecessor_ip: str = None, assume_predpred: str = None):

        with self.lock:
            print(f"Asumiendo datos del predecesor....")
            # Asumir etiquetas replicadas
            self.tags.update(self.replicated_pred_tags)
            print(f"{len(self.replicated_pred_tags.items())} etiquetas asumidas del predecesor")
            self.save_tags()


            # Asumir archivos binarios replicados
            for k, _ in self.replicated_pred_files.items():
                # Leer archivo binario
                file_path = f"{self.replicated_pred_bins_path}/{k}"
                content = []
                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        content.append(data)
                    content = b''.join(content)

                # Escribir archivo binario en la nueva ubicación
                new_file_path = f"{self.bins_path}/{k}"
                with open(new_file_path, 'wb') as file:
                    file.write(content)

                # Eliminar la réplica del archivo binario
                os.remove(file_path)

            # Asumir archivos replicados
            self.files.update(self.replicated_pred_files)
            print(f"{len(self.replicated_pred_files.items())} archivos asumidos del predecesor")
            self.save_files()

            self.replicated_pred_tags = {}
            self.save_replicated_pred_tags()

            for k, _ in self.replicated_pred_files.items():
                # Leer archivo binario
                file_path = f"{self.replicated_pred_bins_path}/{k}"

                # Eliminar la réplica del archivo binario
                os.remove(file_path)

            self.replicated_pred_files = {}
            self.save_replicated_pred_files()

            self.replicated_pred2_tags = {}
            self.save_replicated_pred2_tags()
            for k, _ in self.replicated_pred2_files.items():
                # Leer archivo binario
                file_path = f"{self.replicated_pred2_bins_path}/{k}"

                # Eliminar la réplica del archivo binario
                os.remove(file_path)

            self.replicated_pred2_files = {}
            self.save_replicated_pred2_files()

            # Asumir datos del predecesor del predecesor si es necesario
            if assume_predpred:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((assume_predpred, self.storage_port))

                    # Solicitar datos replicados
                    s.sendall(f"{PULL_SUCC_REPLICA}".encode('utf-8'))

                    # Recibir etiquetas
                    tags_json_str = s.recv(1024).decode('utf-8')
                    tags_data = json.loads(tags_json_str)
                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir archivos
                    files_json_str = s.recv(1024).decode('utf-8')
                    files_data = json.loads(files_json_str)
                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir y escribir archivos binarios
                    recv_write_bins(s, self.bins_path)

                    # Sobrescribir etiquetas y archivos replicados
                    self.tags.update(tags_data)
                    self.files.update(files_data)
                    print(tags_data)
                    print(files_data)
                    self.save_tags()
                    self.save_files()

                    print(f"{len(tags_data.items())} etiquetas asumidas del predecesor del predecesor")
                    print(f"{len(files_data.items())} archivos asumidos del predecesor del predecesor")

                    s.close()


            # Notificar al sucesor que los datos han cambiado
            print(f"Avisando al sucesor: {successor_ip}")
            self.send_fetch_notification(successor_ip)

            # Obtener replicación del nuevo predecesor si existe
            if new_predecessor_ip:
                self.pull_replication(new_predecessor_ip)
                self.pull_replication(new_predecessor_ip, False)

                #self.send_fetch_notification(new_predecessor_ip, False)


    # Función para delegar datos al nuevo nodo propietario
    def delegate_data(self, new_owner_ip: str, successor_ip: str, predecessor_ip: str, case_2: bool):
        with self.lock:
            print(f"Delegando datos a {new_owner_ip}")

            i_t = 0
            i_f = 0

            new_owner_id = getShaRepr(new_owner_ip)
            my_id = getShaRepr(self.storage_ip)

            tags_to_delegate = {}
            for k, v in self.tags.items():
                tag_hash = getShaRepr(k)
                if not inbetween(tag_hash, new_owner_id, my_id):
                    tags_to_delegate[k] = v
                    i_t += 1

            files_to_delegate = {}
            for k, v in self.files.items():
                file_name_hash = getShaRepr(k)
                if not inbetween(file_name_hash, new_owner_id, my_id):
                    files_to_delegate[k] = v
                    i_f += 1

            # Enviar datos al nuevo propietario
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                s.connect((new_owner_ip, self.storage_port))
                s.sendall(f"{PUSH_DATA}".encode('utf-8'))
                ack = s.recv(1024).decode('utf-8')
                if ack != f"{OK}":
                    raise Exception("ACK negativo")

                # Enviar etiquetas
                tags_json_str = json.dumps(tags_to_delegate)
                s.sendall(tags_json_str.encode('utf-8'))

                ack = s.recv(1024).decode('utf-8')
                if ack != f"{OK}":
                    raise Exception("ACK negativo")

                # Enviar archivos
                files_json_str = json.dumps(files_to_delegate)
                s.sendall(files_json_str.encode('utf-8'))

                ack = s.recv(1024).decode('utf-8')
                if ack != f"{OK}":
                    raise Exception("ACK negativo")

                # Enviar archivos binarios
                send_bins(s, files_to_delegate, self.bins_path)
                ack = s.recv(1024).decode('utf-8')
                if ack != f"{OK}":
                    raise Exception("ACK negativo")

                s.close()

            print(f"{i_t} etiquetas delegadas")
            print(f"{i_f} archivos delegados")

            # Eliminar datos que ya no corresponden al nodo actual
            for k in tags_to_delegate.keys():
                del self.tags[k]
            for k in files_to_delegate.keys():
                del self.files[k]
            for k in files_to_delegate.keys():
                file_path = f"{self.bins_path}/{k}"
                os.remove(file_path)

            self.save_tags()
            self.save_files()

            # Notificar al sucesor que tiene nuevos datos
            self.send_fetch_notification(successor_ip)


    # Función para obtener todos los datos del nodo predecesor y almacenarlos en el diccionario de replicación
    def pull_replication(self, owner_ip: str, is_pred: bool = True):
        """
        Obtiene los datos replicados de un nodo (predecesor o sucesor) y los almacena.

        Parámetros:
        owner_ip (str): IP del nodo del cual se extraerán los datos replicados.
        is_pred (bool): Indica si se trata del predecesor (True) o del sucesor (False).
        """
        with self.lock:
            if is_pred:
                print(f"Extrayendo replicación de {owner_ip} : {self.storage_port}, con is_pred=True")

                # Eliminar las réplicas actuales
                for k, _ in self.replicated_pred_files.items():
                    os.remove(f"{self.replicated_pred_bins_path}/{k}")
                self.replicated_pred_tags = {}
                self.replicated_pred_files = {}
                time.sleep(20)
                # Obtener las nuevas réplicas del predecesor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((owner_ip, self.storage_port))

                    # Solicitar replicación
                    s.sendall(f"{PULL_REPLICATION}".encode('utf-8'))

                    # Recibir etiquetas
                    tags_json_str = s.recv(1024).decode('utf-8')
                    tags_data = json.loads(tags_json_str)

                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir archivos
                    files_json_str = s.recv(1024).decode('utf-8')
                    files_data = json.loads(files_json_str)

                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir y escribir archivos binarios
                    recv_write_bins(s, self.replicated_pred_bins_path)

                    # Sobrescribir etiquetas y archivos replicados
                    self.replicated_pred_tags = tags_data
                    self.replicated_pred_files = files_data

                    self.save_replicated_pred_tags()
                    self.save_replicated_pred_files()

                    s.close()

            else:
                print(f"Extrayendo replicación de {owner_ip}, con is_pred=False")

                # Eliminar las réplicas actuales
                for k, _ in self.replicated_pred2_files.items():
                    os.remove(f"{self.replicated_pred2_bins_path}/{k}")
                self.replicated_pred2_tags = {}
                self.replicated_pred2_files = {}

                # Obtener las nuevas réplicas del sucesor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((owner_ip, self.storage_port))

                    # Solicitar replicación
                    s.sendall(f"{PULL_PRED_REPLICA}".encode('utf-8'))

                    # Recibir etiquetas
                    tags_json_str = s.recv(1024).decode('utf-8')
                    tags_data = json.loads(tags_json_str)

                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir archivos
                    files_json_str = s.recv(1024).decode('utf-8')
                    files_data = json.loads(files_json_str)

                    s.sendall(f"{OK}".encode('utf-8'))

                    # Recibir y escribir archivos binarios
                    recv_write_bins(s, self.replicated_pred2_bins_path)

                    # Sobrescribir etiquetas y archivos replicados
                    self.replicated_pred2_tags = tags_data
                    self.replicated_pred2_files = files_data

                    self.save_replicated_pred2_tags()
                    self.save_replicated_pred2_files()

                    s.close()


    # Función para notificar a los nodos replicados que los datos han cambiado
    def send_fetch_notification(self, target_ip: str, is_pred: bool = True):
        """
        Envía una notificación a un nodo para que actualice su replicación.

        Parámetros:
        target_ip (str): IP del nodo al que se notificará.
        is_pred (bool): Indica si se trata del predecesor (True) o del sucesor (False).
        """
        is_pred_str = "1" if is_pred else "0"
        threading.Thread(target=send_2, args=(f"{FETCH_REPLICA}", f"{self.storage_ip};{is_pred_str}", target_ip, self.storage_port), daemon=True).start()


    def _recv(self):
        """
        Escucha conexiones entrantes y maneja las solicitudes recibidas.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.storage_ip, self.storage_port))
        sock.listen(10)

        while True:
            conn, _ = sock.accept()
            data = conn.recv(1024).decode('utf-8')
            threading.Thread(target=self._handle_recv, args=(conn, data)).start()


    def _handle_recv(self, conn: socket.socket, data: str):
        """
        Maneja las solicitudes entrantes relacionadas con la replicación y almacenamiento de datos.

        Parámetros:
        conn (socket): Conexión del socket con el nodo solicitante.
        data (str): Mensaje recibido con la operación a ejecutar.
        """
        # with self.lock:
        print("**********************************************************************")
        print(data)
        # Operaciones con el predecesor
        if data == f"{REPLICATE_PRED_STORE_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag = conn.recv(1024).decode('utf-8')
            self.replicated_pred_tags[tag] = []
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_tags()

        elif data == f"{REPLICATE_PRED_APPEND_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred_tags[tag].append(file_name)
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_tags()

        elif data == f"{REPLICATE_PRED_DELETE_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag = conn.recv(1024).decode('utf-8')
            del self.replicated_pred_tags[tag]
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_tags()

        elif data == f"{REPLICATE_PRED_REMOVE_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred_tags[tag].remove(file_name)
            if not self.replicated_pred_tags[tag]:
                del self.replicated_pred_tags[tag]
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_tags()

        elif data == f"{REPLICATE_PRED_STORE_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            self.replicated_pred_files[file_name] = []
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_files()

        elif data == f"{REPLICATE_PRED_APPEND_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred_files[file_name].append(tag)
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_files()

        elif data == f"{REPLICATE_PRED_DELETE_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            del self.replicated_pred_files[file_name]
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_files()

        elif data == f"{REPLICATE_PRED_REMOVE_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred_files[file_name].remove(tag)
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred_files()

        elif data == f"{REPLICATE_PRED_STORE_BIN}":
            """conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            conn.sendall(f"{OK}".encode('utf-8'))
            bin_data = conn.recv(1024)"""
            file_name, bin_data = recv_bin(conn)
            with open(f"{self.replicated_pred_bins_path}/{file_name}", 'wb') as file:
                file.write(bin_data)
            conn.sendall(f"{OK}".encode('utf-8'))

        elif data == f"{REPLICATE_PRED2_STORE_BIN}":
            """conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            conn.sendall(f"{OK}".encode('utf-8'))
            bin_data = conn.recv(1024)"""
            file_name, bin_data = recv_bin(conn)
            with open(f"{self.replicated_pred2_bins_path}/{file_name}", 'wb') as file:
                file.write(bin_data)
            conn.sendall(f"{OK}".encode('utf-8'))

        elif data == f"{REPLICATE_PRED_DELETE_BIN}":
            conn.sendall(f"{OK}".encode('utf-8'))
            file_name = conn.recv(1024).decode('utf-8')
            os.remove(f"{self.replicated_pred_bins_path}/{file_name}")
            conn.sendall(f"{OK}".encode('utf-8'))

        # Operaciones con el sucesor
        elif data == f"{REPLICATE_PRED2_STORE_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag = conn.recv(1024).decode('utf-8')
            self.replicated_pred2_tags[tag] = []
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred2_tags()

        elif data == f"{REPLICATE_PRED2_APPEND_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred2_tags[tag].append(file_name)
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred2_tags()

        elif data == f"{REPLICATE_PRED2_DELETE_TAG}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag = conn.recv(1024).decode('utf-8')
            del self.replicated_pred2_tags[tag]
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred2_tags()

        elif data == f"{REPLICATE_PRED2_REMOVE_FILE}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tag, file_name = conn.recv(1024).decode('utf-8').split(';')
            self.replicated_pred2_tags[tag].remove(file_name)
            if not self.replicated_pred2_tags[tag]:
                del self.replicated_pred2_tags[tag]
            conn.sendall(f"{OK}".encode('utf-8'))
            self.save_replicated_pred2_tags()

        # Solicitudes de replicación
        elif data == f"{PULL_REPLICATION}":
            if len(self.tags) > 0:
                print(f"******** {len(self.tags)} **********")
                conn.sendall(json.dumps(self.tags).encode('utf-8'))
                conn.recv(1024)  # Esperar ACK
                print(f"******** {self.files} **********")
                conn.sendall(json.dumps(self.files).encode('utf-8'))
                conn.recv(1024)  # Esperar ACK
                send_bins(conn, self.files, self.bins_path)

        elif data == f"{PULL_PRED_REPLICA}":
            if len(self.replicated_pred_tags):
                conn.sendall(json.dumps(self.replicated_pred_tags).encode('utf-8'))
                conn.recv(1024)  # Esperar ACK
                conn.sendall(json.dumps(self.replicated_pred_files).encode('utf-8'))
                conn.recv(1024)  # Esperar ACK
                send_bins(conn, self.replicated_pred_files, self.replicated_pred_bins_path)

        elif data == f"{FETCH_REPLICA}":
            conn.sendall(f"{OK}".encode('utf-8'))
            ip, is_pred = conn.recv(1024).decode('utf-8').split(';')
            self.pull_replication(ip, is_pred == "1")
            conn.sendall(f"{OK}".encode('utf-8'))
        elif data == f"{PUSH_DATA}":
            conn.sendall(f"{OK}".encode('utf-8'))
            tags_json_str = conn.recv(1024).decode('utf-8')
            tags_received = json.loads(tags_json_str)
            self.tags.update(tags_received)
            self.save_tags()
            conn.sendall(f"{OK}".encode('utf-8'))
            files_json_str = conn.recv(1024).decode('utf-8')
            files_received = json.loads(files_json_str)
            self.files.update(files_received)
            self.save_files()
            conn.sendall(f"{OK}".encode('utf-8'))
            recv_write_bins(conn, self.bins_path)
            conn.sendall(f"{OK}".encode('utf-8'))
        conn.close()
