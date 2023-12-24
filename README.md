# TD Sauvegarde
#### Gavrieli Evan
#### Afonso Alexandre

## Pré-requis

Afin de veiller au bon fonctionnement de l'application il faudrait tout d'abord executer le script init.sh comme ceci :

``` sh
cd path/to/Sauve
chmod 777 init.sh
./init.sh
```

## Lancement du server
Pour lancer le server, il suffira uniquement de lancer le programme comme ceci :
``` sh 
cd server
python3 server.py
```
Le server se mettra ensuite en attente d'une connexion à la socket

## Lancement d'un client
Pour lancer un client, il suffira uniquement de lancer le programme comme ceci :
``` sh 
cd client
python3 client.py
```

Suivez ensuite les instruction dictées sur la console, vous pouvez tester grâce au dossier :
``` sh
../TestFolder #a partir du dossier client
```

## Fonctionnement global

Lorsque vous allez lancer le programme et vous connecter au server via l'ip et le port, le server créera un thread afin de gérer cette connexion. Ensuite, vous devrez choisir 1 (envoyer un ou plusieurs fichiers à sauvegarder) ou 2 (récuperer un fichier). Cette action enverra un signal au server.

### Envoi

Lorsque vous allez envoyer un ou plusieurs fichiers au server, un fichier logs.json sera créer, celui-ci permettra de savoir quand a été éffectuée la dernière sauvegarde d'un fichier. Lors de l'envoi, si un fichier est présent dans logs.json et que la date de dernière modification est égale, alors on n'enverra pas le fichier. <br> <br>
Lorsque le server va recevoir un fichier, celui-ci va le placer dans un path envoyé par le client qui est généré grâce à un hash de l'emplacement du fichier et à la date actuelle pour mieux gérer les plusieurs clients possibles. Le server va ensuite chiffrer le contenu du fichier pour des raisons de sécurité. Il est à noter que le fichier est envoyé grâce au protocole TLS sécurisant la connexion entre les sockets. 

### Récupération
Lorsque vous demandez la récupération d'un ou plusieurs fichers, si celui-ci existe en plusieurs exemplaires à des dates différentes, il vous sera proposé d'entrer la date de la version que vous voulez. Une fois la demande faite, le server va déchiffrer le contenu du fichier au path donné et l'envoyer au client. Une fois le fichier récupéré celui-ci sera placé dans le dossier :
```sh
./backup #a partir du dossier client
```