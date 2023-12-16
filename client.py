import socket
from Fichier import Fichier
import os

def send_end_signal(socket):
    # Envoyer une longueur de nom de fichier égale à zéro pour signaler la fin des fichiers
    socket.send(int(0).to_bytes(4, byteorder='big'))

def send_file(file_to_send, socket):
    print(f"Envoi du fichier : {file_to_send.get_path()}")
    # Créer un socket pour le client
    file_name_length = len(file_to_send.get_path())
    socket.send(file_name_length.to_bytes(4, byteorder='big'))
    # Envoyer le nom du fichier
    socket.send(file_to_send.get_path().encode())
    print(f"Nom du fichier envoyé : {file_to_send.get_path()}")
    # Lire et envoyer le contenu du fichier
    content = file_to_send.read()
    file_content_length = len(content)
    socket.send(file_content_length.to_bytes(4, byteorder='big'))
    socket.send(content)
    print(f"Le fichier {file_to_send.get_path()} a été envoyé.")

def send_folder(folder_to_send, socket):
    for root, dirs, files in os.walk(folder_to_send.get_path()):
        for file in files:
            send_file(Fichier(os.path.join(root, file)), socket)
        for dir_name in dirs:
            send_folder(Fichier(os.path.join(root, dir_name)), socket)

# Adresse IP et port du serveur
host = input("Entrez l'adresse IP du serveur : ")  # Mettez l'adresse IP du serveur ici
port = int(input("Entrez le port du serveur : "))  # Mettez le port du serveur ici

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Création d'une instance de la classe Fichier avec le chemin du fichier à envoyer
to_send = Fichier(input("entrez le path du fichier : "))  # Remplacez par le chemin de votre fichier

if os.path.isfile(to_send.get_path()):
    send_file(to_send, client)
elif os.path.isdir(to_send.get_path()):
    send_folder(to_send, client)
else:
    print("Le fichier ou dossier n'existe pas.")

send_end_signal(client)

client.close()