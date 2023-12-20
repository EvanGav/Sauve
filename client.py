import socket
from Fichier import Fichier
import os
import hashlib
import configparser
from datetime import date
import json




config = configparser.ConfigParser()
config.read('extensions.conf')
allowed_extensions = config['Extensions']['allowed_extensions'].split(', ')


def get_absolute_path_hash():
    current_path = os.path.abspath(__file__)
    hash_object = hashlib.sha256(current_path.encode())
    return hash_object.hexdigest()

BASE_FOLDER = get_absolute_path_hash()

def clean_file_path(file_path):
    # Supprimer les références relatives (../)
    file_path = os.path.abspath(os.path.expanduser(file_path))

    # Supprimer les chemins absolus (C:, D:, etc.)
    if ':' in file_path:
        drive, path = os.path.splitdrive(file_path)
        if drive:
            file_path = path
    
    file_path = file_path.replace("/Users/"+os.getlogin()+"/","")
    file_path = file_path.replace("\\Users\\"+os.getlogin()+"\\","")

    file_path = os.path.join(".", BASE_FOLDER, date.today().strftime("%d-%m-%Y"), file_path)
    
    return file_path

def clean_file_path_for_retrieval(file_path,d):
    # Supprimer les références relatives (../)
    file_path = os.path.abspath(os.path.expanduser(file_path))

    # Supprimer les chemins absolus (C:, D:, etc.)
    if ':' in file_path:
        drive, path = os.path.splitdrive(file_path)
        if drive:
            file_path = path
    
    file_path = file_path.replace("/Users/"+os.getlogin()+"/","")
    file_path = file_path.replace("\\Users\\"+os.getlogin()+"\\","")
    file_path = os.path.join(".", BASE_FOLDER, d, file_path)
    return file_path

def load_logs():
    logs = {}
    if os.path.exists('logs.json'):
        with open('logs.json', 'r') as log_file:
            logs = json.load(log_file)
    return logs

def save_logs(logs):
    with open('logs.json', 'w') as log_file:
        json.dump(logs, log_file, indent=4)

def update_file_info(file_info, logs):
    if file_info["path"] in logs:
        if logs[file_info["path"]]["last_modified"] < file_info["last_modified"]:
            print(f"Le fichier {file_info['path']} a une version plus récente, envoi au serveur...")
            file_info["backup_date"] = logs[file_info["path"]]["backup_date"]
            return True
    else:
        print(f"Le fichier {file_info['path']} n'existe pas dans les logs, envoi au serveur...")
        return True
    print(f"Le fichier {file_info['path']} n'a pas été envoyé car cette version existe déjà à la date du {file_info['backup_date']}.")
    return False
   
def send_file(file_to_send, socket):
    if not file_to_send.get_path().split('.')[-1] in allowed_extensions:
        print(f"Le fichier {file_to_send.get_path()} n'est pas autorisé.")
        return

    print(f"Envoi du fichier : {file_to_send.get_path()}")
    content = file_to_send.read()
    last_modified = file_to_send.get_last_modified()

    logs = load_logs()

    file_info = {
        "path": file_to_send.get_path(),
        "last_modified": last_modified,
        "backup_date": date.today().strftime("%d-%m-%Y")
    }

    if update_file_info(file_info, logs):
        logs[file_info["path"]] = file_info
        save_logs(logs)
    
        file_to_send.set_path(clean_file_path(file_to_send.get_path()))
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

