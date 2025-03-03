import socket
import threading
import time
import struct  # 💡 Import necesario para manejo de datos binarios

from const import *
from utils import *
from chordnodeobject import ChordNodeObject
#from leader import LeaderElection

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

        self.lock = threading.Lock()
        self.green_ligth = False
        

        # Iniciar hilos para diversas funciones de mantenimiento
        threading.Thread(target=self.discover_nodes, daemon=True).start()
        threading.Thread(target=self.listen_nodes, daemon=True).start()
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.fix_fingers, daemon=True).start()




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
        #with self.lock:  # 🔒 Proteger acceso
        if self.id == id:
            return self.ref
        if inbetween(id, self.id, self.succ.id):
            return self.succ

        for i in range(len(self.finger) - 1, -1, -1):
            if self.finger[i] and inbetween(self.finger[i].id, self.id, id):
                if self.finger[i] and self.finger[i].check_node():
                    if self.finger[i].id == self.id:  # Evitar bucles infinitos
                        break
                    return self.finger[i].lookup(id)

        return self.succ

    def fix_fingers(self):
        """
        Actualiza periódicamente la tabla de finger.
        """
        #with self.lock:
        batch_size = 10
        while True:
            #with self.lock:  # 🔒 Proteger acceso
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
        #with self.lock:
        print("Uniéndose...")
        if node:
            if not node.check_node():
                raise Exception(f"No hay un nodo en la dirección {node.ip}")

            self.pred = None
            self.predpred = None
            self.succ = node.lookup(self.id)



            if self.succ.succ.id == self.succ.id:
                self.pred = self.succ
                self.predpred = self.ref
                self.succ.not_alone_notify(self.ref)
        else:
            self.succ = self.ref
            self.pred = None
            self.predpred = None


        print("Fin de la unión")

    def stabilize(self):
        """
        Verifica y actualiza periódicamente el sucesor y el predecesor.
        """
        #with self.lock:
        while True:
            #with self.lock:  # 🔒 Proteger acceso
            if self.succ.id != self.id:
                print('Estabilizando...')
                if self.succ.check_node():
                    x = self.succ.pred
                    if x.id != self.id:
                        if x and inbetween(x.id, self.id, self.succ.id):
                            if x.id != self.succ.id:
                                self.succ = x
                                if self.update_replication:
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
            if self.update_replication:
                self.update_replication(False, True)
        elif node.check_node():
            if inbetween(node.id, self.pred.id, self.id):
                self.predpred = self.pred
                self.pred = node
                if self.update_replication:
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
        if self.update_replication:
            self.update_replication(delegate_data=True, case_2=True)
        print(f"Fin de la actuación...")

    # Método para verificar periódicamente si el predecesor sigue activo
    def check_predecessor(self):
        #with self.lock:
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
                            if self.update_replication:
                                self.update_replication(False, False, True, assume_predpred=self.ip)
                        else:
                            if self.update_replication:                
                                self.update_replication(False, False, True)
                        continue

                    self.pred.reverse_notify(self.ref)

                    # Asumir datos del predecesor si es necesario
                    if two_in_a_row:
                        if self.update_replication:
                            self.update_replication(False, False, True, assume_predpred=self.pred.ip)
                    else:
                        if self.update_replication:
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



        # Enviar respuesta
        if data_resp:
            response = f'{data_resp.id},{data_resp.ip}'.encode('utf-8')
            conn.sendall(response)
        conn.close()

    # Método para iniciar el servidor y manejar solicitudes entrantes
    def start_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.ip, self.chord_port))
                s.listen(10)
                print(f"Nodo {self.id} escuchando en el puerto {self.chord_port}")
                while True:
                    conn, addr = s.accept()
                    print(f"Conexión entrante desde {addr}")
                    data = conn.recv(1024).decode('utf-8').split(',')
                    print(f"Solicitud recibida: {data}")
                    threading.Thread(target=self.request_handler, args=(conn, addr, data)).start()
        except OSError as e:
            print(f"Error al iniciar el servidor en {self.ip}:{self.chord_port} - {e}")

    

    
    def discover_nodes(self):
        """Envía mensajes multicast para descubrir otros nodos en la red e integrarse en el anillo Chord."""
        
        while not self.green_ligth:
            pass

        multicast_group = (MULTICAST_GROUP, DEFAULT_BROADCAST_PORT)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            s.settimeout(2)

            while True:
                try:
                    # 🔄 Enviar mensaje DISCOVER al grupo de multicast
                    print(f"🌐 Nodo {self.id} enviando mensaje DISCOVER en {MULTICAST_GROUP}")
                    s.sendto(b"DISCOVER", multicast_group)

                    # 🔄 Esperar respuesta de otros nodos en el grupo multicast
                    while True:
                        data, addr = s.recvfrom(1024)
                        print(f"📩 Recibido mensaje de {addr}: {data}")

                        if addr[0] == self.ip:
                            continue  # Ignorar respuestas de sí mismo

                        parts = data.decode().split()
                        if len(parts) >= 2 and parts[0] == "NODE":
                            new_node_ip = addr[0]
                            new_node_id = int(parts[1])
                            encrypted_id = parts[2]
                            decrypted_id = decrypt_message(encrypted_id, SECRET_KEY)
                            
                            if not parts[1] == decrypted_id :
                                print(f"❌ Nodo {new_node_id} {decrypted_id} {parts[1]} rechazado...")
                                continue
                            else:
                                print(f"✅ Nodo {new_node_id} aceptado...")
                            
                            response = f"IDENTIFY {self.id}".encode()
                            s.sendto(response, addr)

                            print(f"✅ Nodo {self.id} encontró nodo: {new_node_id} en {new_node_ip}")

                            # 🔍 Evaluar si el nuevo nodo debe ser el sucesor o predecesor
                            new_node = ChordNodeObject(new_node_ip, self.chord_port)

                            # 🔗 Evaluar si el nuevo nodo debe ser el sucesor
                            if inbetween(new_node_id, self.id, self.succ.id):
                                print(f"🔄 Actualizando sucesor de {self.id} a {new_node_id}")
                                old_succ = self.succ
                                self.succ = new_node
                                # Notificar al nuevo sucesor
                                self.succ.notify(self.ref)
                                # Decir al antiguo sucesor que su nuevo predecesor es el nodo descubierto
                                old_succ.reverse_notify(new_node)
                                # 🔄 Forzar estabilización para sincronizar datos
                                self.stabilize()
                            # 🔗 Evaluar si el nuevo nodo debe ser el predecesor
                            elif not self.pred or inbetween(new_node_id, self.pred.id, self.id):
                                print(f"🔄 Actualizando predecesor de {self.id} a {new_node_id}")
                                old_pred = self.pred
                                self.pred = new_node
                                self.predpred = old_pred if old_pred else self.ref

                                # Notificar al nuevo predecesor
                                self.pred.reverse_notify(self.ref)

                                # Si hay un predecesor anterior, decirle que su sucesor ha cambiado
                                if old_pred:
                                    old_pred.notify(new_node)
                                # 🔄 Forzar estabilización para sincronizar datos
                                self.stabilize()
                            # Si el nodo está solo, se establece como su propio predecesor y sucesor
                            elif self.succ.id == self.id and self.pred is None:
                                print("🟢 Nodo solitario encontró otro nodo, actualizando...")

                                # Guarda el estado actual de succ y pred
                                old_succ = self.succ
                                old_pred = self.pred

                                # 🔄 Actualiza las referencias
                                self.succ = new_node
                                self.pred = new_node
                                self.predpred = self.ref

                                # 🔄 Notificar cambios con métodos existentes
                                # Usar reverse_notify para informar al nuevo sucesor
                                self.succ.reverse_notify(self.ref)

                                # Usar notify para informar al nuevo predecesor
                                self.pred.notify(self.ref)

                                # Si había un sucesor o predecesor anterior, notificar el cambio
                                if old_succ and old_succ.id != self.succ.id:
                                    old_succ.reverse_notify(self.succ)
                                if old_pred and old_pred.id != self.pred.id:
                                    old_pred.notify(self.pred)

                                # 🔄 Forzar estabilización para propagar cambios y sincronizar datos
                                self.stabilize()

                except socket.timeout:
                    print(f"⏳ Nodo {self.id} no encontró otros nodos. Reintentando...")

                time.sleep(10)  # Reintentar cada 10 segundos

    def listen_nodes(self):
        """Escucha mensajes de multicast de nuevos nodos buscando unirse al anillo Chord."""
        while not self.green_ligth:
                pass
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', DEFAULT_BROADCAST_PORT))  # Escuchar en todas las interfaces

            # 🔄 Unirse al grupo multicast
            group = socket.inet_aton(MULTICAST_GROUP)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            print(f"📡 Nodo {self.id} suscrito a multicast en {MULTICAST_GROUP}:{DEFAULT_BROADCAST_PORT}")

            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    print(f"📨 Mensaje recibido de {addr}: {data}")

                    if addr[0] == self.ip:
                        continue  # Ignorar mensajes propios
                    
                    message = data.decode().strip()
                    if message == "DISCOVER":
                        encrypted_id = encrypt_message(str(self.id), SECRET_KEY)
                        response = f"NODE {self.id} {encrypted_id}".encode()
                        print(response)
                        s.sendto(response, addr)  # Responder con el ID del nodo
                        print(f"📤 Enviando respuesta a {addr[0]}: {response.decode()}")
                        data, addr = s.recvfrom(1024)
                        print(f"📩 Recibido mensaje de {addr}: {data}")
                        parts = data.decode().split()
                        if len(parts) >= 4 and parts[0] == "IDENTIFY":
                            new_node_id = int(parts[1])
                            print(f"📩 Nodo identificado {addr}: {new_node_id}")    

                except Exception as e:
                    print(f"⚠️ Error en listen_for_multicast: {e}")


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip)

    counter = 0
    while True:
        if counter % 100000000 == 0:
            print(f"Predecesor: {str(node.pred).split(',')[0] if node.pred != None else None}, Nodo: {node.id}, Sucesor: {str(node.succ).split(',')[0] if node.succ != None else None}")
        counter += 1