import socket
import threading
from Fichier import Fichier
import os

def recvall(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


# Fonction pour gérer les connexions clientes
def handle_client(client_socket):
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

        # Créer une instance de la classe Fichier
        received_file = Fichier(file_name)
        received_file.content = file_content

        received_last_modified = int.from_bytes(client_socket.recv(8), byteorder='big')

        if os.path.exists(file_name):
            # Vérifier si le fichier existe déjà
            if received_last_modified > os.path.getmtime(file_name):
                # Le fichier reçu est plus récent que le fichier existant
                print(f"Fichier reçu plus récent.")
                print(f"Ecrasement du fichier {file_name}...")
                received_file.save_to_path()
                print(f"Fichier {file_name} enregistré.")
            else:
                print(f"Fichier déjà existant.")
        else:
            # Vérifier et enregistrer le fichier sur le serveur
            received_file.save_to_path()
            print(f"Fichier {file_name} reçu et enregistré.")

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
