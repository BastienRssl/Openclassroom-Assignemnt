#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 13:31:13 2018

@author: moi
"""

#serveur_interface.py

import fonctions_serveur
import socket
import select
import time
import os
import re

hote = ''
port = 12600

#Création du socket de connexion
connexion_principale = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connexion_principale.bind((hote,port))
connexion_principale.listen(5)

#Affichage du menu serveur/Sélection d'une carte/Traduction de la carte texte en tableau
carte_path = fonctions_serveur.lancement()
carte_tableau = fonctions_serveur.carte_encodage(carte_path)


#Attente des joueurs et de la commande commencer de la part d'un joueur
clients_connectes = []
attente = True
while attente:
    connexions_demandees, wlist, xlist = select.select([connexion_principale],[],[],0.05)
    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        clients_connectes.append(connexion_avec_client)
        connexion_avec_client.send(b"Vous etes connecte")
        print(clients_connectes)
    
    time.sleep(1)
    
    try:
        if len(clients_connectes) >= 2:
            for client in clients_connectes:
                client.send(b"\nAppuyer sur c pour lancer la partie :")
        else:
            for client in clients_connectes:
                client.send(b"\nEn attente de joueurs...")
    except BrokenPipeError:
        clients_connectes.remove(client)

    
    if clients_connectes == []:
        pass
    else:
        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes,[],[],0.05)
        except select.error:
            pass
        else:
            for client in clients_a_lire:
                try:
                    msg_recu = client.recv(1024)
                    msg_recu = msg_recu.decode()
        
                    if msg_recu == 'c' and len(clients_connectes) >= 2:
                        attente = False
                    else:
                        pass
                except ConnectionResetError:
                    clients_connectes.remove(client)
                                             
    time.sleep(0.05)

#Initialisation de la carte/Positionement d'un robot distinct par joueur
liste_robots = ['X','A','B','C','D']
for i, client in enumerate(clients_connectes):
    carte_tableau = fonctions_serveur.initialisation(carte_tableau, liste_robots[i])
    
       
#Envoi de la carte initialisée à chaque joueur avec son robot de précisé
carte_texte = fonctions_serveur.carte_decodage(carte_tableau)


#Jeux au tour par tour    
j = 1 
continuer = True
while continuer:

    for i, client in enumerate(clients_connectes):
            try:
                robot = liste_robots[i]
                msg_legende = "\n\nTour-{}, Robot-{}, Veuillez choisir une direction :".format(j,robot)
                msg = carte_texte + msg_legende
                msg = msg.encode()
                client.send(msg)
            except (BrokenPipeError, OSError):
                clients_connectes.remove(client)
    
    j += 1
    
    clients_restants = list(clients_connectes)
    tour_incomplet = True
    clients_tour = []
    
    while tour_incomplet:
        
        if clients_connectes == []:
            tour_incomplet = False
            continuer = False
        else:
            try:
                clients_a_lire, wlist, xlist = select.select(clients_connectes,[],[],0.05)
            except select.error:
                pass
            else:
                for client in clients_a_lire:
                    try:
                        if client in clients_restants:
                            clients_tour.append(client)
                            clients_restants.remove(client)
            
                            for i, customer in enumerate(clients_connectes):
                                if customer == client:
                                    robot = liste_robots[i]
                            
                            msg_action = client.recv(1024)
                            msg_action = msg_action.decode()
            
                            x,y = fonctions_serveur.position_identification(carte_tableau, robot)
                            
                            if fonctions_serveur.action(carte_tableau, x, y, msg_action) == 'conflit':
                                msg_legende = "\n\nAction impossible, veuillez resaisir une action :"
                                msg = carte_texte + msg_legende
                                msg = msg.encode()
                                client.send(msg)
                                msg_action = client.recv(1024)
                                msg_action = msg_action.decode()
                                while fonctions_serveur.action(carte_tableau, x, y, msg_action) == 'conflit':
                                    msg_legende = "\n\nAction impossible, veuillez resaisir une action :"
                                    msg = carte_texte + msg_legende
                                    msg = msg.encode()
                                    client.send(msg)
                                    msg_action = client.recv(1024)
                                    msg_action = msg_action.decode()
                                x, y, action = fonctions_serveur.action(carte_tableau, x, y, msg_action)
                                carte_tableau = fonctions_serveur.mise_a_jour_carte(carte_tableau, x, y, robot, action)
                            elif fonctions_serveur.action(carte_tableau, x, y, msg_action) == 'victoire':
                                msg_final = "\nLe robot {} remporte la partie !\n".format(robot)
                                msg_final = msg_final.encode()
                                continuer = False
                                print("partie terminee")
                            else:
                                x, y, action = fonctions_serveur.action(carte_tableau, x, y, msg_action)
                                carte_tableau = fonctions_serveur.mise_a_jour_carte(carte_tableau, x, y, robot, action)
                        
                            carte_texte = fonctions_serveur.carte_decodage(carte_tableau)
                            
                            if len(clients_restants) != 0:
                                msg_legende = "\nEn attente des autres joueurs..."
                                msg = carte_texte + msg_legende
                                msg = msg.encode()
                                client.send(msg)
                            
                        if len(clients_restants) == 0:
                            tour_incomplet = False

                    except (BrokenPipeError, OSError):
                        clients_connectes.remove(client)


time.sleep(2)

    
if len(clients_connectes) != 0:
    print("\nEnvoi du message de fin")
    try:
        for client in clients_connectes:
            client.send(msg_final)
    except (BrokenPipeError, OSError):
        clients_connectes.remove(client)
    

    time.sleep(2)


    try:
        for client in clients_connectes:
            client.send(b"Fermeture de l'application en cours...")
    except(BrokenPipeError, OSError):
        clients_connectes.remove(client)
      
        
    time.sleep(2)
    
    
    #Récupération des PID des processus clients & arret des processus clients récupérés
    cmd = os.popen("ps")
    cmd = cmd.read()
    cmd = cmd.split("\n")
    regex_pid = r"[0-9]{1,} "
    
    
    
    liste_PID = []
    for chaine in cmd:
        if chaine.find('python client_interface.py') != -1:
            PID_test = re.search(regex_pid, chaine)
            PID_found = PID_test.group(0)
            liste_PID.append(PID_found)
    
    try:
        for PID in liste_PID:
            cmd = "kill " + PID
            os.system(cmd)
    except:
        print("kill error")
    
    try:
        for client in clients_connectes:
            client.close()
    except(BrokenPipeError, OSError): 
        pass

    connexion_principale.close()
    
connexion_principale.close()
