import json
import socket
import threading
import time
from const import *


# mensajes del broadcast
DEFAULT = 0
ELECTION = 1
OK = 2
LEADER = 3

PORT = 8080


class Resources:
    """
    Representa los recursos en términos de etiquetas y archivos.
    """
    def __init__(self, tags: list[str], files: list[str]) -> None:
        self.tags: set = set(tags)
        self.files: set = set(files)

    def use(self, other: 'Resources') -> bool:
        """
        Verifica si hay intersección entre los recursos actuales y otros recursos.

        Parámetros:
        other (Resources): Otro objeto de recursos a comparar.

        Retorna:
        bool: True si hay recursos compartidos, False en caso contrario.
        """
        return len(self.tags.intersection(other.tags)) != 0 or len(self.files.intersection(other.files)) != 0
    
    def adopt(self, other: 'Resources') -> None:
        """
        Adopta los recursos de otro conjunto de recursos.

        Parámetros:
        other (Resources): Otro objeto de recursos a adoptar.
        """
        self.tags = self.tags.union(other.tags)
        self.files = self.files.union(other.files)

    def release(self, other: 'Resources') -> None:
        """
        Libera los recursos que coinciden con otro conjunto de recursos.

        Parámetros:
        other (Resources): Otro objeto de recursos a liberar.
        """
        self.tags = self.tags.difference(other.tags)
        self.files = self.files.difference(other.files)
    


class RequestNode:
    """
    Representa una solicitud de nodo que maneja una operación basada en recursos.
    """
    def __init__(self, sock: socket.socket, tags: list[str], files: list[str], query_tags: list[str], qt_func, end_func) -> None:
        """
        Inicializa un nodo de solicitud con los recursos necesarios.

        Parámetros:
        sock (socket.socket): Socket asociado a la solicitud.
        tags (list[str]): Lista de etiquetas solicitadas.
        files (list[str]): Lista de archivos solicitados.
        query_tags (list[str]): Lista de etiquetas de consulta.
        qt_func (function): Función para obtener archivos basados en las etiquetas de consulta.
        end_func (function): Función de finalización cuando la solicitud termina.
        """
        self.sock = sock
        self.green_light = False

        resource_tags = set(tags).union(set(query_tags))
        resource_files = set(qt_func(query_tags))
        self.resources = Resources(resource_tags, resource_files)

        self.end_func = end_func

    def set_green_light(self):
        """
        Permite que la solicitud continúe cuando los recursos están disponibles.
        """
        self.green_light = True

    def start(self):
        """
        Espera hasta recibir luz verde y luego maneja la solicitud.
        """
        while not self.green_light:
            time.sleep(0.5)

        # Enviar señal de aprobación al cliente
        self.sock.sendall(f"{OK}".encode('utf-8'))

        ack = self.sock.recv(1024).decode('utf-8')
        if ack != f"{END}":
            print("No se recibió confirmación de finalización de la operación")

        # Llamar a la función de finalización para liberar recursos
        self.end_func(self)




