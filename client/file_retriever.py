import os
from Fichier import Fichier
from json_handler import *
from base_position import BASE_FOLDER


def clean_file_path_for_retrieval(file_path,d):
    """
    Modifie le chemin du fichier pour la récupération en ajoutant une date et un path spécifique.

    Args:
    - file_path (str): Le chemin du fichier à modifier.
    - d (str): La date.

    Returns:
    - str: Le chemin modifié du fichier pour la récupération.
    """
    # On supprime ../
    file_path = os.path.abspath(os.path.expanduser(file_path))

    # On supprime les chemins absolus (C:, D:, etc.)
    if ':' in file_path:
        drive, path = os.path.splitdrive(file_path)
        if drive:
            file_path = path
    #On remplace le path par un nouveau
    file_path = file_path.replace("/Users/"+os.getlogin()+"/","")
    file_path = file_path.replace("\\Users\\"+os.getlogin()+"\\","")
    file_path = file_path.replace("/home/"+os.getlogin()+"/","")
    file_path = os.path.join(".", BASE_FOLDER, d, file_path)
    return file_path

def recvall(sock, length):
    """
    Cette fonction permet de recevoir des données d'une socket jusqu'à une certaine longueur.

    Args:
    - sock (socket): La socket à partir de laquelle recevoir les données.
    - length (int): La longueur totale des données à recevoir.

    Returns:
    - data (bytes): Les données reçues depuis la socket.
    """
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def retrieve_data(socket):
    """
    Récupère et enregistre les données du fichier à partir d'une socket.

    Args:
    - socket (socket.socket): Le socket pour la communication.
    """
    # On reçoit la longueur du nom de fichier
    file_name_length = int.from_bytes(socket.recv(4), byteorder='big')
    # On reçoit le nom de fichier
    file_name = socket.recv(file_name_length).decode()
    print(f"Reception du fichier : {file_name}")
    # On reçoit la longueur du contenu du fichier
    file_content_length = int.from_bytes(socket.recv(4), byteorder='big')
    # On reçoit le contenu du fichier
    file_content = recvall(socket, file_content_length)
    # On crée un Fichier
    received_file = Fichier(file_name)
    received_file.content = file_content
    # On enregistre le fichier sur le serveur
    received_file.save_to_path()
    print(f"Fichier {file_name} reçu et enregistré.")    




def ask_retrieve_file(file_to_retrieve, socket):
    """
    Gère la demande de récupération d'un fichier spécifique à partir d'une socket.

    Args:
    - file_to_retrieve (Fichier): Le fichier à récupérer.
    - socket (socket.socket): Le socket pour la communication.
    """
    # On charge les logs (JSON) existants pour la recherche du fichier
    logs = load_logs()
    print(f"Recherche du fichier {file_to_retrieve.get_path()} dans les logs...")
    #On vérifie si le path du fichier existe dans le fichier logs
    if file_to_retrieve.get_path() in logs.keys():
        # Le fichier existe dans les logs
        print(f"Le fichier {file_to_retrieve.get_path()} existe.")
        # On regarde les dates disponibles pour ce fichier
        file_dates = [info["backup_date"] for path, info in logs.items() if path == file_to_retrieve.get_path()]
        #S'il en a plus d'une, on demande à l'utilisateur de choisir
        if len(set(file_dates)) > 1:
            print("Ce fichier existe pour plusieurs dates. Voici les dates disponibles :")
            for date in set(file_dates):
                print(date)
            chosen_date = input("Entrez la date pour laquelle récupérer le fichier : ")
            #On envoie la demande de fichier à la date choisie
            if chosen_date in file_dates:
                # Envoi au serveur du path du fichier à récupérer pour la date choisie
                file_to_retrieve.set_path(clean_file_path_for_retrieval(file_to_retrieve.get_path(),chosen_date))
                file_name_length = len(file_to_retrieve.get_path())
                #On envoie la longueur du nom du fichier
                socket.send(file_name_length.to_bytes(4, byteorder='big'))
                #On envoie le nom du fichier
                socket.send(file_to_retrieve.get_path().encode())
            else:
                print("Date invalide.")
        else:
            # Il n'existe qu'une seule date pour ce fichier, donc on envoie directement au serveur
            chosen_date = file_dates[0]
            file_to_retrieve.set_path(clean_file_path_for_retrieval(file_to_retrieve.get_path(),chosen_date))
            print(f"Nom du fichier nettoyé : {file_to_retrieve.get_path()}")
            file_name_length = len(file_to_retrieve.get_path())
            socket.send(file_name_length.to_bytes(4, byteorder='big'))
            socket.send(file_to_retrieve.get_path().encode())
        #On récupère le fichier
        retrieve_data(socket)
    else:
        print(f"Le fichier {file_to_retrieve.get_path()} n'existe pas dans les logs.")

def ask_retrieve_folder(folder_to_retrieve, socket):
    """
    Gère la demande de récupération d'un dossier.

    Args:
    - folder_to_retrieve (Fichier): Le dossier à récupérer.
    - socket (socket.socket): Le socket pour la communication.
    """
    for root, dirs, files in os.walk(folder_to_retrieve.get_path()):
        for file in files:
            #Si on tombe sur un fichier, on demande à le récuperer
            file_path = os.path.join(root, file)
            ask_retrieve_file(Fichier(file_path), socket)
    for dir_name in dirs:
        #Si c'est un dossier on appelle récursivement la fonction
        ask_retrieve_folder(Fichier(os.path.join(root, dir_name)), socket)