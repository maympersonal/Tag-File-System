
# Puertos predeterminados para los diferentes servicios del sistema
DEFAULT_NODE_PORT = 8001        # Puerto para la comunicación entre nodos en la red Chord
DEFAULT_DATA_PORT = 8002        # Puerto para la transferencia de datos entre nodos
DEFAULT_QUERY_PORT = 8003       # Puerto para la gestión de consultas en el sistema de archivos
DEFAULT_BROADCAST_PORT = 8255   # Puerto utilizado para mensajes de difusión en la red
DEFAULT_DB_PORT = 8888          # Puerto para la base de datos distribuida
DEFAULT_LEADER_PORT = 8999      # Puerto de comunicación con el nodo líder

# Operaciones en la red Chord
FIND_SUCCESSOR = 1              # Buscar el sucesor de un nodo en la red
FIND_PREDECESSOR = 2            # Buscar el predecesor de un nodo en la red
GET_SUCCESSOR = 3               # Obtener el nodo sucesor
GET_PREDECESSOR = 4             # Obtener el nodo predecesor
NOTIFY = 5                      # Notificar cambios en la red
CHECK_NODE = 6                  # Verificar si un nodo está activo
CLOSEST_PRECEDING_FINGER = 7     # Obtener el nodo más cercano al destino en la tabla de finger
LOOKUP = 15                     # Buscar un nodo en la red
STORE_KEY = 8                   # Almacenar una clave en la red
RETRIEVE_KEY = 9                # Recuperar una clave almacenada
NOT_ALONE_NOTIFY = 10           # Notificar a un nodo que ya no está solo en la red
REVERSE_NOTIFY = 11             # Notificar cambios en el nodo sucesor
GET_LEADER = 12                 # Obtener la dirección del nodo líder
DISCOVER = 13                   # Descubrir otros nodos en la red
ENTRY_POINT = 14                # Definir un punto de entrada a la red

# Códigos de confirmación y operaciones en la gestión de archivos y etiquetas
OK = 0                          # Respuesta de éxito en una operación
INSERT_TAG = 1                  # Insertar una etiqueta en el sistema
DELETE_TAG = 2                  # Eliminar una etiqueta del sistema
APPEND_FILE = 3                 # Asociar un archivo a una etiqueta
REMOVE_FILE = 4                 # Desasociar un archivo de una etiqueta
RETRIEVE_TAG = 5                # Recuperar archivos asociados a una etiqueta

INSERT_FILE = 7                 # Insertar un archivo en el sistema
DELETE_FILE = 8                 # Eliminar un archivo del sistema
APPEND_TAG = 9                  # Agregar una etiqueta a un archivo
REMOVE_TAG = 10                 # Eliminar una etiqueta de un archivo
RETRIEVE_FILE = 11              # Recuperar etiquetas asociadas a un archivo
OWNS_FILE = 12                  # Verificar si un nodo es dueño de un archivo

INSERT_BIN = 13                 # Insertar un archivo binario en el sistema
DELETE_BIN = 14                 # Eliminar un archivo binario del sistema
RETRIEVE_BIN = 15               # Recuperar el contenido binario de un archivo
END = 100                       # Código de finalización de una operación
END_FILE = 200                  # Código de finalización de transferencia de un archivo binario

FALSE = 0                       # Representación de falso en el sistema
TRUE = 1                        # Representación de verdadero en el sistema

# Operaciones de replicación y sincronización de datos entre nodos
PULL_REPLICATION = 2            # Solicitar los datos replicados de un nodo predecesor
PULL_SUCC_REPLICA = 3           # Solicitar los datos replicados de un nodo sucesor
PUSH_DATA = 4                   # Enviar datos a un nuevo nodo propietario
FETCH_REPLICA = 8               # Solicitar la replicación de datos de otro nodo

# Replicación de datos desde el predecesor
REPLICATE_PRED_STORE_TAG = 11   # Replicar el almacenamiento de una etiqueta
REPLICATE_PRED_APPEND_FILE = 12 # Replicar la asociación de un archivo con una etiqueta
REPLICATE_PRED_DELETE_TAG = 13  # Replicar la eliminación de una etiqueta
REPLICATE_PRED_REMOVE_FILE = 14 # Replicar la desasociación de un archivo de una etiqueta

REPLICATE_PRED_STORE_FILE = 21  # Replicar el almacenamiento de un archivo
REPLICATE_PRED_APPEND_TAG = 22  # Replicar la asociación de una etiqueta a un archivo
REPLICATE_PRED_DELETE_FILE = 23 # Replicar la eliminación de un archivo
REPLICATE_PRED_REMOVE_TAG = 24  # Replicar la eliminación de una etiqueta de un archivo

REPLICATE_PRED_STORE_BIN = 30   # Replicar el almacenamiento de un archivo binario
REPLICATE_PRED_DELETE_BIN = 31  # Replicar la eliminación de un archivo binario

# Replicación de datos desde el sucesor
REPLICATE_SUCC_STORE_TAG = 111  # Replicar el almacenamiento de una etiqueta
REPLICATE_SUCC_APPEND_FILE = 121 # Replicar la asociación de un archivo con una etiqueta
REPLICATE_SUCC_DELETE_TAG = 131 # Replicar la eliminación de una etiqueta
REPLICATE_SUCC_REMOVE_FILE = 141 # Replicar la desasociación de un archivo de una etiqueta

REPLICATE_SUCC_STORE_FILE = 211 # Replicar el almacenamiento de un archivo
REPLICATE_SUCC_APPEND_TAG = 221 # Replicar la asociación de una etiqueta a un archivo
REPLICATE_SUCC_DELETE_FILE = 231 # Replicar la eliminación de un archivo
REPLICATE_SUCC_REMOVE_TAG = 241 # Replicar la eliminación de una etiqueta de un archivo

REPLICATE_SUCC_STORE_BIN = 301  # Replicar el almacenamiento de un archivo binario
REPLICATE_SUCC_DELETE_BIN = 311 # Replicar la eliminación de un archivo binario
