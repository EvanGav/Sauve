
import os
import hashlib

def get_absolute_path_hash():
    """
    Cette fonction génère un hash basé sur le chemin absolu du fichier actuel.

    Returns:
    - str: Le hash du chemin absolu du fichier.
    """
    # On récupère le chemin absolu du fichier actuel
    current_path = os.path.abspath(__file__)
    # On crée un objet pour le hachage en SHA-256
    hash_object = hashlib.sha256(current_path.encode())
    # On renvoie le hash sous forme de chaîne hexadécimale
    return hash_object.hexdigest()

BASE_FOLDER = get_absolute_path_hash()