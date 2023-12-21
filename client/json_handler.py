import json
import os

def load_logs():
    """
    Cette fonction charge les logs depuis le fichier logs.json s'il existe et renvoie un dictionnaire vide sinon.

    Returns:
    - dict: Contenu des logs chargé depuis le fichier 'logs.json' ou un dictionnaire vide.
    """
    # Initialise un dictionnaire vide pour les logs
    logs = {}
    # On vérifie si le fichier 'logs.json' existe
    if os.path.exists('logs.json'):
        # On ouvre le fichier 'logs.json' en mode lecture puis on met les logs dans le dictionnaire
        with open('logs.json', 'r') as log_file:
            logs = json.load(log_file)
    return logs

def save_logs(logs):
    """
    Cette fonction enregistre les logs dans le fichier 'logs.json'.

    Args:
    - logs (dict): Dictionnaire contenant les logs à enregistrer.
    """
    # Ouvre le fichier 'logs.json' en mode écriture
    with open('logs.json', 'w') as log_file:
        # Enregistre les logs dans le fichier 'logs.json' en format JSON
        json.dump(logs, log_file, indent=4)

def update_file_info(file_info, logs):
    """
    Cette fonction met à jour les informations sur un fichier dans les logs en comparant la date de dernière modification
    du fichier actuel avec celle enregistrée dans les logs. Si le fichier actuel est plus récent, elle ajuste les informations
    de sauvegarde pour le fichier à envoyer.

    Args:
    - file_info (dict): Informations sur le fichier à mettre à jour.
    - logs (dict): Logs actuels pour comparer les informations du fichier.

    Returns:
    - bool: Indique si le fichier doit être envoyé ou non.
    """
    # On vérifie si le chemin du fichier à mettre à jour existe déjà dans les logs
    if file_info["path"] in logs:
        if logs[file_info["path"]]["last_modified"] < file_info["last_modified"]:
            print(f"Le fichier {file_info['path']} a une version plus récente, envoi au serveur...")
            # On met à jour la date de sauvegarde avec celle du fichier actuel
            file_info["backup_date"] = logs[file_info["path"]]["backup_date"]
            return True
    else:
        print(f"Le fichier {file_info['path']} n'existe pas dans les logs, envoi au serveur...")
        #On envoie le fichier
        return True
    print(f"Le fichier {file_info['path']} n'a pas été envoyé car cette version existe déjà à la date du {file_info['backup_date']}.")
    #On envoie pas le fichier
    return False