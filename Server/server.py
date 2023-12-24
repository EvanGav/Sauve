import socket
import threading
from file_storer import store_file
from backup_sender import receive_demand
import ssl

def handle_client(client_socket):
    """
    Cette fonction est exécutée dans un thread pour gérer la connexion cliente

    Args:
    - client_socket (socket): La socket du client connecté.

    """
    # On reçoit l'ordre du client (1 pour envoyer un fichier, 2 pour recevoir un fichier) sinon on ferme la connexion du client
    order = int.from_bytes(client_socket.recv(4), byteorder='big')
    if order == 1:
        # On appelle la fonction store_file pour recevoir le fichier du client et l'enregistrer dans le serveur
        store_file(client_socket)
 
    elif order == 2:
        # On appelle la fonction receive_demand pour envoyer le fichier demandé par le client
        receive_demand(client_socket)

    client_socket.close()



# Adresse IP et port du serveur
host = "127.0.0.1"
port = 3333

# On créer un socket pour le serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# On lie le socket à l'adresse IP et au port du serveur
server.bind((host, port))
# On écoute les connexions entrantes
server.listen(5)
#on initialise le contexte SSL
context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode=ssl.CERT_OPTIONAL
context.check_hostname=False

context.load_cert_chain(certfile="../cert/rootCA.pem", keyfile="../cert/rootCA.key")

context.load_verify_locations("../cert/rootCA.pem")

server_ssl=ssl.wrap_socket(server, ssl_version=ssl.PROTOCOL_TLSv1_2, server_side=True, certfile="../cert/rootCA.pem", keyfile="../cert/rootCA.key")


print(f"Serveur en attente de connexions sur le port {port}...")

while True:
    # On accepte les connexions clientes
    client_sock, addr = server_ssl.accept()
    print(f"Connexion entrante de {addr[0]}:{addr[1]}")

    # On démarre un thread pour gérer la connexion d'un ou plusieurs clients
    client_handler = threading.Thread(target=handle_client, args=(client_sock,))
    client_handler.start()
