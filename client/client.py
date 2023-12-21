import socket
from Fichier import Fichier
import os
from file_sender import *
from file_retriever import *


# Adresse IP et port du serveur
host = input("Entrez l'adresse IP du serveur : ")  
port = int(input("Entrez le port du serveur : "))  
#On initialise la socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

#On demande à l'utilisateur l'action qu'il veut réaliser
action=int(input("Entrez 1 pour envoyer un fichier, 2 pour récupérer un fichier : "))

if action == 1:
    #On envoie un signal indiquant que l'on veut sauvegarder un ou plusieurs fichiers
    client.send(int(1).to_bytes(4, byteorder='big'))
    #On demande le path
    to_send = Fichier(input("entrez le path du fichier : "))  
    #On lance la fonction selon si on tombe sur un dossier ou un fichier
    if os.path.isfile(to_send.get_path()):
        send_file(to_send, client)
    elif os.path.isdir(to_send.get_path()):
        send_folder(to_send, client)
    else:
        print("Le fichier ou dossier n'existe pas.")
    #On indique au serveur qu'on à fini
    client.send(int(0).to_bytes(4, byteorder='big'))

elif action == 2:
    #On envoie un signal indiquant que l'on veut récupérer un ou plusieurs fichiers
    client.send(int(2).to_bytes(4, byteorder='big'))
    #On demande le path
    to_retrieve = Fichier(input("entrez le path du fichier : "))
    if os.name == 'nt':  # Si c'est Windows
        to_retrieve.set_path(to_retrieve.get_path().replace("/", "\\"))
    #On lance la fonction selon si on tombe sur un dossier ou un fichier
    if os.path.isfile(to_retrieve.get_path()):
        ask_retrieve_file(to_retrieve, client)
    elif os.path.isdir(to_retrieve.get_path()):
        ask_retrieve_folder(to_retrieve, client)
    else:
        print("Le fichier ou dossier n'existe pas.")
    #On indique au serveur qu'on à fini
    client.send(int(0).to_bytes(4, byteorder='big'))

client.close()