def recvall(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def retrieve_data(socket):
        # Recevoir la longueur du nom de fichier
        file_name_length = int.from_bytes(socket.recv(4), byteorder='big')
        # Recevoir le nom de fichier
        file_name = socket.recv(file_name_length).decode()
        print(f"Reception du fichier : {file_name}")
        # Recevoir la longueur du contenu du fichier
        file_content_length = int.from_bytes(socket.recv(4), byteorder='big')
        # Recevoir le contenu du fichier
        file_content = recvall(socket, file_content_length)
        #file_content = decrypt_file(file_content, key)
        # Créer une instance de la classe Fichier
        received_file = Fichier(file_name)
        received_file.content = file_content
        # Vérifier et enregistrer le fichier sur le serveur
        received_file.save_to_path()
        print(f"Fichier {file_name} reçu et enregistré.")    

def send_folder(folder_to_send, socket):
    for root, dirs, files in os.walk(folder_to_send.get_path()):
        for file in files:
            send_file(Fichier(os.path.join(root, file)), socket)
        for dir_name in dirs:
            send_folder(Fichier(os.path.join(root, dir_name)), socket)


def ask_retrieve_file(file_to_retrieve, socket):
    
    logs = load_logs()

    print(f"Recherche du fichier {file_to_retrieve.get_path()} dans les logs...")
    
    if file_to_retrieve.get_path() in logs.keys():
        # Le fichier existe dans les logs
        print(f"Le fichier {file_to_retrieve.get_path()} existe.")

        # Collecter les dates disponibles pour ce fichier
        file_dates = [info["backup_date"] for path, info in logs.items() if path == file_to_retrieve.get_path()]

        if len(set(file_dates)) > 1:
            print("Ce fichier existe pour plusieurs dates. Voici les dates disponibles :")
            for date in set(file_dates):
                print(date)

            chosen_date = input("Entrez la date pour laquelle récupérer le fichier : ")
            if chosen_date in file_dates:
                #print(f"Envoi du fichier {file_to_retrieve.get_path()} pour la date {chosen_date} au serveur.")
                # Envoi au serveur du path du fichier à récupérer pour la date choisie
                file_to_retrieve.set_path(clean_file_path_for_retrieval(file_to_retrieve.get_path(),chosen_date))
                file_name_length = len(file_to_retrieve.get_path())
                socket.send(file_name_length.to_bytes(4, byteorder='big'))
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
        
        retrieve_data(socket)
    else:
        print(f"Le fichier {file_to_retrieve.get_path()} n'existe pas dans les logs.")

def ask_retrieve_folder(folder_to_retrieve, socket):
    for root, dirs, files in os.walk(folder_to_retrieve.get_path()):
        for file in files:
            file_path = os.path.join(root, file)
            ask_retrieve_file(Fichier(file_path), socket)
    for dir_name in dirs:
        ask_retrieve_folder(Fichier(os.path.join(root, dir_name)), socket)


    

# Adresse IP et port du serveur
host = input("Entrez l'adresse IP du serveur : ")  # Mettez l'adresse IP du serveur ici
port = int(input("Entrez le port du serveur : "))  # Mettez le port du serveur ici

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
#shared_key = perform_diffie_hellman_client(client)

action=int(input("Entrez 1 pour envoyer un fichier, 2 pour récupérer un fichier : "))

if action == 1:
    client.send(int(1).to_bytes(4, byteorder='big'))
# Création d'une instance de la classe Fichier avec le chemin du fichier à envoyer
    to_send = Fichier(input("entrez le path du fichier : "))  # Remplacez par le chemin de votre fichier

    if os.path.isfile(to_send.get_path()):
        send_file(to_send, client)
    elif os.path.isdir(to_send.get_path()):
        send_folder(to_send, client)
    else:
        print("Le fichier ou dossier n'existe pas.")

    client.send(int(0).to_bytes(4, byteorder='big'))

elif action == 2:
    
    client.send(int(2).to_bytes(4, byteorder='big'))
    to_retrieve = Fichier(input("entrez le path du fichier : "))
    if os.name == 'nt':  # Si c'est Windows
        to_retrieve.set_path(to_retrieve.get_path().replace("/", "\\"))

    if os.path.isfile(to_retrieve.get_path()):
        ask_retrieve_file(to_retrieve, client)
    elif os.path.isdir(to_retrieve.get_path()):
        ask_retrieve_folder(to_retrieve, client)
    else:
        print("Le fichier ou dossier n'existe pas.")
    
    client.send(int(0).to_bytes(4, byteorder='big'))


client.close()