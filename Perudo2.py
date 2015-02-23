#!/usr/bin/env python2
# -*- coding: utf8 -*-

import irclib
import ircbot
import random
import re
import sys

class PeruBot(ircbot.SingleServerIRCBot):

    server = sys.argv[1]
    chan = '#'+sys.argv[2]
    state = 'PRE-JEU'
    players = {}
    order = []
    curr = 0
    nb = 0
    val = 0
    palifico = False

    def __init__(self):
        ircbot.SingleServerIRCBot.__init__(self, [(self.server, 6667)],
                                           "PeruBot", "Bot pour jouer au Perudo écrit par traklon en Python à l'aide du module ircbot.")

    def on_welcome(self, serv, ev):
        serv.join(self.chan)

    def on_join(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        if self.state == 'PRE-JEU':
            serv.privmsg(self.chan, "Bienvenue " + author + " ! Tape !join pour rejoindre ! Rappel : tapez !play pour lancer la partie !")

    def melange(self,serv):
        for player in self.players.iterkeys():
            d = self.players[player]
            for (i,e) in enumerate(d):
                d[i] = random.randint(1,6)
            self.players[player] = d
            serv.notice(player, "Tes dés sont : "+ ", ".join(map(str,d)))

    def verif(self, serv):
        somme = 0
        for player in self.players.iterkeys():
            tmp_nb = 0
            for e in self.players[player]:
                if ((e == self.val) or ((e == 1) and (not self.palifico))):
                    tmp_nb = tmp_nb+1
            somme += tmp_nb
            serv.privmsg(self.chan, player + " révèle " + str(tmp_nb) + " " + str(self.val) + " !")
        return somme

    def verif_elimination(self, serv):
        if len(self.players[self.order[self.curr]]) == 0:
            serv.privmsg(self.chan, self.order[self.curr] + " est éliminé !")
            name = self.order[self.curr]
            self.order.remove(name)
            self.players.pop(name, None)
            self.curr = (self.curr)%(len(self.players))

    def verif_gg(self, serv):
        if len(self.players) == 1:
            serv.privmsg(self.chan, self.order[0] + " a gagné ! Félicitations !")
            self.reset()
            return True
        return False

    def verif_1de(self, serv):
        if len(self.players[self.order[self.curr]]) == 1:
            serv.privmsg(self.chan, "PALIFICO !")
            self.palifico = True
        else:
            self.palifico = False

    def reset(self):
        self.state = 'PRE-JEU'
        self.players = {}
        self.order = []
        self.curr = 0
        self.nb = 0
        self.val = 0
        self.palifico = False

    def nouv_tirage(self, serv):
         self.verif_1de(serv)
         self.verif_elimination(serv)
         if (not self.verif_gg(serv)):
            serv.privmsg(self.chan, "C'est au tour de " + self.order[self.curr] + " !")
            self.state = 'ENCHERES'
            self.nb = 0
            self.val = 0
            self.melange(serv)

    def on_pubmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0].lower()
        if message == "!regles":
            serv.privmsg(self.chan, "Rappel des règles : on doit obligatoirement augmenter le nombre de dés, mais pas forcément la valeur "+\
                                                         "du dé (sauf bien sûr en passant par les 1). 'exact' ne peut être tenté que par le joueur à qui"+\
                                                         " c'est le tour. On ne peut pas avoir plus de 5 dés. En 1 vs 1, 'exact' fait perdre un dé. "+\
                                                         "Si vous n'aimez pas ces règles, pingez 'traklon' pour l'insulter.")
        elif message == "!comm":
            serv.privmsg(self.chan, "Annoncer une valeur (ex : 4 fois le dé 6) : 4 6. On ne peut pas écrire paco pour les 1.")
            serv.privmsg(self.chan, "Annoncer 'exact' : exact OU calza.")
            serv.privmsg(self.chan, "Confondre un menteur : menteur OU dudo OU faux")
            serv.privmsg(self.chan, "Meta-jeu : !nbde pour le nombre total de dés. !ordre pour l'ordre du jeu"+\
                            ". !recap pour un récapitulatif du nombre de dés de chacun. !suiv pour avoir le nom du joueur suivant."+\
                            " !quit pour annuler la partie.")
        elif message == "!nbde":
            somme = 0
            for player in self.players.iterkeys():
                somme += len(self.players[player])
                serv.privmsg(self.chan, "Il y a " + str(somme) + " dés en jeu.")

        elif message == "!quit":
            serv.privmsg(self.chan, "Partie annulée !")
            self.reset()

        elif message == "!recap":
            for player in self.players.iterkeys():
                serv.privmsg(self.chan, player + " a " + str(len(self.players[player])) + " dés.")

        elif message == "!ordre":
            serv.privmsg(self.chan, "L'ordre de jeu est : " + ", ".join(self.order))

        elif ((message == "!suiv") and (self.state != 'PRE-JEU')):
            serv.privmsg(self.chan, "C'est au tour de " + self.order[self.curr] + " !")

        elif self.state == 'PRE-JEU':
            if ((message == "!join") and (not (author in self.players))):
                serv.privmsg(self.chan, author + " a rejoint la partie !")
                self.players[author] = [1,1,1,1,1]
                self.order.append(author)
            if ((message == "!play") and (author in self.players)):
                if (len(self.players) == 1):
                    serv.privmsg(self.chan, "Jouer seul, c'est pas super intéressant...")
                else:
                    serv.privmsg(self.chan, "La partie débute !")
                    serv.privmsg(self.chan, "Tapez !regles pour connaître les règles en vigueur.")
                    serv.privmsg(self.chan, "Tapez !comm pour connaîtres les commandes (normalement assez intuitives).")
                    serv.privmsg(self.chan, "L'ordre de jeu est : "+ ", ".join(self.order))
                    self.state = 'ENCHERES'
                    self.melange(serv)

        elif self.state == 'ENCHERES':
            if author == self.order[self.curr] :
                if re.match (r'^[1-9][0-9]* [1-6]$', message):
                    tmp_nb = int(message[:-2])
                    tmp_val = int(message[-1])
                    if self.palifico :
                        verif = (tmp_val == self.val) and (tmp_nb > self.nb)
                    else:
                        verif = (((self.val == 1) and (((tmp_val > 1) and (tmp_nb > 2*self.nb)) or ((tmp_val == 1) and (tmp_nb > self.nb)))) or ((self.val > 1) and (((tmp_val == 1) and (tmp_nb*2 >= self.nb)) or ((tmp_val > 1) and (tmp_nb > self.nb)))))
                    if (verif or (self.val == 0)):
                         self.nb = tmp_nb
                         self.val = tmp_val
                         self.curr = (self.curr+1)%(len(self.players))
                         serv.privmsg(self.chan, "C'est au tour de " + self.order[self.curr] + " !")
                    else:
                        serv.privmsg(self.chan, "Enchère erronée !")
                elif (((message == 'faux') or (message == 'menteur') or (message == 'dudo')) and self.val > 0):
                    self.state = 'FAUX'
                elif (((message == 'exact') or (message == 'calza')) and self.val > 0):
                    self.state = 'EXACT'
                elif re.match (r'[0-9]+ [0-9]', message):
                    serv.privmsg(self.chan, "Crétin.")
            else:
                if (re.match (r'[1-9][0-9]* [1-6]', message) or (message == 'exact') or (message == 'menteur') or (message == 'dudo') or (message == 'faux') or (message == 'calza')):
                    serv.privmsg(self.chan, author + " : ce n'est pas ton tour, mais celui de " + str(self.order[self.curr]) + " !")


        if self.state == 'FAUX':
            somme = self.verif(serv)

            if (self.nb <= somme):
                serv.privmsg(self.chan, "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était correcte ! " + author + " perd un dé !")
            else:
                self.curr = (self.curr+len(self.players)-1)%(len(self.players))
                serv.privmsg(self.chan, "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était fausse ! " + self.order[self.curr] + " perd un dé !")
            self.players[self.order[self.curr]] = self.players[self.order[self.curr]][1:]

            self.nouv_tirage(serv)


        if self.state == 'EXACT':
            somme = self.verif(serv)

            if (self.nb == somme):
                if (len(self.players) > 2):
                    serv.privmsg(self.chan, "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était exacte ! " + author + " gagne un dé !")
                    if len(self.players[author]) < 5:
                        (self.players[author]).append(1)

                else:
                    self.curr = (self.curr+len(self.players)-1)%(len(self.players))
                    serv.privmsg(self.chan, "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était exacte ! " + self.order[self.curr] + " perd un dé !")
                    self.players[self.order[self.curr]] = self.players[self.order[self.curr]][1:]
            else:
                serv.privmsg(self.chan, "Avec " + str(somme) + " " + str(self.val) + ", l'enchère était inexacte ! " + author + " perd un dé !")
                self.players[self.order[self.curr]] = self.players[self.order[self.curr]][1:]

            self.nouv_tirage(serv)


if __name__ == "__main__":
    PeruBot().start()
