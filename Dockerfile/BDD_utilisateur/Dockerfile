
# Utilise l'image officielle Python version 3.9 comme image de base.
# Cette image inclut l'interpréteur Python 3.9 et est utilisée pour exécuter l'application.
FROM python:3.9

# Copie le fichier requirements.txt depuis le répertoire local vers le répertoire de travail dans le conteneur Docker.
# Ce fichier contient la liste des dépendances Python nécessaires pour l'application.
COPY requirements.txt .

# Copie le fichier authentification.py dans l'image Docker.
# Ce fichier contient le code source de l'application FastAPI pour l'authentification.
COPY authentification.py .

# Exécute la commande pip pour installer les dépendances Python spécifiées dans le fichier requirements.txt.
# L'option --no-cache-dir est utilisée pour réduire la taille de l'image en évitant de stocker le cache de pip.
RUN pip install --no-cache-dir -r requirements.txt

# Informe Docker que l'application écoute sur le port 8001.
# Cela n'expose pas le port automatiquement, mais sert de documentation et d'indication.
EXPOSE 8001

# Définit la commande par défaut à exécuter lorsque l'image est lancée.
# Ici, elle lance Uvicorn avec l'application FastAPI définie dans authentification.py, accessible à l'extérieur du conteneur sur le port 8001.
CMD ["uvicorn", "authentification:app", "--host", "0.0.0.0", "--port", "8001"]



