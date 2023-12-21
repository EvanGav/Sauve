import os

class Fichier:
    def __init__(self, path):
        self.path = path
        self.content = None
        self.last_modified = None

    def __repr__(self) -> str:
        return f"Fichier({self.path})", f"Contenu : {self.content}"

    def read(self):
        with open(self.path, 'rb') as file:
            return file.read()

    def get_path(self):
        return self.path
    
    def get_last_modified(self):
        return os.path.getmtime(self.path)
    
    def set_content(self, content):
        self.content = content

    def set_path(self, path):
        self.path = path

    def save_to_path(self):
        """
        Enregistre le contenu du fichier dans le chemin spécifié.
        Crée le dossier s'il n'existe pas.
        """
        folder_path = os.path.dirname(self.path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(self.path, 'wb') as file:
            file.write(self.content)

