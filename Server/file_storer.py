from Fichier import Fichier
from Encryption import xor_encrypt_decrypt


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

def store_file(client_socket):
    """
    Cette fonction permet stocker un fichier reçu depuis un client.

    Args:
    - client_socket (socket): La socket du client pour recevoir le fichier.
    """
    while True:
        # On reçoit la longueur du nom du fichier
        file_name_length = int.from_bytes(client_socket.recv(4), byteorder='big')
        #Si file_name_length == 0, alors on n'a plus de fichier à recevoir
        if file_name_length == 0:
            break  # On termine la reception des fichiers
        # On reçoit le nom du fichier
        file_name = client_socket.recv(file_name_length).decode()
        print(f"Reception du fichier : {file_name}")
        # On reçoit la longueur du contenu du fichier
        file_content_length = int.from_bytes(client_socket.recv(4), byteorder='big')
        # On reçoit le contenu du fichier puis on le chiffre
        file_content = recvall(client_socket, file_content_length)
        file_content = xor_encrypt_decrypt(file_content)
        # On le transforme en Fichier
        received_file = Fichier(file_name)
        received_file.content = file_content
        # On vérifie et on enregistre le fichier sur le serveur
        received_file.save_to_path()
        print(f"Fichier {file_name} reçu et enregistré.")