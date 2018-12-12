#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 15:54:39 2018

@author: Bastien Roussel
"""

#fonctions_serveur.py
from random import randint
import glob
import os
import re


liste_robots = ['X','A','B','C','D']



class Carte():
    """Une carte est un fichier txt, sauvegardé dans le répertoire Cartes/ 
    et dont le nom est ajouté au dictionnaire de la classe lors de sa création""" 


    carte_liste = glob.glob("Cartes/*.txt")
    les_cartes = {}

    for path in carte_liste:
        carte_name = os.path.basename(path)
        carte_name_bis = carte_name.split(".")
        carte_name = carte_name_bis[0]
        les_cartes[carte_name] = path
    
    
    def __init__(self,nom):
        
        self.nom = nom
        chemin_fichier = "Cartes/" + str(nom) + ".txt"
        fichier = open(chemin_fichier,'w')
        Carte.les_cartes[str(nom)] = chemin_fichier
        fichier.close()


def lancement():
    """Menu affiché au lancement du serveur (côté serveur), 
    permettant de selectionner une carte"""
    
    print("\nLabyrinthes existants :")
    
    i = 1
    options = {}
    for cle, value in Carte.les_cartes.items():
        options[str(i)] = value
        print("{} - {}".format(i,cle))
        i += 1
        
    selection = input("\nEntrez un numéro de Labyrinth pour commencer : ")
    print("\nOn attend les clients ...")
    return options[selection]


def carte_encodage(carte_path):
    """Traduit le texte compris dans un fichier carte.txt en un tableau manipulable"""
    
    fichier = open(carte_path, 'r')
    texte_liste = fichier.readlines()
    fichier.close()
    
    carte_tableau = []
    for elt in texte_liste:
        ligne_decomposee = []
        for elemt in elt:
            ligne_decomposee.append(elemt)
        carte_tableau.append(ligne_decomposee)
    
    return carte_tableau

    
def carte_decodage(carte_tableau):
    """Traduit une carte tableau en carte string"""
    liste_intermediaire = []
    for elt in carte_tableau:
        ligne = "".join(elt)
        liste_intermediaire.append(ligne)
    carte_texte = "".join(liste_intermediaire)
    return carte_texte
    
    
def initialisation(carte_tableau, X):
    """Place aléatoirement 'X' sur un emplacement vide de la carte"""
    
    cherche_position = True
    while cherche_position:
        borne_sup = len(carte_tableau) - 1
        num_ligne = randint(0,borne_sup)
        borne_sup_bis = len(carte_tableau[num_ligne]) - 2
        num_colonne = randint(0,borne_sup_bis)
        if carte_tableau[num_ligne][num_colonne] == ' ':
            carte_tableau[num_ligne][num_colonne] = str(X)
            cherche_position = False
        else:
            pass
        
    return carte_tableau
    

def position_identification(carte_tableau, X):
    """Identifie les coordonnées du robot dans la carte """
    
    for i, elt in enumerate(carte_tableau):
        for j, elmt in enumerate(elt):
            if elmt == str(X):
                return (i, j)
            else:
                pass 
    
    
def action(carte_tableau, x, y, action_msg):
    
    regex_action = r"^[NnSsOoEe][PpMm]$"
    regex_deplacement = r"^[NnSsOoEe]$"
              
    if re.search(regex_action, action_msg) is not None:
        if action_msg[0] in ['N', 'n']:
            x_test = x - 1
            y_test = y
        elif action_msg[0] in ['S', 's']:
            x_test = x + 1
            y_test = y
        elif action_msg[0] in ['E', 'e']:
            x_test = x
            y_test = y + 1
        elif action_msg[0] in ['O', 'o']:
            x_test = x
            y_test = y - 1
        
        if carte_tableau[x_test][y_test] == 'U' or carte_tableau[x_test][y_test] in liste_robots:
            return 'conflit'
        else:
            if action_msg[1] in ['P', 'p']:
                return (x_test, y_test, 'percer')
            else:
                return (x_test, y_test, 'murer')
            
    elif re.search(regex_deplacement, action_msg):
        if action_msg in ['N', 'n']:
            x_test = x - 1
            y_test = y
        elif action_msg in ['S', 's']:
            x_test = x + 1
            y_test = y
        elif action_msg in ['E', 'e']:
            x_test = x
            y_test = y + 1
        else:
            x_test = x
            y_test = y - 1
        
        
        if x_test > len(carte_tableau) - 2:
            return "conflit"
        elif y_test > len(carte_tableau[x_test]) - 2:
            return "conflit"
        else:
            pass
        
        
        if carte_tableau[x_test][y_test] == 'O'or carte_tableau[x_test][y_test] in liste_robots:
            return "conflit"
        elif carte_tableau[x_test][y_test] == 'U':
            return "victoire"
        else:
            return (x_test, y_test, 'deplacer')
    
    else:
        return 'conflit'
    

def mise_a_jour_carte(carte_tableau, x, y, X, action):
    """Met à jour la carte en positionnant le robot sur 
    la coordonnée (x,y) rentrée en paramétre"""
    
    if action == 'deplacer':
        x_init, y_init = position_identification(carte_tableau, X)
        carte_tableau[x_init][y_init] = " "
        carte_tableau[x][y] = str(X)
    elif action == 'percer':
        carte_tableau[x][y] = ' '
    else:
        carte_tableau[x][y] = 'O'
    
    return carte_tableau


    

    
