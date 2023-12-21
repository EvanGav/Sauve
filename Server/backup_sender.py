from Fichier import Fichier
from Encryption import xor_encrypt_decrypt

def send_backup_file(file_to_send, socket):
    """
    Cette fonction envoie un fichier déchiffré au client à travers la socket.

    Args:
    - file_to_send (Fichier): le fichier à envoyer.
    - socket (socket): Socket pour communiquer avec le client.
    """
    print(f"Envoi du fichier : {file_to_send.get_path()}")
    # On lit le contenu du fichier à envoyer
    content = file_to_send.read()
    # On le déchiffre
    content = xor_encrypt_decrypt(content)
    # On modifie le chemin du fichier pour le stockage de sauvegarde
    file_to_send.set_path(file_to_send.get_path().replace("./", "./backup/"))
    file_to_send.set_path(file_to_send.get_path().replace(".\\", ".\\backup\\"))
    print(f"Nom du fichier nettoyé : {file_to_send.get_path()}")
    # On envoie la longueur du nom du fichier
    file_name_length = len(file_to_send.get_path())
    socket.send(file_name_length.to_bytes(4, byteorder='big'))
    # On envoie le nom du fichier
    socket.send(file_to_send.get_path().encode())
    print(f"Nom du fichier envoyé : {file_to_send.get_path()}")
    # On envoie la longueur du contenu du fichier
    file_content_length = len(content)
    socket.send(file_content_length.to_bytes(4, byteorder='big'))
    # On envoie le contenu
    socket.send(content)
    print(f"Le fichier {file_to_send.get_path()} a été envoyé.")


def receive_demand(client_socket):
    """
    Cette fonction reçoit une demande de fichier du client et envoie le fichier demandé.

    Args:
    - client_socket (socket): Socket pour communiquer avec le client.
    """
    while True:
        # On reçoit la longueur du nom du fichier
        file_name_length = int.from_bytes(client_socket.recv(4), byteorder='big')
        #Si file_name_length == 0, alors on n'a plus de fichier à envoyer
        if file_name_length == 0:
            break  # Terminer la réception des fichiers
        # On reçoit le nom de fichier
        file_name = client_socket.recv(file_name_length).decode()
        print(f"Envoi du fichier : {file_name}")
        # On envoie le fichier au client
        send_backup_file(Fichier(file_name), client_socket)