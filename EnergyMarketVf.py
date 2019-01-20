from multiprocessing import Process, Value, Array, Pool, Condition, Semaphore, Pipe,Lock
from multiprocessing import Queue
import threading
import random
import time
import matplotlib.pyplot as plt
import signal
import os


def meteo(listTemp, N):
    # Entrée : N nombre de jours à étudier

    # Liste des températures
    temp = [3.3, 4.2, 7.8, 10.8, 14.3, 17.5, 19.4, 19.1, 16.4, 11.6, 7.2, 4.2, 3.1,
            4.5]  # Temperatures moyennes sur 1 année de janvier à décembre
    # temp=[10.1,11,13,17.4,19,20,25,28,30,,22,21,18,15]
    # temp = [7.8, 10.8, 14.3, 17.5, 19.4, 19.1, 16.4, 11.6, 7.2,4.2,3.3, 4.2]
    tempf = []
    for i in range(len(temp) - 1):
        for j in range(29):
            tempf.append(round(random.uniform(temp[i], temp[i + 1]), 1))  # Temperatures pour 300 jours environ
    for i in range(N):
        listTemp[i] = tempf[i]


class Marche(Process):
    def __init__(self, vPrix, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition, suiviMaison,
                 tabProduction, nMaison, suiviMaison2):
        super().__init__()
        self.vPrix = vPrix
        self.tabMarche = tabMarche
        self.listTemp = listTemp
        self.portefeuille = portefeuille
        self.monJour = monJour
        self.synCondition = synCondition
        self.flagFinishTurn = flagFinishTurn
        self.suiviMaison = suiviMaison
        self.suiviMaison2 = suiviMaison2
        self.tabProduction = tabProduction
        self.nMaison = nMaison

    def run(self):
        print("--------- Creation marche ---------")

        parent_conn, child_conn = Pipe()
        pEvenementExt = Process(target=evenementExt, args=(child_conn,))
        pEvenementExt.start()

        while self.monJour.value != 365:

            parent_conn.send(self.monJour.value)
            dayEvent = parent_conn.recv();

            nrj = 0

            # calcul du nouveau prix pour le jour suivant
            # self.vPrix[self.monJour.value+1]=0.5

            # print("nouveau prix", self.vPrix[self.monJour.value + 1])
            # print("nous sommes jour", self.monJour.value)
            while Marche.__test__(self, self.nMaison) != True:
                while self.tabMarche.empty() == False:
                    # print(self.monJour.value)
                    indice, valeur = self.tabMarche.get()

                    # print(indice,valeur,"jour",self.monJour.value)
                    nrj = nrj + valeur
                    threadAchatMarche = threading.Thread(target=Marche.__achat_marche__, args=(self, indice, valeur))
                    threadAchatMarche.start()
                    threadAchatMarche.join()
                # maj du jour apres avoir verifie que les 10 process maisons ont finie leur tour

            self.vPrix[self.monJour.value + 1] = (0.99 * self.vPrix[self.monJour.value] + Marche.prix(nrj) + dayEvent)

            fichier = open("Courbes.txt", "a")
            fichier.write(str(self.vPrix[self.monJour.value] + 3.5) + "," + str(self.monJour.value) + "\n")
            fichier.close()

            # time.sleep(0.05)

            fichier = open("nrj.txt", "a")
            fichier.write("Jour : " + str(self.monJour.value + 1) + "\n")
            fichier.close()

            self.monJour.value += 1

            if self.tabProduction.empty() == False:
                x = self.tabProduction.get()

            # print("marche",self.monJour.value)
            self.synCondition.acquire()
            for i in range(self.nMaison):
                self.flagFinishTurn[i] = False
            self.synCondition.notify_all()
            self.synCondition.release()

            self.suiviMaison[self.monJour.value] = self.portefeuille[-1] / 100
            self.suiviMaison2[self.monJour.value] = self.portefeuille[0] / 100

        pEvenementExt.terminate()
        self.tabMarche.close()
        self.tabMarche.join_thread()
        self.tabProduction.close()
        self.tabProduction.join_thread()

    def __test__(self, n):
        for i in range(n):
            # print("Marche",self.flagFinishTurn[:],"jour",self.monJour.value)
            if self.flagFinishTurn[i] == False:
                return False
        return True

    # Thread qui fait le lien avec les maisons
    def __achat_marche__(self, i, valeur):
        # possible no need for lock : its a shared array memory (already implemented?
        self.portefeuille[i] += valeur * (self.vPrix[self.monJour.value] + 3.5)

        # print(ancienneVal - valeur * self.vPrix[self.monJour.value],"ce qu on a fait",self.portefeuille[i])

        # print("portefeuille",i,"montant",self.portefeuille[i])

    def prix(val):

        if val < 0:
            return (0.04)

        else:
            return (-0.03)

        """a= - 0.001
        for i in range(0,100000,20):
            if val < i+20 and val >= i:
                return(a)
            a= a - 0.001
        b = 0.05
        for i in range(-100000,0,20):
            if val > i and val <= i+20:
                return(b)
            b=b - 0.001"""