class Leader:
    """
    Clase que representa al líder del sistema, encargado de manejar solicitudes y recursos.
    """
    def __init__(self, ip: str, query_tag_function, port: int = DEFAULT_LEADER_PORT):
        """
        Inicializa el líder del sistema.

        Parámetros:
        ip (str): Dirección IP del líder.
        query_tag_function (función): Función para consultar etiquetas.
        port (int): Puerto en el que el líder escucha solicitudes (por defecto DEFAULT_LEADER_PORT).
        """
        self.ip = ip
        self.port = port
        self.query_tag_func = query_tag_function

        self.blocked_resources: Resources = Resources([], [])
        self.waiting_queue: list[RequestNode] = []

        threading.Thread(target=self._start_leader_server, daemon=True).start()

    def block_resources(self, resources: Resources):
        """Bloquea los recursos especificados para evitar conflictos de acceso."""
        self.blocked_resources.adopt(resources)

    def release_resources(self, resources: Resources):
        """Libera los recursos previamente bloqueados."""
        self.blocked_resources.release(resources)

    def join(self, node: RequestNode):
        """
        Agrega un nodo a la lista de solicitudes pendientes.

        Parámetros:
        node (RequestNode): Nodo de solicitud que quiere acceder a los recursos.
        """
        if not node.resources.use(self.blocked_resources):
            self.block_resources(node.resources)
            node.set_green_light()
        else:
            self.waiting_queue.append(node)

    def end_function(self, node: RequestNode):
        """
        Finaliza la ejecución de un nodo, liberando sus recursos.

        Parámetros:
        node (RequestNode): Nodo cuya solicitud ha finalizado.
        """
        self.release_resources(node.resources)

        if node in self.waiting_queue:
            self.waiting_queue.remove(node)

        for n in self.waiting_queue:
            if not n.resources.use(self.blocked_resources):
                self.block_resources(n.resources)
                n.set_green_light()

    def _start_leader_server(self):
        """Inicia el servidor del líder para manejar solicitudes entrantes."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                conn, _ = s.accept()
                json_str_data = conn.recv(1024).decode('utf-8')
                data = json.loads(json_str_data)

                threading.Thread(
                    target=self.request_leader_handler, 
                    args=(conn, data['tags'], data['files'], data['query_tags'])
                ).start()

    def request_leader_handler(self, sock: socket.socket, tags: list[str], files: list[str], query_tags: list[str]):
        """
        Maneja una solicitud de recursos de un nodo.

        Parámetros:
        sock (socket.socket): Socket de conexión del nodo.
        tags (list[str]): Lista de etiquetas solicitadas.
        files (list[str]): Lista de archivos solicitados.
        query_tags (list[str]): Etiquetas utilizadas en la consulta.
        """
        request_node = RequestNode(sock, tags, files, query_tags, self.query_tag_func, self.end_function)
        self.join(request_node)
        request_node.start()


class LeaderElection:
    """
    Implementa el algoritmo de elección de líder en la red.
    """
    def __init__(self) -> None:
        """Inicializa los valores de la elección del líder."""
        self.in_election = False
        self.work_done = True
        self.leader = None
        self.its_me = False
        self.id = str(socket.gethostbyname(socket.gethostname()))

    def leader_lost(self):
        """Notifica la pérdida del líder y reinicia el proceso de elección."""
        print("Líder perdido")
        self.leader = None

    def adopt_leader(self, leader: str):
        """
        Asigna un nuevo líder a este nodo.

        Parámetros:
        leader (str): Dirección IP del nuevo líder.
        """
        self.leader = leader
        if self.leader == self.id:
            self.its_me = True

    def loop(self):
        """Ejecuta el proceso de elección de líder en un bucle continuo."""
        time.sleep(0.5)

        threading.Thread(target=self._server).start()

        counter = 0
        while True:
            if not self.leader and not self.in_election:
                print("Iniciando elección de líder...")
                self.in_election = True
                self.work_done = False

                threading.Thread(target=self._broadcast_msg, args=(f"{ELECTION}",)).start()

            elif self.in_election and not self.work_done:
                counter += 1
                if counter == 10:
                    if not self.leader:
                        print("Soy el nuevo líder")
                        threading.Thread(target=self._broadcast_msg, args=(f"{LEADER}",)).start()

                    counter = 0

            time.sleep(0.5)

    def _broadcast_msg(self, msg: str, broadcast_ip='255.255.255.255'):
        """
        Envía un mensaje de broadcast a todos los nodos de la red.

        Parámetros:
        msg (str): Mensaje a enviar.
        broadcast_ip (str): Dirección de broadcast (por defecto '255.255.255.255').
        """
        mensaje = {"1": "ELECCIÓN", "2": "OK", "3": "LÍDER"}.get(msg, "DEFAULT")
        print(f"Enviando broadcast: {mensaje}")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg.encode('utf-8'), (broadcast_ip, PORT))
        s.close()

    def _bully(self, id1, id2):
        """
        Implementa el algoritmo de Bully para comparar identificadores de nodos.

        Parámetros:
        id1 (str): ID del primer nodo.
        id2 (str): ID del segundo nodo.

        Retorna:
        bool: True si id1 es mayor que id2, False en caso contrario.
        """
        return int(id1.split('.')[-1]) > int(id2.split('.')[-1])

    def _server(self):
        """Inicia un servidor UDP para recibir mensajes de elección de líder."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', PORT))

        while True:
            try:
                msg, sender = s.recvfrom(1024)
                if msg:
                    threading.Thread(target=self._handle_request, args=(msg, sender)).start()
            except Exception as e:
                print(f"Error en el servidor de elección: {e}")

    def _handle_request(self, msg, sender):
        """
        Maneja las solicitudes de elección de líder.

        Parámetros:
        msg (bytes): Mensaje recibido.
        sender (tuple): Dirección IP y puerto del remitente.
        """
        sender_id = sender[0]
        msg = msg.decode("utf-8")

        if msg.isdigit():
            msg = int(msg)

            if msg == ELECTION and not self.in_election:
                print(f"Mensaje de ELECCIÓN recibido de: {sender_id}")

                self.in_election = True
                self.leader = None
                
                if self._bully(sender_id, self.id):
                    self.work_done = True
                    return
                
                if self._bully(self.id, sender_id):
                    self.work_done = False

                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(f'{OK}'.encode('utf-8'), (sender_id, PORT))

                    threading.Thread(target=self._broadcast_msg, args=(f"{ELECTION}",)).start()
                        
            elif msg == OK:
                print(f"Mensaje OK recibido de: {sender_id}")

                if self._bully(sender_id, self.id):
                    self.work_done = True

            elif msg == LEADER:
                print(f"Mensaje LÍDER recibido de: {sender_id}")

                if not self.leader:
                    self.leader = sender_id
                    self.its_me = sender_id == self.id
                    self.work_done = True
                    self.in_election = False
