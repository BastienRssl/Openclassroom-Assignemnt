#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 10:34:05 2018

@author: moi
"""

#client_interface.py

from tkinter import *
from threading import Thread
import socket
import sys
import signal


hote = "localhost"
port = 12600



class Interface(LabelFrame):
    
    
    def __init__(self,fenetre, text = 'Le Labyrinth', **kwargs):
        LabelFrame.__init__(self, fenetre, text = 'Le Labyrinth', cursor = "mouse", width = 400, height = 500)
        self.pack(fill = BOTH)
        self.pack_propagate(0)
        
        self.ecran = Label(self, text = "Lancement Application", font = "Menlo")
        self.ecran.pack(side = "top", fill = X)
        
        self.var_texte = StringVar()
        self.ligne_texte = Entry(fenetre, textvariable = self.var_texte, validatecommand = self.var_texte.get())
        self.ligne_texte.pack()
        self.ligne_texte.bind("<Return>", execution_commande)
    

class Reception(Thread):
    

    def __init__(self, interface):
        Thread.__init__(self)
        self.message = ''
        self.interface = interface
        
    
    def run(self):
        while True:
            try:
                self.message = connexion_avec_serveur.recv(1024)
                self.message = self.message.decode()
                self.interface.ecran["text"] = self.message
            except OSError:
                break


def execution_commande(event):
    texte = interface.var_texte.get()
    msg = texte.encode()
    connexion_avec_serveur.send(msg)
    interface.var_texte.set('')


#def fermer_application(signal, frame):
#    #thread_reception.join()
#    print("test")
#    sys.exit(0)
#    #interface.ecran["text"] = "Extinction à la régulière"
#    #thread_reception.join()
#    #connexion_avec_serveur.close()
#    #interface.destroyed()
#    #sys.exit(0)
#    
#
##signal.signal(signal.SIGTERM, fermer_application)


#Creation du socket de connexion
connexion_avec_serveur = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote,port))


fenetre = Tk()
interface = Interface(fenetre)

thread_reception = Reception(interface)
thread_reception.start()
       
interface.mainloop()

connexion_avec_serveur.close()

sys.exit(0)
            
            



