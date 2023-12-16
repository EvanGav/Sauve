import socket
import threading
import os
from Fichier import Fichier

# Fonction pour gérer les connexions clientes
def handle_client(client_socket):
    # Recevoir le nom du fichier
    file_name = client_socket.recv(1024).decode()
    print(f"Reception du fichier : {file_name}")

    # Créer une instance de la classe Fichier
    received_file = Fichier(file_name)
    received_file.content = client_socket.recv(1024)

    # Enregistrer le fichier dans les dossiers du chemin
    received_file.save_to_path()
    print(f"Fichier {file_name} reçu et enregistré.")
    client_socket.close()

# Adresse IP et port du serveur
host = input("Entrez l'adresse IP du serveur : ")
port = int(input("Entrez le port du serveur : "))

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
