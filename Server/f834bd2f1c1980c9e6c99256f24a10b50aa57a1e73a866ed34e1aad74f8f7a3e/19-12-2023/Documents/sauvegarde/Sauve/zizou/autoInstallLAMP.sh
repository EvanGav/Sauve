#!/bin/bash

sudo apt update
read -p "Voulez-vous désinstaller LAMP,installer LAMP ou déployer un site ? (u/i/d) " action

  # Cette fonction permet de vérifier pour chaque argument de la fonction (les paquets à installer)  si il est installé et on l'installe si ce n'est pas le cas
  function verifyAndInstall(){
    for toInstall in $@
      do
        echo "verification pour $toInstall"
        if [ $(dpkg-query -W -f='${Status}' $toInstall 2>/dev/null | grep -c "ok installed") -eq 0 ]
          then
            echo "$toInstall non installe, installation en cours"
            sudo apt install $toInstall -y
          else
            echo "$toInstall est deja installe"
        fi
      done
  }  
  #zouzoufgdxsfsqzqfzefzq
  # Cette fonction permet de créer un site en fonction des réponses de l'utilisateur
  function createSite(){
    read -p "Quel est le nom du site ? " nom
    read -p "Quel est le suffixe du site [.com par exemple] ? " suf
    sudo touch /etc/apache2/sites-available/$nom.conf
    # si l'utilisateur choisi d'activer https, on créer le fichier de configuration du site avec les paramètres https
    if [ $@ = "y" ]
      then
        echo "<VirtualHost *:443>" >> /etc/apache2/sites-available/$nom.conf
        echo "ServerName $nom" >> /etc/apache2/sites-available/$nom.conf
        echo "ServerAlias www.$nom$suf" >> /etc/apache2/sites-available/$nom.conf
        echo "DocumentRoot /var/www/$nom" >> /etc/apache2/sites-available/$nom.conf
        echo "SSLEngine on" >> /etc/apache2/sites-available/$nom.conf
        echo "SSLCertificateFile /etc/ssl/certs/ssl.crt" >> /etc/apache2/sites-available/$nom.conf
        echo "SSLCertificateKeyFile /etc/ssl/private/ssl.key" >> /etc/apache2/sites-available/$nom.conf
        echo "<Directory /var/www/$nom>" >> /etc/apache2/sites-available/$nom.conf
        echo "Options -Indexes" >> /etc/apache2/sites-available/$nom.conf 
        echo "AllowOverride All" >> /etc/apache2/sites-available/$nom.conf
        echo "</Directory>" >> /etc/apache2/sites-available/$nom.conf
        echo "</VirtualHost>" >> /etc/apache2/sites-available/$nom.conf
      # sinon on créer le fichier de configuration du site avec les paramètres http
      else
        echo "<VirtualHost *:80>" >> /etc/apache2/sites-available/$nom.conf
        echo "ServerName $nom" >> /etc/apache2/sites-available/$nom.conf
        echo "ServerAlias www.$nom$suf" >> /etc/apache2/sites-available/$nom.conf
        echo "DocumentRoot /var/www/$nom" >> /etc/apache2/sites-available/$nom.conf
        echo "<Directory /var/www/$nom>" >> /etc/apache2/sites-available/$nom.conf
        echo "Options -Indexes" >> /etc/apache2/sites-available/$nom.conf 
        echo "AllowOverride All" >> /etc/apache2/sites-available/$nom.conf
        echo "</Directory>" >> /etc/apache2/sites-available/$nom.conf
        echo "</VirtualHost>" >> /etc/apache2/sites-available/$nom.conf
    fi
    # on créer le dossier du site et on copie le contenu du site dans le dossier
    sudo mkdir /var/www/$nom
    read -p "Quel est le path du site ? " path
    sudo cp -r $path /var/www/$nom
    # on active le site et on redémarre apache
    sudo a2ensite $nom
    sudo systemctl restart apache2
  }




  function verifyAndPurge(){
    for toDelete in $@
      do
        echo "verification pour $toDelete"
        if [ $(dpkg-query -W -f='${Status}' $toDelete 2>/dev/null | grep -c "ok installed") -eq 1 ]
          then
            echo "$toDelete  installe, purge en cours"
            sudo apt-get purge $toDelete
          else
            echo "$toDelete n'est pas installe"
        fi
      done
  }
  

function main(){
  if [[ $action == "u" ]]
    then
      echo "uninstalling ..."
      verifyAndPurge "apache2 php mysql-server phpmyadmin openssl"
  
  elif [[ $action == "d" ]]
    then
      read -p "Voulez-vous activer https ? (y/n) " cert
      echo "deploying ..."
      createSite $cert
  
  elif [[ $action == "i" ]]
    then
    echo "installing ..."
    verifyAndInstall "apache2 php mysql-server phpmyadmin"
    echo "Include /etc/phpmyadmin/apache.conf" | sudo tee -a /etc/apache2/apache2.conf > /dev/null
    echo "Include /etc/phpmyadmin/apache.conf" >> /etc/apache2/apache2.conf
    sudo chown -R www-data:www-data /usr/share/phpmyadmin
    sudo chmod -R 755 /usr/share/phpmyadmin
    sudo ln -sf /usr/share/phpmyadmin /var/www/html && echo "Created symlink"
    sudo ln -s /usr/share/phpmyadmin /var/www/html/phpmyadmin
    sudo systemctl restart apache2
    read -p "Voulez-vous activer https ? (y/n) " cert
    if [ "$cert" = "y" ]
      then
        verifyAndInstall "openssl"
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/ssl.key -out /etc/ssl/certs/ssl.crt
        sudo a2enmod ssl
        sudo a2ensite default-ssl
        sudo systemctl restart apache2
    fi
  else
    echo "Veuillez choisir une action valide"
    ./autoInstallLAMP.sh
  fi
}

main