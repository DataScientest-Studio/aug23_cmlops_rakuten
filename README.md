# **Challenge_Rakuten_py**

## Presentation et Installation
Ce projet s’inscrit dans le challenge Rakuten France Multimodal Product Data Classification: Il s’agit de prédire le code type de produits (tel que défini dans le catalogue Rakuten France) à partir d’une description texte et d’une image.

Rakuten France souhaite pouvoir catégoriser ses produits automatiquement grâce à la désignation, la description et les images des produits vendus sur son site.

Ce projet a été développé pendant notre formation de MLops avec le centre de formation Datascientest (https://datascientest.com/)

Notre équipe de développement du projet était composée de:
  * Flavien SAUX ([GitHub](https://github.com/Flav63s) / [LinkedIn](https://www.linkedin.com/in/flavien-s-712596190/))
  * Patricia WINTREBERT ([GitHub](https://github.com/patw47) / [LinkedIn](https://www.linkedin.com/in/patriciawintrebert/))
  * Mimoune LOUARRADI ([GitHub](https://github.com/mlouarra) / [LinkedIn](https://www.linkedin.com/in//))
  * Michaël DEVAUX ([GitHub](https://github.com/MichaelD24) / [LinkedIn](https://www.linkedin.com/in/michaël-devaux-362760139/))

## Déroulement du projet
Le projet suit un plan en plusieurs étapes :

* Collecte, exploration et préparation des données.
* Modélisation d'algorithmes de Deep Learning avec TensorFlow:
  * Réseau de neurones convolutifs (CNN (Resnet50)) pour la classification d'images,
  * Réseaux de neurones récurrents (RNN (BERT)) pour la classification de texte.
* Modèle de fusion, concatenation d'un modèle textuel (BERT) et d'un modèle image (Resnet50).
* Création d'une API avec 9 endpoints:
  * Le Main
  * Authentification des utilisateurs/administrateurs,
  * Interroger la base de données,
  * Obtention des prédictions du modèle pour le traitement de texte,
  * Obtention des prédictions du modèle pour le traitement des images,
  * Obtention des prédictions du modèle pour le traitement des combinaisons textes/images (fusion),
  * écriture dans les logs.
  * mise à jour de la base de données.
  * mise à jour/réentrainement du modèle si nécessaire.
* Isolation du projet via la création de contenaires Dockers, pilotage et déploiement du modèle de Deeplearning via Kubernetes.
* Amélioration de la vitesse de réponse du modèle déployé.
* Evolutions possibles du modèle.
  
## **Base de données**

Nous n'avons pas pu télécharger les données nécessaires sur GitHub, pour que vous puissiez refaire ce projet dans les mêmes conditions que nous.
Ces dernières étaient trop volumineuses pour être acceuillies sur notre espace.
Cependant, vous pouvez les télécharger sur le site [challengedata](https://challengedata.ens.fr/challenges/35).
Après vous êtes enregistré, vous pourrez accéder aux 4 fichiers composants les données.
* X_train_update.csv
* X_test_update.csv
* Y_train_CVw08PX.csv
* Le dossier contenant toutes les images
Dans notre projet, les données ont été imagé et entré dans le contenaire "Données".

## **API**
   ## API de Classification de Produits

Bienvenue dans l'API de Classification de Produits. Cette API permet de classer un produit en fonction d'une image et d'une description textuelle.

   ## Installation

1. Assurez-vous d'avoir Python 3.9 ou une version ultérieure installée.

2. Clonez ce dépôt Git sur votre ordinateur :

   ```bash
   git clone https://github.com/DataScientest-Studio/aug23_cmlops_rakuten.git

3. Accédez au répertoire du projet :
   
   ```bash
   cd aug23_cmlops_rakuten
   
4. Installez les dépendances :

   ```bash
   pip install -r requirements.txt

5. Lancez l'API à l'aide de la commande suivante :

   ```bash
   uvicorn main:app --reload
   ```
L'API sera disponible à l'adresse http://127.0.0.1:8000.
   
 ## Effectuer une classification de produit

 Utilisez un client HTTP ou un navigateur Web pour envoyer une requête POST à l'URL suivante : http://127.0.0.1:8000/predict.

 Vous devrez inclure une image et une description textuelle dans la requête.

 Vous pouvez aussi faire une requête par le terminal via l'outil Curl :

   ```bash
   curl -X POST "http://127.0.0.1:8000/predict" -F "text=Description du produit" -F "image=@chemin/vers/image.jpg"

Vous devez remplacer "Description du produit" par la description de votre produit et "chemin/vers/image.jpg" par le chemin de l'image du produit.

L'API renverra la catégorie prdtypecode et la thématique du produit.



