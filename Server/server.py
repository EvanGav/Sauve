import socket
import threading
from Fichier import Fichier

key="0qhau7ia8yi3d1tb07dq7xmrakpcaw9fefv6n3s0tmy117s4y8gk1n9cgnuqg5hbfppf6hjqnupxybpnrmneqbewijhdc8md5ihol8294f5q29kiea2uhgcpxqnylbe475876aqz8ki7ckx5x079z9s9w9ix1sqozjdivdfqe52kgdb3u7zze3ls9uwcea52bty0vgviufgtvpcxmivbk2l0bm84ujb2gmruoactm5a50znprye9to2zqcjc9ug4n044y9tyz2sj9xotjmssawn0x162ayc7w4c3xffdm13k3epv5zyok29c4pa77hcx"

def recvall(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_backup_file(file_to_send, socket):
    print(f"Envoi du fichier : {file_to_send.get_path()}")
    content = file_to_send.read()
    content = xor_encrypt_decrypt(content)
    file_to_send.set_path(file_to_send.get_path().replace("./", "./backup/"))
    file_to_send.set_path(file_to_send.get_path().replace(".\\", ".\\backup\\"))
    print(f"Nom du fichier nettoyé : {file_to_send.get_path()}")
    # Créer un socket pour le client
    file_name_length = len(file_to_send.get_path())
    socket.send(file_name_length.to_bytes(4, byteorder='big'))
    # Envoyer le nom du fichier
    socket.send(file_to_send.get_path().encode())
    print(f"Nom du fichier envoyé : {file_to_send.get_path()}")
    # Lire et envoyer le contenu du fichier
    file_content_length = len(content)
    socket.send(file_content_length.to_bytes(4, byteorder='big'))
    socket.send(content)
    print(f"Le fichier {file_to_send.get_path()} a été envoyé.")

def adjust_key_length(text_length):
    key_length = len(key)
    repetitions = text_length // key_length
    remaining = text_length % key_length
    adjusted_key = key * repetitions + key[:remaining]
    return adjusted_key

def xor_encrypt_decrypt(content):
    key_bytes = bytes(adjust_key_length(len(content)), 'utf-8')
    result_bytes = bytes([a ^ b for a, b in zip(content, key_bytes)])
    return result_bytes

# Fonction pour gérer les connexions clientes
def handle_client(client_socket):
    order = int.from_bytes(client_socket.recv(4), byteorder='big')
    if order == 1:
        while True:
            # Recevoir la longueur du nom de fichier
            file_name_length = int.from_bytes(client_socket.recv(4), byteorder='big')

            if file_name_length == 0:
                break  # Terminer la réception des fichiers

            # Recevoir le nom de fichier
            file_name = client_socket.recv(file_name_length).decode()

            print(f"Reception du fichier : {file_name}")

            # Recevoir la longueur du contenu du fichier
            file_content_length = int.from_bytes(client_socket.recv(4), byteorder='big')

            # Recevoir le contenu du fichier
            file_content = recvall(client_socket, file_content_length)

            file_content = xor_encrypt_decrypt(file_content)

            # Créer une instance de la classe Fichier
            received_file = Fichier(file_name)
            received_file.content = file_content

            # Vérifier et enregistrer le fichier sur le serveur
            received_file.save_to_path()
            print(f"Fichier {file_name} reçu et enregistré.")
 
    elif order == 2:
        while True:
            print("Envoi d'un fichier")
            file_name_length = int.from_bytes(client_socket.recv(4), byteorder='big')

            if file_name_length == 0:
                break  # Terminer la réception des fichiers
    
            # Recevoir le nom de fichier
            file_name = client_socket.recv(file_name_length).decode()

            print(f"Envoi du fichier : {file_name}")

            send_backup_file(Fichier(file_name), client_socket)

    client_socket.close()



# Adresse IP et port du serveur
host = "127.0.0.1"
port = 3333

# Créer un socket pour le serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

print(f"Serveur en attente de connexions sur le port {port}...")

while True:
    # Accepter les connexions clientes
    client_sock, addr = server.accept()
    print(f"Connexion entrante de {addr[0]}:{addr[1]}")

    # Démarrer un thread pour gérer la connexion cliente
    client_handler = threading.Thread(target=handle_client, args=(client_sock,))
    client_handler.start()
