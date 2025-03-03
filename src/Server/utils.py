import hashlib
import socket
import os
from const import OK, END, END_FILE, SECRET_KEY
from typing import Dict, List
import time
import random
import base64
import random
import string

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
            first_msg = encrypt_message(first_msg, SECRET_KEY)
            s.sendall(first_msg.encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != f"{OK}":
                raise Exception("ACK negativo")
            second_msg = encrypt_message(second_msg, SECRET_KEY)
            s.sendall(second_msg.encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != f"{OK}":
                raise Exception("ACK negativo")
    except:
        print(f"{target_ip} no está disponible")


# Función para abrir un socket y enviar un archivo binario
def send_bin(op: str, file_name: str, bin_data: bytes, target_ip: str, target_port: int, end_msg: bool = False):
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

    try:
        print(f"******* CONECTAR A {target_ip}:{target_port} *********")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))

            # Enviar código de operación
            print("Enviando código de operación...")
            s.sendall(op.encode('utf-8'))
            ack = s.recv(1024).decode('utf-8')
            if ack != OK:
                return f"ACK negativo para op: {ack}"

            # Enviar nombre del archivo
            print("Enviando nombre del archivo...")
            s.sendall(file_name.encode('utf-8'))
            ack = s.recv(1024).decode('utf-8')
            if ack != OK:
                return f"ACK negativo para file_name: {ack}"

            # Enviar contenido binario en fragmentos
            fragment_size = 1024
            print("Enviando contenido binario...")
            for i in range(0, len(bin_data), fragment_size):
                fragment = bin_data[i:i + fragment_size]
                s.sendall(fragment)

            if end_msg:
                s.sendall(END_FILE.encode('utf-8'))

            result = s.recv(1024)
            return result.decode('utf-8')
    except Exception as e:
        print(f"Error en send_bin: {e}")

# Función ajustada para recibir un archivo binario y guardarlo en un directorio especificado
def recv_bin(conn: socket.socket):
    """
    Recibe un archivo binario y lo guarda en el directorio especificado.

    Parámetros:
    s (socket): Socket utilizado para la recepción.
    dest_dir (str): Directorio donde se almacenará el archivo recibido.
    """
    try:
        conn.sendall(f"{OK}".encode('utf-8'))
        file_name = conn.recv(1024).decode('utf-8')
        conn.sendall(f"{OK}".encode('utf-8'))

        bin_data = b''
        end_file = f"{END_FILE}".encode('utf-8')
        while True:
            fragment = conn.recv(1024)
            if end_file in fragment:
                bin_data += fragment.split(end_file)[0]
                break
            bin_data += fragment
        return file_name, bin_data

    except Exception as e:
        print(f"Error en recv_bin: {e}")
        return "", b''
    
# Función mejorada para enviar múltiples archivos binarios
def send_bins(s: socket.socket, files_to_send: dict, path: str):
    """
    Envía múltiples archivos binarios a través de un socket.

    Parámetros:
    s (socket): Socket utilizado para la transmisión.
    files_to_send (dict): Diccionario con los nombres de archivo y sus datos.
    path (str): Ruta del directorio donde están los archivos.
    """
    try:
        if len(files_to_send) > 0:
            for file_name, _ in files_to_send.items():
                file_path = f"{path}/{file_name}"

                # Verificar si el archivo existe antes de enviar
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

                s.sendall(file_name.encode('utf-8'))

                ack = s.recv(1024).decode('utf-8')
                if ack != OK:
                    return f"ACK negativo para {file_name}"

                # Enviar contenido binario en fragmentos
                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(1024)

                        if not data:
                            break
                        s.sendall(data)

                        ack = s.recv(1024).decode('utf-8')
                        if ack != OK:
                            return f"ACK negativo durante envío de datos para {file_name}"

                s.sendall(END_FILE.encode('utf-8'))

                ack = s.recv(1024).decode('utf-8')
                if ack != OK:
                    return f"ACK negativo al finalizar {file_name}"

            s.sendall(END.encode('utf-8'))

            ack = s.recv(1024).decode('utf-8')
            if ack != OK:
                return "ACK negativo al finalizar transmisión"

    except Exception as e:
        print(f"Error en send_bins: {e}")