class Maison(Process):

    # __init__: constructeur, initialise tout les parametres
    def __init__(self, numMaison, tabProduction, tabMarche, listTemp, flagFinishTurn, monJour,
                 synCondition, etatSimulation, lockProduction):
        # penser a mettre le super sinon ca marche pas
        super().__init__()
        # valeurs arbitraires
        self.consommation = 100
        self.production = 0
        # on recupere le numero du process maison en cours
        self.numMaison = numMaison
        # queue tabProduction
        self.tabProduction = tabProduction

        self.listTemp = listTemp
        # Portefeuilles maisons
        self.portefeuille = portefeuille
        self.tabMarche = tabMarche

        self.monJour = monJour
        self.synCondition = synCondition
        self.flagFinishTurn = flagFinishTurn
        self.autorisationAchatMaison = 0
        self.etatSimulation = etatSimulation
        self.lockProduction = lockProduction

    # run definie ce que fait le process
    def run(self):
        # print("creation maison",self.numMaison)
        # condition pour changement de jour quand marche a maj monJour
        # n=0
        # print("premier jour",self.monJour.value)
        while self.monJour.value != 365:
            # print("Maison",self.flagFinishTurn[:],"num", self.numMaison)
            # n+=1
            # print(self.numMaison,"refait une boucle nombre",n)
            # self.flagFinishTurn[self.numMaison] = False
            # on attend que tout les process maisons soient synch
            # creation d'un thread (un thread par maison) qui va produire
            threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
            threadProduire.start()
            threadProduire.join()

            if self.etatSimulation == 0:  # on entre dans le mode de gestion communiste
                if self.production > self.consommation:
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()
                    threadDonnerMaison.join()
                else:

                    threadAcheter = threading.Thread(target=Maison.__acheterCommuniste__, args=(self,))
                    threadAcheter.start()
                    threadAcheter.join()

            else:  # on entre dans le mode de gestion capitaliste
                threadEchangeMarche = threading.Thread(target=Maison.__echangeMarche__, args=(self,))
                threadEchangeMarche.start()
                threadEchangeMarche.join()

            # avertie qu'il a fini son jour
            self.flagFinishTurn[self.numMaison] = True
            self.synCondition.acquire()
            self.synCondition.wait()
            self.synCondition.release()

    # thread produire de l'energie
    def __produire__(self):
        taux = abs(self.listTemp[self.monJour.value] - 20) / 20  # Nrj max pour 20°
        coefproduction = random.randint(10, 80)
        coefconso = random.randint(10, 80)

        self.production = (1 - taux) * 100 + coefproduction
        self.consommation = taux * 100 + coefconso
        # print("maison",self.numMaison,"produit",self.production,"consomme",self.consommation)

    def __donnerMaison__(self):

        with self.lockProduction:
            if self.tabProduction.empty() == False:
                cagnotteProdMaisons = self.tabProduction.get()
                # print("cagnotteProdMaisons",cagnotteProdMaisons)
                cagnotteProdMaisons += (self.production - self.consommation)
                self.tabProduction.put(cagnotteProdMaisons)

                fichier = open("nrj.txt", "a")
                fichier.write(
                    "Maison " + str(self.numMaison) + " donne " + str(self.production - self.consommation) + " kW" + "\n")
                fichier.close()

            else:
                self.tabProduction.put(self.production - self.consommation)

                fichier = open("nrj.txt", "a")
                fichier.write(
                    "Maison " + str(self.numMaison) + " donne " + str(self.production - self.consommation) + " kW" + "\n")
                fichier.close()

    # thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheterCommuniste__(self):

        # print(self.numMaison,self.production,self.consommation)

        if self.tabProduction.empty() == False:
            with self.lockProduction:
                cagnotteProdMaisons = self.tabProduction.get()
                if cagnotteProdMaisons >= (self.consommation - self.production):
                    cagnotteProdMaisons -= (self.consommation - self.production)
                    self.tabProduction.put(cagnotteProdMaisons)

                    fichier = open("nrj.txt", "a")
                    fichier.write("Maison " + str(self.numMaison) + " achète " + str(
                        self.production - self.consommation) + " kW" + "\n")
                    fichier.close()

                    self.production = self.consommation

                else:
                    fichier = open("nrj.txt", "a")
                    fichier.write("Maison " + str(self.numMaison) + " achète " + str(cagnotteProdMaisons) + " kW" + "\n")
                    fichier.close()

                    self.production += cagnotteProdMaisons
                    self.tabProduction.put(0)

        if self.production < self.consommation:
            fichier = open("nrj.txt", "a")
            fichier.write("Maison " + str(self.numMaison) + " achète au marché " + str(
                self.production - self.consommation) + " kW" + "\n")
            fichier.close()

            tupleSend = (self.numMaison, self.production - self.consommation)
            self.tabMarche.put(tupleSend)

            # print("apres marche","produit",self.production,"consomme",self.consommation)

    def __echangeMarche__(self):
        # marche met a jour le portefeuille
        fichier = open("nrj.txt", "a")
        fichier.write("Maison " + str(self.numMaison) + " échange au marché " + str(
            self.production - self.consommation) + " kW" + "\n")
        fichier.close()

        tupleSend = (self.numMaison, self.production - self.consommation)
        self.tabMarche.put(tupleSend)


