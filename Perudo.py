#!/usr/bin/env python2
# -*- coding: utf8 -*-

import irclib
import ircbot
import random
import re

class PeruBot(ircbot.SingleServerIRCBot):

	state = 0
	players = {}
	order = []
	curr = 0
	nb = 0
	val = 0
	pal = False

	def __init__(self):
		ircbot.SingleServerIRCBot.__init__(self, [("irc.rezel.org", 6667)],
                                           "PerudoBot", "Bot pour jouer au Perudo écrit par traklon en Python à l'aide du module ircbot.")

	def on_welcome(self, serv, ev):
		serv.join("#perudo")

	def on_join(self, serv, ev):
		author = irclib.nm_to_n(ev.source())
		if self.state == 0:
			serv.privmsg("#perudo", "Bienvenue " + author + " ! Tape !join pour rejoindre ! Rappel : tapez !play pour lancer la partie !")
			
	def melange(self,serv, players):
		for player in self.players.iterkeys():
			d = self.players[player]
			for (i,e) in enumerate(d):
				d[i] = random.randint(1,6)
			self.players[player] = d
			serv.notice(player, "Tes dés sont : "+ ", ".join(map(str,d)))
	
	def verif(self, serv, players):
		somme = 0
		for player in self.players.iterkeys():
			tmp_nb = 0
			for e in self.players[player]:
				if ((e == self.val) or (e == 1)):
					tmp_nb = tmp_nb+1
			somme += tmp_nb
			serv.privmsg("#perudo", player + " révèle " + str(tmp_nb) + " " + str(self.val) + " !")
		return somme

        def verif_p(self, serv, players):
                somme = 0
                for player in self.players.iterkeys():
                        tmp_nb = 0
                        for e in self.players[player]:
                                if (e == self.val):
                                        tmp_nb = tmp_nb+1
                        somme += tmp_nb
                        serv.privmsg("#perudo", player + " révèle " + str(tmp_nb) + " " + str(self.val) + " !")
                return somme

	def reset(self):
		self.state = 0
		self.players = {}
		self.order = []
		self.curr = 0
		self.nb = 0
		self.val = 0			
		self.pal = False
			
	def on_pubmsg(self, serv, ev):
		author = irclib.nm_to_n(ev.source())
		chan = ev.target()
		message = ev.arguments()[0].lower()
		if message == "!regles":
			serv.privmsg("#perudo", "Rappel des règles : on doit obligatoirement augmenter le nombre de dés, mais pas forcément la valeur "+\
                                                         "du dé (sauf bien sûr en passant par les 1). 'exact' ne peut être tenté que par le joueur à qui"+\
                                                         " c'est le tour. On ne peut pas avoir plus de 5 dés. En 1 vs 1, 'exact' fait perdre un dé. "+\
                                                         "Si vous n'aimez pas ces règles, pingez 'traklon' pour l'insulter.")
		elif message == "!comm":
			serv.privmsg("#perudo", "Annoncer une valeur (ex : 4 fois le dé 6) : 4 6. On ne peut pas écrire paco pour les 1.")
			serv.privmsg("#perudo", "Annoncer 'exact' : exact OU dudo.")
			serv.privmsg("#perudo", "Confondre un menteur : menteur OU faux")
			serv.privmsg("#perudo", "Meta-jeu : !nbde pour le nombre total de dés. !ordre pour l'ordre du jeu"+\
							". !recap pour un récapitulatif du nombre de dés de chacun. !suiv pour avoir le nom du joueur suivant."+\
							" !quit pour annuler la partie.")
		elif message == "!nbde":
			somme = 0
			for player in self.players.iterkeys():
                                somme += len(self.players[player])
			serv.privmsg("#perudo", "Il y a " + str(somme) + " dés en jeu.")
		
		elif message == "!quit":
                        serv.privmsg("#perudo", "Partie annulée !")
			self.reset()

                elif message == "!recap":
                        for player in self.players.iterkeys():
                        	serv.privmsg("#perudo", player + " a " + str(len(self.players[player])) + " dés.")

		elif message == "!ordre":
                        serv.privmsg("#perudo", "L'ordre de jeu est : " + ", ".join(self.order))

		elif ((message == "!suiv") and (self.state > 0)):
                        serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")

		elif self.state == 0:
			if ((message == "!join") and (not (author in self.players))):
				serv.privmsg("#perudo", author + " a rejoint la partie !")
				self.players[author] = [1,1,1,1,1]
				self.order.append(author)
			if ((message == "!play") and (author in self.players)):
				serv.privmsg("#perudo", "La partie débute !")
				serv.privmsg("#perudo", "Tapez !regles pour connaître les règles en vigueur.")
				serv.privmsg("#perudo", "Tapez !comm pour connaîtres les commandes (normalement assez intuitives).")
				serv.privmsg("#perudo", "L'ordre de jeu est : "+ ", ".join(self.order))
				self.state = 1
				self.melange(serv, self.players)
					
		elif self.state == 1:
			self.pal = False
			if author == self.order[self.curr] :
				if re.match (r'^[1-9][0-9]* [1-6]$', message):
					tmp_nb = int(message[:-2])
					tmp_val = int(message[-1])
					if ((((self.val == 1) and (((tmp_val > 1) and (tmp_nb > 2*self.nb)) or ((tmp_val == 1) and (tmp_nb > self.nb)))) or ((self.val > 1) and (((tmp_val == 1) and (tmp_nb*2 >= self.nb)) or ((tmp_val > 1) and (tmp_nb > self.nb))))) or (self.val == 0)):
						self.nb = tmp_nb
						self.val = tmp_val
						self.curr = (self.curr+1)%(len(self.players))
						serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")
					else:
						serv.privmsg("#perudo", "Enchère erronée !")
				elif ((message == 'faux') or (message == 'menteur')):
					self.state = 2
				elif ((message == 'exact') or (message == 'dudo')):
					self.state = 3
				elif re.match (r'[0-9]+ [0-9]', message):
					serv.privmsg("#perudo", "Crétin.")
			else:
				if (re.match (r'[1-9][0-9]* [1-6]', message) or (message == ('exact' or 'dudo' or 'faux' or 'menteur'))):
					serv.privmsg("#perudo", author + " : ce n'est pas ton tour, mais celui de " + str(self.order[self.curr]) + " !")


                elif self.state == 4:
			self.pal = True
                        if author == self.order[self.curr] :
                                if re.match (r'^[1-9][0-9]* [1-6]$', message):
                                        tmp_nb = int(message[:-2])
                                        tmp_val = int(message[-1])
                                     	if (self.val == 0):
                                               	self.nb = tmp_nb
                                                self.val = tmp_val
       	                                        self.curr = (self.curr+1)%(len(self.players))
						serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")
					elif (tmp_val != self.val):
						serv.privmsg("#perudo", "Il y a Palifico ! Tu dois jouer les " + str(self.val) + " !")
					elif (tmp_nb > self.nb):
						self.nb = tmp_nb
						self.curr = (self.curr+1)%(len(self.players))
						serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")
					else:
						serv.privmsg("#perudo", "Enchère erronée ! Relisez !regles si besoin !")
						
                                elif ((message == 'faux') or (message == 'menteur')):
                                        self.state = 2
                                elif ((message == 'exact') or (message == 'dudo')):
                                        self.state = 3
                                elif re.match (r'[0-9]+ [0-9]', message):
                                       	serv.privmsg("#perudo", "Crétin.")
                        else:
				if (re.match (r'[1-9][0-9]* [1-6]', message) or (message == ('exact' or 'dudo' or 'faux' or 'menteur'))):
                               		serv.privmsg("#perudo", author + " : ce n'est pas ton tour, mais celui de " + str(self.order[self.curr]) + " !")

			
		if self.state == 2:
                        if self.pal:
                                somme = self.verif_p(serv, self.players)
                        else:
				somme = self.verif(serv, self.players)
			if (self.nb <= somme):
				serv.privmsg("#perudo", "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était correcte ! " + author + " perd un dé !")
			else:
				self.curr = (self.curr+len(self.players)-1)%(len(self.players))
				serv.privmsg("#perudo", "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était fausse ! " + self.order[self.curr] + " perd un dé !")

                        tmp = self.players[self.order[self.curr]]
			self.players[self.order[self.curr]] = tmp[1:]
			if len(tmp) == 1:
				serv.privmsg("#perudo", self.order[self.curr] + " est éliminé !")
				name = self.order[self.curr]
				self.order.remove(name)
				self.players.pop(name, None)
				if len(self.players) == 1:
					serv.privmsg("#perudo", self.order[0] + " a gagné ! Félicitations !")
					self.reset()
			if (len(self.players) > 1):
				serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")
				if len(tmp) == 2:
					serv.privmsg("#perudo", "PALIFICO !")
					self.state = 4
				else:
					self.state = 1
				self.melange(serv, self.players)
				self.nb = 0
				self.val = 0
			

                if self.state == 3:
			if self.pal:
				somme = self.verif_p(serv, self.players)
                        else:
				somme = self.verif(serv, self.players)
			tmp = self.players[self.order[self.curr]]
                        if (self.nb == somme):
				if (len(self.players) > 2):
                                	serv.privmsg("#perudo", "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était exacte ! " + author + " gagne un dé !")
					if len(self.players[author]) < 5:
						(self.players[author]).append(1)
					
				else:
        	                        self.curr = (self.curr+len(self.players)-1)%(len(self.players))
	                                serv.privmsg("#perudo", "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était exacte ! " + self.order[self.curr] + " perd un dé !")
	
                        else:
				serv.privmsg("#perudo", "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était inexacte ! " + author + " perd un dé !")
               	        	self.players[self.order[self.curr]] = tmp[1:]
               		if len(tmp) == 1:
                                serv.privmsg("#perudo", self.order[self.curr] + " est éliminé !")
				name = self.order[self.curr]
       		                self.order.remove(name)
                       		self.players.pop(name, None)
				if len(self.players) == 1:
					serv.privmsg("#perudo", self.order[0] + " a gagné ! Félicitations !")
					self.reset()
			if (len(self.players) > 1):
				serv.privmsg("#perudo", "C'est au tour de " + self.order[self.curr] + " !")
				if len(tmp) == 2:
      		                	serv.privmsg("#perudo", "PALIFICO !")
                              		self.state = 4	
	                        else:
               	              		self.state = 1
				self.melange(serv, self.players)
				self.nb = 0
				self.val = 0		
        

if __name__ == "__main__":
    	PeruBot().start()
