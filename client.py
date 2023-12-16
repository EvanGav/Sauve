import socket
from Fichier import Fichier

# Adresse IP et port du serveur
host = input("Entrez l'adresse IP du serveur : ")  # Mettez l'adresse IP du serveur ici
port = int(input("Entrez le port du serveur : "))  # Mettez le port du serveur ici

# Création d'une instance de la classe Fichier avec le chemin du fichier à envoyer
file_to_send = Fichier(input("entrez le path du fichier : "))  # Remplacez par le chemin de votre fichier

# Créer un socket pour le client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Envoyer le nom du fichier
client.send(file_to_send.get_path().encode())

# Lire et envoyer le contenu du fichier
content = file_to_send.read()
client.send(content)

print(f"Le fichier {file_to_send.get_path()} a été envoyé.")
client.close()