
# Utilise l'image officielle Python version 3.10 comme image de base.
FROM python:3.10

# Copie le fichier main.py depuis le répertoire local vers le répertoire de travail dans l'image Docker.
COPY main.py .

# Copie le fichier requirements.txt, qui liste toutes les dépendances Python nécessaires, dans l'image Docker.
COPY requirements.txt .

# Copie le script script_de_prediction.py dans l'image Docker.
COPY script_de_prediction.py .

# Exécute la commande pip pour installer les packages Python spécifiés dans le fichier requirements.txt.
# L'option --no-cache-dir est utilisée pour réduire la taille de l'image en n'enregistrant pas le cache de pip.
RUN pip install --no-cache-dir -r requirements.txt

# Informe Docker que l'application écoute sur le port 8000.
# Cela n'expose pas le port, mais sert de documentation entre le créateur de l'image et l'utilisateur de l'image.
EXPOSE 8000

# Définit la commande par défaut à exécuter lorsque l'image est lancée. 
# Ici, elle lance Uvicorn avec l'application FastAPI définie dans main.py, accessible à l'extérieur du conteneur.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]



