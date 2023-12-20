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

    file_path = "./" + BASE_FOLDER +"/"+date.today().strftime("%d-%m-%Y")+"/" + file_path
    
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

client.send(int(0).to_bytes(4, byteorder='big'))

client.close()