# Utiliser une image de base Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt ./

# Installer les dépendances, y compris MLflow
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mlflow


# Exposer le port pour le serveur MLflow
EXPOSE 5001

# Définir la commande par défaut pour lancer MLflow
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5001"]