# Función mejorada para recibir múltiples archivos binarios
def recv_write_bins(s: socket.socket, dest_dir: str):
    """
    Recibe múltiples archivos binarios y los guarda en un directorio.

    Parámetros:
    s (socket): Socket utilizado para la recepción.
    dest_dir (str): Directorio donde se almacenarán los archivos recibidos.
    """
    try:
        while True:
            data = s.recv(1024)
            if data.decode('utf-8') == END:
                break

            file_name = data.decode('utf-8')
            s.sendall(OK.encode('utf-8'))

            file_content = []
            while True:
                data = s.recv(1024)
                # Verificar si el fragmento es END_FILE (manejo robusto de binarios)
                if data.decode('utf-8', errors='ignore').strip() == END_FILE:
                    file_bin = b''.join(file_content)

                    # Guardar el archivo binario en el directorio de destino
                    os.makedirs(dest_dir, exist_ok=True)
                    with open(f"{dest_dir}/{file_name}", 'wb') as file:
                        file.write(file_bin)

                    file_content = []
                    break
                file_content.append(data)
                s.sendall(OK.encode('utf-8'))

            s.sendall(OK.encode('utf-8'))

    except Exception as e:
        print(f"Error en recv_write_bins: {e}")



def generate_rsa_keys(bits=2048):
    """Genera un par de claves RSA (pública y privada)."""
    # Paso 1: Generar dos primos grandes
    def is_prime(n, k=5):  # Test de primalidad de Miller-Rabin
        if n < 2: return False
        for _ in range(k):
            a = random.randint(2, n - 1)
            if pow(a, n - 1, n) != 1:
                return False
        return True

    def generate_large_prime(bits):
        while True:
            num = random.getrandbits(bits)
            if is_prime(num):
                return num

    p = generate_large_prime(bits // 2)
    q = generate_large_prime(bits // 2)
    n = p * q  # Módulo RSA
    phi = (p - 1) * (q - 1)

    # Paso 2: Elegir e (comúnmente 65537)
    e = 65537
    while phi % e == 0:
        e = random.randrange(2, phi)

    # Paso 3: Calcular d (inverso modular de e mod phi)
    def mod_inverse(e, phi):
        """Calcula el inverso modular de e mod phi usando el algoritmo de Euclides extendido."""
        a, b, x0, x1 = phi, e, 0, 1
        while b:
            q = a // b
            a, b = b, a % b
            x0, x1 = x1, x0 - q * x1
        return x0 % phi

    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key



def encrypt_message(message: str, public_key):
    """
    Cifra un mensaje usando una combinación de RSA y AES.

    - Cifra la clave AES con la clave pública RSA.
    - Usa la clave AES para cifrar el mensaje con XOR simple.

    Parámetros:
        message (str): El mensaje a cifrar.
        public_key (tuple): Clave pública RSA del receptor (e, n).

    Retorna:
        str: Mensaje cifrado en hexadecimal + clave AES cifrada con RSA.
    """
    e, n = public_key

    # 🔐 Generar clave AES aleatoria (16 caracteres)
    aes_key = hashlib.sha256(str(n).encode()).hexdigest()[:16]

    # 🔑 Cifrar la clave AES con la clave pública RSA
    key_int = int.from_bytes(aes_key.encode(), "big")
    encrypted_aes_key = pow(key_int, e, n)

    # 🔒 Cifrar el mensaje con AES usando XOR (simplificado)
    key_hash = hashlib.sha256(aes_key.encode()).digest()[:16]
    encrypted_bytes = bytes(ord(c) ^ key_hash[i % len(key_hash)] for i, c in enumerate(message))
    encrypted_message = encrypted_bytes.hex()

    # 🔄 Retornar la clave AES cifrada + mensaje cifrado
    return f"{encrypted_aes_key}:{encrypted_message}"

def decrypt_message(encrypted_data: str, private_key):
    """
    Descifra un mensaje cifrado con RSA y AES.

    - Descifra la clave AES con la clave privada RSA.
    - Usa la clave AES para descifrar el mensaje con XOR simple.

    Parámetros:
        encrypted_data (str): Mensaje cifrado recibido (clave AES cifrada + mensaje cifrado en hexadecimal).
        private_key (tuple): Clave privada RSA del receptor (d, n).

    Retorna:
        str: Mensaje original descifrado.
    """
    d, n = private_key

    # 🔓 Separar la clave AES cifrada y el mensaje cifrado
    encrypted_aes_key_str, encrypted_message = encrypted_data.split(":")

    # 🗝 Descifrar la clave AES con RSA
    encrypted_aes_key = int(encrypted_aes_key_str)
    key_int = pow(encrypted_aes_key, d, n)
    aes_key = key_int.to_bytes((key_int.bit_length() + 7) // 8, "big").decode()

    # 🔓 Descifrar el mensaje con AES usando XOR (simplificado)
    key_hash = hashlib.sha256(aes_key.encode()).digest()[:16]
    encrypted_bytes = bytes.fromhex(encrypted_message)
    decrypted_message = ''.join(chr(b ^ key_hash[i % len(key_hash)]) for i, b in enumerate(encrypted_bytes))

    return decrypted_message

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



def generate_password(length=12):
    """Genera una clave secreta que parece una contraseña."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Generar una clave secreta
secret_key = generate_password(12)
print(secret_key)

