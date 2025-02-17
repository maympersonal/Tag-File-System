import json
import socket
from const import *
from utils import *

class ChordNodeObject:
    def __init__(self, ip: str, chord_port: int = DEFAULT_NODE_PORT, data_port: int = DEFAULT_DATA_PORT):
        """ 
        Inicializa un objeto de nodo Chord.
        
        Parámetros:
        ip (str): Dirección IP del nodo.
        chord_port (int): Puerto utilizado para la comunicación Chord.
        data_port (int): Puerto utilizado para la comunicación de datos.
        """
        self.id = getShaRepr(ip)
        self.ip = ip
        self.chord_port = chord_port
        self.data_port = data_port

    # Método interno para enviar datos al nodo referenciado (este nodo)
    def _send_chord_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.chord_port))
                s.sendall(f'{op},{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            return b''

    # Método para encontrar el predecesor de un ID dado
    def find_predecessor(self, id: int) -> 'ChordNodeObject':
        response = self._send_chord_data(FIND_PREDECESSOR, str(id)).decode('utf-8').split(',')
        ip = response[1]
        return ChordNodeObject(ip, self.chord_port)

    # Propiedad para obtener el sucesor del nodo actual
    @property
    def succ(self) -> 'ChordNodeObject':
        response = self._send_chord_data(GET_SUCCESSOR).decode('utf-8').split(',')
        return ChordNodeObject(response[1], self.chord_port)

    # Propiedad para obtener el predecesor del nodo actual
    @property
    def pred(self) -> 'ChordNodeObject':
        response = self._send_chord_data(GET_PREDECESSOR).decode('utf-8').split(',')
        return ChordNodeObject(response[1], self.chord_port)

    # Método para notificar al nodo actual sobre otro nodo
    def notify(self, node: 'ChordNodeObject'):
        self._send_chord_data(NOTIFY, f'{node.id},{node.ip}')

    # Notificación inversa para informar sobre el nuevo sucesor
    def reverse_notify(self, node: 'ChordNodeObject'):
        self._send_chord_data(REVERSE_NOTIFY, f'{node.id},{node.ip}')

    # Notificación de que el nodo ya no está solo
    def not_alone_notify(self, node: 'ChordNodeObject'):
        self._send_chord_data(NOT_ALONE_NOTIFY, f'{node.id},{node.ip}')

    # Método para comprobar si el predecesor está vivo
    def check_node(self) -> bool:
        response = self._send_chord_data(CHECK_NODE)
        return response != b'' and len(response.decode('utf-8')) > 0

    # Método para obtener el líder de la red
    def get_leader(self) -> str:
        leader = self._send_chord_data(GET_LEADER).decode('utf-8').split(',')[1]
        return leader

    # Método para buscar un nodo responsable de un ID dado
    def lookup(self, id: int):
        response = self._send_chord_data(LOOKUP, str(id)).decode('utf-8').split(',')
        return ChordNodeObject(response[1], self.chord_port)

    # ========================== Nodo de Datos ==============================

    # Método interno para enviar datos al nodo referenciado (este nodo)
    def _send_data_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.data_port))
                s.sendall(f'{op},{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            return b''

    def insert_tag(self, tag: str) -> str:
        """ Inserta una etiqueta en el sistema. Si ya existe, no lanza error. """
        response = self._send_data_data(INSERT_TAG, tag).decode('utf-8')
        return response

    def delete_tag(self, tag: str) -> str:
        """ Elimina una etiqueta del sistema. Si no existe, no lanza error. """
        response = self._send_data_data(DELETE_TAG, tag).decode('utf-8')
        return response

    def append_file(self, tag: str, file_name: str):
        """ Añade un archivo a una etiqueta. """
        response = self._send_data_data(APPEND_FILE, f"{tag},{file_name}").decode('utf-8')
        return response

    def remove_file(self, tag: str, file_name: str):
        """ Elimina un archivo de una etiqueta. """
        response = self._send_data_data(REMOVE_FILE, f"{tag},{file_name}").decode('utf-8')
        return response

    def retrieve_tag(self, tag: str) -> list[str]:
        """ Recupera la lista de archivos asociados a una etiqueta (solo funciona desde el nodo propietario). """
        json_str_data = self._send_data_data(RETRIEVE_TAG, tag).decode('utf-8')
        json_data = json.loads(json_str_data)
        return json_data['data']

    def insert_file(self, file_name: str) -> str:
        """ Inserta un archivo en el sistema. Si ya existe, no lanza error. """
        response = self._send_data_data(INSERT_FILE, file_name).decode('utf-8')
        return response

    def delete_file(self, file_name: str) -> str:
        """ Elimina un archivo del sistema. Si no existe, no lanza error. """
        response = self._send_data_data(DELETE_FILE, file_name).decode('utf-8')
        return response

    def append_tag(self, file_name: str, tag: str):
        """ Añade una etiqueta a un archivo. """
        response = self._send_data_data(APPEND_TAG, f"{file_name},{tag}").decode('utf-8')
        return response

    def remove_tag(self, file_name: str, tag: str):
        """ Elimina una etiqueta de un archivo. """
        response = self._send_data_data(REMOVE_TAG, f"{file_name},{tag}").decode('utf-8')
        return response

    def retrieve_file(self, file_name: str) -> list[str]:
        """ Recupera la lista de etiquetas asociadas a un archivo (solo funciona desde el nodo propietario). """
        json_str_data = self._send_data_data(RETRIEVE_FILE, file_name).decode('utf-8')
        json_data = json.loads(json_str_data)
        return json_data['data']

    def owns_file(self, file_name: str):
        """ Retorna '1' si el nodo es propietario del archivo, de lo contrario '0'. """
        response = self._send_data_data(OWNS_FILE, file_name).decode('utf-8')
        return response == "1"

    # Debe ser llamado desde el nodo propietario
    def insert_bin(self, file_name: str, bin: bytes):
        """ Inserta un archivo binario en el sistema. """
        response = send_bin(f"{INSERT_BIN}", file_name, bin, self.ip, self.data_port, end_msg=True)
        return response

    def delete_bin(self, file_name: str):
        """ Elimina un archivo binario del sistema. """
        response = self._send_data_data(f"{DELETE_BIN}", file_name)
        return response

    def retrieve_bin(self, file_name: str):
        """ Recupera el contenido binario de un archivo. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.data_port))
            s.sendall(f"{RETRIEVE_BIN},{file_name}".encode('utf-8'))

            file_bin = b''
            end_file = f"{END_FILE}".encode('utf-8')
            while True:
                fragment = s.recv(1024)
                if end_file in fragment:
                    file_bin += fragment.split(end_file)[0]
                    break
                else:
                    file_bin += fragment
            s.close()
            return file_bin

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.chord_port}'

    def __repr__(self) -> str:
        return str(self)
