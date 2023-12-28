#!/bin/sh

# Copier les fichiers initiaux depuis le drive
rclone --config /rclone.conf copy "Projet_rakuten_MLOPS:Model/CSV_Rakuten_MLOPS.csv" /drive
chmod 777 /drive/CSV_Rakuten_MLOPS.csv

rclone --config /rclone.conf copy "Projet_rakuten_MLOPS:Model/combined_model_trained_after_resume.h5" /drive
chmod 777 /drive/combined_model_trained_after_resume.h5

rclone --config /rclone.conf copy "Projet_rakuten_MLOPS:Model/matrice_photo_4D.npy" /drive
chmod 777 /drive/matrice_photo_4D.npy




sync_to_drive() {
    echo "Copying files to drive"
    rclone --config /rclone.conf copy /drive Projet_rakuten_MLOPS:Model
}



sync_csv_to_drive() {
    echo "Copying CSV to drive"
    rclone --config /rclone.conf copy /drive/csv Projet_rakuten_MLOPS:CSV
    echo "Deleting local CSV files"
    rm -rf /drive/csv/*
}


sync_jpg_to_drive() {
    echo "Copying JPG to drive"
    rclone --config /rclone.conf copy /drive/jpg Projet_rakuten_MLOPS:JPG
    echo "Deleting local JPG files"
    rm -rf /drive/jpg/*
}


sync_npy_to_drive() {
    echo "Copying NPY to drive"
    rclone --config /rclone.conf copy /drive/npy Projet_rakuten_MLOPS:NPY
    echo "Deleting local NPY files"
    rm -rf /drive/npy/*
}



# Surveillance du dossier /drive pour les modifications
while inotifywait -r -e modify,create,delete /drive; do
    sync_to_drive
done