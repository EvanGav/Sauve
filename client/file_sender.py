from datetime import date
import os
import configparser
from Fichier import Fichier
from json_handler import *
from base_position import BASE_FOLDER



#On charge le fichier .conf pour savoir quels fichiers sont autorisés
config = configparser.ConfigParser()
config.read('extensions.conf')
allowed_extensions = config['Extensions']['allowed_extensions'].split(', ')


def clean_file_path(file_path):
    """
    Cette fonction modifie le path du fichier pour correspondre au serveur.

    Args:
    - file_path (str): Chemin du fichier à nettoyer.

    Returns:
    - str: Chemin vers le dossier de sauvegarde correspondant.
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

    file_path = os.path.join(".", BASE_FOLDER, date.today().strftime("%d-%m-%Y"), file_path)
    
    return file_path

def send_file(file_to_send, socket):
    """
    Cette fonction envoie un fichier au client via une socket après avoir vérifié s'il est autorisé. Elle met aussi à jour les logs avec les informations sur le fichier envoyé.

    Args:
    - file_to_send (Fichier): Le fichier à envoyer.
    - socket (socket): Socket à utiliser pour l'envoi du fichier.
    """
    #On vérifie si l'extension du ficheir est autorisée
    if not file_to_send.get_path().split('.')[-1] in allowed_extensions:
        print(f"Le fichier {file_to_send.get_path()} n'est pas autorisé.")
        return

    print(f"Envoi du fichier : {file_to_send.get_path()}")
    #On récupère le contenu et la date de dernière modification
    content = file_to_send.read()
    last_modified = file_to_send.get_last_modified()
    #On charge le fichier logs (JSON)
    logs = load_logs()
    if os.name == 'nt':  # Si c'est Windows
        file_to_send.set_path(file_to_send.get_path().replace("/", "\\"))
    #On met les informations au format JSON
    file_info = {
        "path": file_to_send.get_path(),
        "last_modified": last_modified,
        "backup_date": date.today().strftime("%d-%m-%Y")
    }
    print(f"Le path du file_info est : {file_info['path']}")
    #Si on peut mettre à jour les infos du fichier logs, on les change et on sauvegarde
    if update_file_info(file_info, logs):
        logs[file_info["path"]] = file_info
        save_logs(logs)
        #On change le path pour le serveur
        file_to_send.set_path(clean_file_path(file_to_send.get_path()))
        print(f"Nom du fichier nettoyé : {file_to_send.get_path()}")
        #On envoie la longueur du nom du fichier
        file_name_length = len(file_to_send.get_path())
        socket.send(file_name_length.to_bytes(4, byteorder='big'))
        # On envoie le nom du fichier
        socket.send(file_to_send.get_path().encode())
        print(f"Nom du fichier envoyé : {file_to_send.get_path()}")
        # On envoie la longueur du contenu puis le contenu
        file_content_length = len(content)
        socket.send(file_content_length.to_bytes(4, byteorder='big'))
        socket.send(content)

        print(f"Le fichier {file_to_send.get_path()} a été envoyé.")


def send_folder(folder_to_send, socket):
    """
    Cette fonction permet d'envoyer un dossier au serveur.

    Args:
    - folder_to_send (Fichier): Objet représentant le dossier à envoyer.
    - socket (socket): Socket à utiliser pour l'envoi des fichiers.
    """
    for root, dirs, files in os.walk(folder_to_send.get_path()):
        for file in files:
            #Si on tombe sur un fichier, on le sauvegarde
            send_file(Fichier(os.path.join(root, file)), socket)
        for dir_name in dirs:
            #Si c'est un dossier on appelle récursivement la fonction
            send_folder(Fichier(os.path.join(root, dir_name)), socket)