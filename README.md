
# **Challenge_Rakuten_py**

## Presentation et Installation
Ce projet s’inscrit dans le challenge Rakuten France Multimodal Product Data Classification: Il s’agit de prédire le code type de produits (tel que défini dans le catalogue Rakuten France) à partir d’une description texte et d’une image.

Rakuten France souhaite pouvoir catégoriser ses produits automatiquement grâce à la désignation, la description et les images des produits vendus sur son site.

Ce projet a été développé pendant notre formation de MLops avec le centre de formation Datascientest (https://datascientest.com/)

Notre équipe de développement du projet était composée de:
  * Flavien SAUX ([GitHub](https://github.com/Flav63s) / [LinkedIn](https://www.linkedin.com/in/flavien-s-712596190/))
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
* Y_train_CVw08PX.csv
* Le dossier contenant toutes les images
Dans notre projet, les données ont été imagé et entré dans le contenaire "Données".

## **API**
   ## API de Classification de Produits

Bienvenue dans les APIs de Classification de Produits. Elles permettent de classer un produit en fonction d'une image et d'une description textuelle.
L'administrateur peut quand à lui vérifier que la prédiction est bonne ou mauvaise, la modifier ou la supprimer. Les données prédites seront enregistrés dans une base de données qui sera utilisé pour l'amélioration continue du modèle.

   ## Installation

1. Clonez ce dépôt Git sur votre ordinateur:

   ```bash
   git clone https://github.com/DataScientest-Studio/aug23_cmlops_rakuten.git
   ```
2. Vérifier que vous avez le logiciel Docker soit ouvert sur votre machine.
   
3. Accédez au répertoire du projet :

   ```bash
   cd aug23_cmlops_rakuten/Projet_Rakuten_docker
   ```
   
4. Vérifier que vous êtes à l'intérieur du répertoire en tapant la commande et voyez le fichier 'docker-compose.yaml':

   ```bash
   ls
   ```

5. Lancez l'application à l'aide de la commande suivante :

   ```bash
   docker-compose up
   ```

A la suite de cette commande, l'installation peut prendre une dizaine de minutes pour installer les images.
<br>
Il se peut que vous rencontriez un dysfonctionnement concernant l'image Apache/Airflow 2.4, le message d'erreur sera qu'il ne trouve pas l'image.
<br>
Dans ce cas, refaites la commande précédente.
  

 ## Connection aux différentes API
 Connection à Swagger:
 L'API sera disponible à l'adresse http://localhost:8000/docs
 <br>
 Deux possibilités pour vous connecter:
 <br>
 "customer" : password "secret63" (accès à une seule route "predict")
 <br>
 "admin" : password "admin63" (accès à toutes les routes)

 Connection à Airflow:
 <br>
 Vous pouvez accéder à Airflow à l'adresse http://localhost:8080
 <br>
 Connection uniquement pour l'admin:
 <br>
 "admin" : "admin"

 ## Effectuer une classification de produit
 Quand vous êtes identifié, déplacez-vous sur la route "predict" où vous trouverez le bouton "try it out", cliquez dessus pour faire apparaître la demande de la désignation 
 du texte et de l'image.
 <br>
 Entrez un texte et téléchargez l'image puis appuyer sur le bouton "execute".
 <br>
 La désignation sera prédite avec un prdtypecode et la thèmatique du produit.
 <br>
 Après cette opération, il vous faudra obligatoirement être connecté commme administrateur pour avoir accès aux autres routes.

 ## Effectuer une vérification de la prédiction
 Dépacez vous sur la route "list_temp_data" et appuyez sur le bouton "try it out", et appuyez sur le bouton "execute".
 <br>
 Dans la cellule reponse Body, vous trouverez la désignation, le numéro de l'image dans colonne "img_pd", et la prédiction.
 <br>
 Pour visualiser l'image, veuillez copier l'URL et le collez dans votre navigateur.

 ## Validation des prédictions
 Copiez le numéro img_pd de la vérification de la prédiction précédente.
 <br>
 ex: ef1438b3-2a46-4279-8f2f-35c23e291329
 <br>
 Déplacez-vous sur la route "validation_prédiction".
 <br>
 Appuyez sur le bouton "try it out", collez le numéro dans la case "filename", utiliser le menu déroulant de validation "True" pour accepter, "False" pour refuser, ensuite 
 appuyez sur le bouton "execute".
 <br>
 Si vous validez en "True", cela déclenche un dag qui ajoute les données automatiquement au fichier image_4D, et au fichier .csv qui seront utilisé pour l'entrainement du 
 modèle.
 <br>
 Si vous validez en "False", les données sont transférées dans un dossier google drive qui sera utilisé en X_test pour l'entrainement du modèle.
 <br>
 Vous pouvez vérifier le google drive au lien suivant: https://drive.google.com/drive/folders/1gK4IP-h4f5eWf9wydGjDmYTWmjhawTco?usp=drive_link

 ## Modification des prédictions
 Pour modifier le prdtypecode, appuyer sur le bouton "try it out", coller le numéro img_pd dans filename de la route "modify_json".
 <br>
 Indiquer le prdtypecode qui convient au texte et à l'image.
 <br>
 Appuyez sur "execute".
 <br>
 Le prdtypecode sera modifié.

