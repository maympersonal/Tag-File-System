import socket
import threading
import time
from const import *
from utils import *
from chordnodeobject import ChordNodeObject
from leader import LeaderElection

class ChordNode:
    def __init__(self, ip: str, m: int = 160, update_replication=None):
        """
        Inicializa un nodo Chord con la dirección IP dada y un espacio de clave de m bits.
        
        Parámetros:
        ip (str): Dirección IP del nodo.
        m (int): Número de bits en el espacio de clave (por defecto 160).
        update_replication: Función para actualizar la replicación de datos.
        """
        self.ip = ip
        self.id = getShaRepr(ip)
        self.chord_port = DEFAULT_NODE_PORT
        self.ref: ChordNodeObject = ChordNodeObject(self.ip, self.chord_port)
        self.succ: ChordNodeObject = self.ref
        self.pred: ChordNodeObject = None
        self.predpred: ChordNodeObject = None
        self.m = m  # Número de bits en el espacio de claves
        self.finger = [self.ref] * self.m  # Tabla de finger
        self.next = 0  # Índice de la tabla finger para actualizar

        self.update_replication = update_replication

        self.election = LeaderElection()

        # Iniciar hilos para diversas funciones de mantenimiento
        threading.Thread(target=self.discover_nodes, daemon=True).start()
        threading.Thread(target=self.listen_for_broadcast, daemon=True).start()
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.election.loop, daemon=True).start()
        threading.Thread(target=self._leader_checker, daemon=True).start()
        threading.Thread(target=self.fix_fingers, daemon=True).start()

    def _leader_checker(self):
        """
        Comprueba periódicamente si el líder sigue activo.
        """
        while True:
            time.sleep(10)
            if self.election.leader:
                leader_node = ChordNodeObject(self.election.leader)
                if not leader_node.check_node():
                    self.election.leader_lost()

    def find_pred(self, id: int) -> 'ChordNodeObject':
        """
        Encuentra el predecesor de un ID dado.
        """
        node = self
        while not inbetween(id, node.id, node.succ.id):
            node = node.succ
        return node.ref if isinstance(node, ChordNode) else node

    def lookup(self, id: int) -> 'ChordNodeObject':
        """
        Busca el nodo responsable de un ID dado.
        """
        if self.id == id:
            return self.ref
        if inbetween(id, self.id, self.succ.id):
            return self.succ
        
        for i in range(len(self.finger) - 1, -1, -1):
            if self.finger[i] and inbetween(self.finger[i].id, self.id, id):
                if self.finger[i].check_node():
                    return self.finger[i].lookup(id)
        
        return self.succ

    def fix_fingers(self):
        """
        Actualiza periódicamente la tabla de finger.
        """
        batch_size = 10
        while True:
            for _ in range(batch_size):
                try:
                    self.next += 1
                    if self.next >= self.m:
                        self.next = 0
                    self.finger[self.next] = self.lookup((self.id + 2 ** self.next) % 2 ** self.m)
                except Exception:
                    pass
            time.sleep(5)

    def join(self, node: 'ChordNodeObject' = None):
        """
        Se une a una red Chord usando un nodo de referencia.
        """
        self.election.adopt_leader(self.ip)
        print("Uniéndose...")
        if node:
            if not node.check_node():
                raise Exception(f"No hay un nodo en la dirección {node.ip}")
            
            self.pred = None
            self.predpred = None
            self.succ = node.lookup(self.id)
            self.election.adopt_leader(node.get_leader())

            if self.succ.succ.id == self.succ.id:
                self.pred = self.succ
                self.predpred = self.ref
                self.succ.not_alone_notify(self.ref)
        else:
            self.succ = self.ref
            self.pred = None
            self.predpred = None
            self.election.adopt_leader(self.ip)

        print("Fin de la unión")

    def stabilize(self):
        """
        Verifica y actualiza periódicamente el sucesor y el predecesor.
        """
        while True:
            if self.succ.id != self.id:
                print('Estabilizando...')
                if self.succ.check_node():
                    x = self.succ.pred
                    if x.id != self.id:
                        if x and inbetween(x.id, self.id, self.succ.id):
                            if x.id != self.succ.id:
                                self.succ = x
                                self.update_replication(False, True, False, False)
                        self.succ.notify(self.ref)
                        print('Fin de la estabilización...')
                    else:
                        print("Estable")
                    if self.pred and self.pred.check_node():
                        self.predpred = self.pred.pred
                else:
                    print("Se ha perdido el sucesor, esperando verificación del predecesor...")
            time.sleep(10)

    def notify(self, node: 'ChordNodeObject'):
        """
        Informa al nodo sobre un nuevo predecesor.
        """
        print(f"El nodo {node.ip} me ha notificado, actuando...")
        if node.id == self.id:
            return
        if self.pred is None:
            self.pred = node
            self.predpred = node.pred
            self.update_replication(False, True)
        elif node.check_node():
            if inbetween(node.id, self.pred.id, self.id):
                self.predpred = self.pred
                self.pred = node
                self.update_replication(True, False)
        print("Fin de la actualización...")

    
    # Método inverso de notificación para informar al nodo sobre su nuevo sucesor
    def reverse_notify(self, node: 'ChordNodeObject'):
        print(f"Nodo {node.id} inverso me notificó, actuando...")
        self.succ = node
        print(f"Fin de la actuación...")

    # Notificación de que el nodo ya no está solo en la red
    def not_alone_notify(self, node: 'ChordNodeObject'):
        print(f"El nodo {node.ip} dice que no estoy solo ahora, actuando...")
        self.succ = node
        self.pred = node
        self.predpred = self.ref
        # Actualizar replicación con el nuevo sucesor
        self.update_replication(delegate_data=True, case_2=True)
        print(f"Fin de la actuación...")

    # Método para verificar periódicamente si el predecesor sigue activo
    def check_predecessor(self):
        while True:
            print("Verificando predecesor...")
            try:
                if self.pred and not self.pred.check_node():
                    print("El predecesor ha fallado")
                    two_in_a_row = False

                    if self.predpred.check_node():
                        self.pred = self.predpred
                        self.predpred = self.predpred.pred
                    else:
                        self.pred = self.find_pred(self.predpred.id)
                        self.predpred = self.pred.pred
                        two_in_a_row = True

                    if self.pred.id == self.id:
                        self.succ = self.ref
                        self.pred = None
                        self.predpred = None
                        if two_in_a_row:
                            self.update_replication(False, False, True, assume_predpred=self.ip)
                        else:
                            self.update_replication(False, False, True)
                        continue

                    self.pred.reverse_notify(self.ref)

                    # Asumir datos del predecesor si es necesario
                    if two_in_a_row:
                        self.update_replication(False, False, True, assume_predpred=self.pred.ip)
                    else:
                        self.update_replication(False, False, True)

            except Exception as e:
                self.pred = None
                self.succ = self.ref

            time.sleep(10)

    # Método para manejar solicitudes entrantes de otros nodos
    def request_handler(self, conn: socket, addr, data: list):
        data_resp = None
        option = int(data[0])

        if option == FIND_PREDECESSOR:
            target_id = int(data[1])
            data_resp = self.find_pred(target_id)

        elif option == LOOKUP:
            target_id = int(data[1])
            data_resp = self.lookup(target_id)

        elif option == GET_SUCCESSOR:
            data_resp = self.succ if self.succ else self.ref

        elif option == GET_PREDECESSOR:
            data_resp = self.pred if self.pred else self.ref

        elif option == NOTIFY:
            ip = data[2]
            self.notify(ChordNodeObject(ip, self.chord_port))

        elif option == REVERSE_NOTIFY:
            ip = data[2]
            self.reverse_notify(ChordNodeObject(ip, self.chord_port))

        elif option == NOT_ALONE_NOTIFY:
            ip = data[2]
            self.not_alone_notify(ChordNodeObject(ip, self.chord_port))

        elif option == CHECK_NODE:
            data_resp = self.ref

        elif option == GET_LEADER:
            leader_ip = self.election.leader
            data_resp = ChordNodeObject(leader_ip)

        # Enviar respuesta
        if data_resp:
            response = f'{data_resp.id},{data_resp.ip}'.encode('utf-8')
            conn.sendall(response)
        conn.close()

    # Método para iniciar el servidor y manejar solicitudes entrantes
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.chord_port))
            s.listen(10)

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024).decode('utf-8').split(',')

                threading.Thread(target=self.request_handler, args=(conn, addr, data)).start()

    # Método para descubrir el sucesor en la red mediante broadcasts
    def discover_Succ(self):
        """Envía broadcasts de forma continua para descubrir el sucesor en la red."""
        id_great = None
        ip_great = None
        id_small = None
        ip_small = None
        print("El auto descubrimiento ha comenzado...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(2)
            s.sendto(b"DISCOVER", ('<broadcast>', DEFAULT_BROADCAST_PORT))
            start_time = time.time()

            while time.time() - start_time < 10:
                s.sendto(b"DISCOVER", ('<broadcast>', DEFAULT_BROADCAST_PORT))
                try:
                    data, addr = s.recvfrom(1024)
                    if addr[0] == self.ip:
                        continue  # Ignorar respuestas propias

                    parts = data.decode().split()

                    if len(parts) == 2 and parts[0] == "NODE":
                        if not id_great:
                            if int(parts[1]) < self.id:
                                if (not id_small) or (int(parts[1]) < id_small):  
                                    id_small = int(parts[1])
                                    ip_small = addr[0]
                                    start_time = time.time()
                            else:
                                id_great = int(parts[1])
                                ip_great = addr[0]
                                start_time = time.time()
                        elif (int(parts[1]) < self.id) and (int(parts[1]) < id_great):
                            id_great = int(parts[1])
                            ip_great = addr[0]
                            start_time = time.time()
                except socket.timeout:
                    pass  # No hay respuestas, continuar

        if not id_great:
            self.join(ChordNodeObject(ip_small) if ip_small else None)
        else:
            self.join(ChordNodeObject(ip_great))

        print(f'El nodo logró unirse a la red, su sucesor es {self.succ}')

    # Método para descubrir otros nodos en la red enviando broadcasts
    def discover_nodes(self):
        """Envía broadcasts de forma continua para descubrir otros nodos en la red."""
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.settimeout(2)
                s.sendto(b"DISCOVER", ('<broadcast>', DEFAULT_BROADCAST_PORT))
                try:
                    data, addr = s.recvfrom(1024)
                    if addr[0] == self.ip:
                        continue  # Ignorar respuestas de sí mismo
                    parts = data.decode().split()
                    if len(parts) == 3 and parts[0] == "NODE":
                        print(f"Nodo {self.id} encontró sucesor automáticamente: {self.succ}")
                except socket.timeout:
                    print(f"Nodo {self.id} no encontró otros nodos activos. Reintentando...")
            time.sleep(10)  # Reintenta cada 10 segundos

    # Método para escuchar mensajes de broadcast de nuevos nodos buscando unirse
    def listen_for_broadcast(self):
        """Escucha mensajes de broadcast de nuevos nodos buscando unirse."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", DEFAULT_BROADCAST_PORT))
            print(f"Nodo {self.id} escuchando broadcasts en el puerto {DEFAULT_BROADCAST_PORT}")
            while True:
                data, addr = s.recvfrom(1024)
                if addr[0] == self.ip:
                    continue  # Ignorar mensajes propios
                elif data.decode().split()[0] == "DISCOVER":
                    s.sendto(f"NODE {self.id} ".encode(), addr)