def evenementExt(child_conn):
    # print("je suis un evenementExt")

    monJour = child_conn.recv();
    while monJour != 365:
        # generation aleatoire d un bonus ou d un malus
        randomValue = random.randint(0, 1000)
        if randomValue < 5:
            # evenement extraordinaire: croissance exceptionnelle ou crash boursier
            child_conn.send(-1 + random.randint(0, 1) * 2)
        elif randomValue < 900 and randomValue > 100:
            # evenement extraordinaire: croissance exceptionnelle
            child_conn.send(0)
        else:
            child_conn.send(random.uniform(-0.02, 0.02))
        monJour = child_conn.recv();


if __name__ == "__main__":

    print(" !! Ne pas oublier de créer les fichiers textes : Courbes.txt nrj.txt")
    print(" ### ------------ SIMULATION --------------- ###")

    etatSimulation = int(input(
        "Quel mode de simulation voulez vous faire ? (0 : communiste, 1: capitaliste) "))  # 0 vaut communiste 1 vaut capitaliste
    N = 366  # Nombre de jours de la simulation
    listTemp = Array('d', range(N))  # Liste des températures
    nMaison = int(input("Quel nombre de maisons voulez vous pour la simulation ? "))  # nombre de maisons
    suiviMaison = Array('d', range(N))
    suiviMaison2 = Array('d', range(N))

    # Méteo (process qui genere 300 temp dans memoire partagee listTemp
    pMeteo = Process(target=meteo, args=(listTemp, N))
    pMeteo.start()

    monJour = Value('i', 0)
    synCondition = Condition()

    vPrix = Array('d', range(N))  # prix gere par marche
    vPrix[0] = 0.8  # prix initial
    flagFinishTurn = Array('i', [
        False] * nMaison)  # se met a True chaque jour quand maison a finie ses echanges pour prevenir marche

    tabProduction = Queue()
    lockProduction = Lock()
    tabMarche = Queue()
    portefeuille = Array('d', [0] * nMaison)  # creation d'un portefeuille pour les 10 maisons process

    # On lance le marché
    pMarche = Marche(vPrix, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition, suiviMaison,
                     tabProduction, nMaison, suiviMaison2)
    pMarche.start()
    # On lance les process maisons

    pMaison = []
    for numMaison in range(nMaison):
        maison = Maison(numMaison, tabProduction, tabMarche, listTemp, flagFinishTurn, monJour, synCondition,
                        etatSimulation, lockProduction)
        maison.start()
        pMaison.append(maison)

    pMarche.join()
    for j in pMaison:
        j.terminate()

    pMeteo.join()

    P = []

    if monJour.value == 365:
        # plot graphe
        suiviMaison[0] = 0
        suiviMaison2[0] = 0

        M = []
        for i in range(N):
            M.append(i + 1)

        for p in vPrix[:]:
            P.append(p + 3.5)

        fig = plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(M, P)
        plt.title("Evolution du prix de l'énergie en fonction du jour")
        plt.xlabel('jours')
        plt.ylabel('Prix en €')

        plt.subplot(2, 2, 3)
        plt.title("Evolution de la températurature en fonction du jour")
        plt.plot(M, listTemp[:])
        plt.xlabel('jours')
        plt.ylabel('Température en °')

        plt.subplot(2, 2, 4)
        plt.title("Evolution du portefeuille de maison 1 en fonction du jour")
        plt.plot(M, suiviMaison, label="Maison a")
        plt.plot(M, suiviMaison2, label="Maison b")
        plt.xlabel('jours')
        plt.legend()

        plt.ylabel('portefeuille en €')
plt.show()
