from multiprocessing import Process, Value, Array, Pool, Condition,Semaphore
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
    temp = [3.3, 4.2, 7.8, 10.8, 14.3, 17.5, 19.4, 19.1, 16.4, 11.6, 7.2,
        4.2,3.1,4.5]  # Temperatures moyennes sur 1 année de janvier à décembre
    #temp = [7.8, 10.8, 14.3, 17.5, 19.4, 19.1, 16.4, 11.6, 7.2,4.2,3.3, 4.2]
    tempf = []
    for i in range(len(temp) - 1):
        for j in range(29):
            tempf.append(round(random.uniform(temp[i], temp[i + 1]), 1))  # Temperatures pour 300 jours environ
    for i in range(N):
        listTemp[i] = tempf[i]


class Marche(Process):
    def __init__(self, vPrix, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition,suiviMaison):
        super().__init__()
        self.vPrix = vPrix
        self.tabMarche = tabMarche
        self.listTemp = listTemp
        self.portefeuille = portefeuille
        self.monJour = monJour
        self.synCondition = synCondition
        self.flagFinishTurn = flagFinishTurn
        self.suiviMaison = suiviMaison

    def run(self):
        print("creation marche")
        while self.monJour.value != 365:

            nrj=0

            # calcul du nouveau prix pour le jour suivant
            # self.vPrix[self.monJour.value+1]=0.5
            
            #print("nouveau prix", self.vPrix[self.monJour.value + 1])
            #print("nous sommes jour", self.monJour.value)
            while Marche.__test__(self) != True:

                if self.tabMarche.empty() == False:
                    indice, valeur = self.tabMarche.get()
                    nrj=nrj+valeur
                    #print(indice,valeur)
                    threadAchatMarche = threading.Thread(target=Marche.__achat_marche__, args=(self, indice, valeur))
                    threadAchatMarche.start()
                    threadAchatMarche.join()
            # maj du jour apres avoir verifie que les 10 process maisons ont finie leur tour
            
            self.vPrix[self.monJour.value + 1] = (0.99 * self.vPrix[self.monJour.value] + Marche.prix(nrj))
            self.monJour.value += 1
            #print("marche",self.monJour.value)
            self.synCondition.acquire()
            for i in range(10):
                self.flagFinishTurn[i] = False
            self.synCondition.notify_all()
            self.synCondition.release()
            while self.tabMarche.empty()==False:
                val=self.tabMarche.get()
            print(self.portefeuille[:])

            
            self.suiviMaison[self.monJour.value] = self.portefeuille[-1]

    def __test__(self):
        for i in range(10):
           # print("Marche",self.flagFinishTurn[:],"jour",self.monJour.value)
            if self.flagFinishTurn[i] == False:
                return False
        return True

    # Thread qui fait le lien avec les maisons
    def __achat_marche__(self, i, valeur):
        # possible no need for lock : its a shared array memory (already implemented?
        ancienneVal=self.portefeuille[i]
        self.portefeuille[i] = ancienneVal - valeur * abs(self.vPrix[self.monJour.value])

        #print(ancienneVal - valeur * self.vPrix[self.monJour.value],"ce qu on a fait",self.portefeuille[i])

        # print("portefeuille",i,"montant",self.portefeuille[i])

    def prix(val):
        print(val)
        
        if val > 160:
            a = 0.07

        if val == 0:
            a= -0.03

        if val > 100 and val <= 160:
            a= 0.06

        if val > 50 and val <= 100:
            a= 0.04

        if val > 0 and val <= 50:

            a=-0.02

        return (a)


class Maison(Process):

    # __init__: constructeur, initialise tout les parametres
    def __init__(self, numMaison, tabProduction, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour,
                 synCondition):
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
        self.flagFinishTurn=flagFinishTurn
        self.autorisationAchatMaison=0

    # run definie ce que fait le process
    def run(self):
        # print("creation maison",self.numMaison)
        # condition pour changement de jour quand marche a maj monJour
        # n=0
        lockProduction=threading.Lock()
        while self.monJour.value != 365:
            #print("Maison",self.flagFinishTurn[:],"num", self.numMaison)
            # n+=1
            # print(self.numMaison,"refait une boucle nombre",n)
            #self.flagFinishTurn[self.numMaison] = False
            # on attend que tout les process maisons soient synch
            # creation d'un thread (un thread par maison) qui va produire
            threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
            threadProduire.start()
            threadProduire.join()

            # boucle while pour que le process ne gere pas un autre jour tant qu'on a pas l equilibre prod/conso
            while self.production != self.consommation:
                # condition pour donner
                if self.production > self.consommation:
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,lockProduction))
                    threadDonnerMaison.start()
                    threadDonnerMaison.join()
                    self.production = self.consommation
                else:
                    threadAcheter = threading.Thread(target=Maison.__acheter__, args=(self,lockProduction))
                    threadAcheter.start()
                    threadAcheter.join()
            # avertie qu'il a fini son jour
            #print("maison,num",self.numMaison,"a finie")
            self.flagFinishTurn[self.numMaison] = True
            self.synCondition.acquire()
            self.synCondition.wait()

            self.synCondition.release()


    # thread produire de l'energie
    def __produire__(self):
        taux = abs(self.listTemp[self.monJour.value] - 20) / 20  # Nrj max pour 20°
        coefmaison = random.randint(10, 50)
        self.production = (1 - taux) * 100 + coefmaison
        self.consommation = taux * 100 + coefmaison
        # print("maison",self.numMaison,"produit",self.production,"consomme",self.consommation)

    def __donnerMaison__(self,lockProduction):

        #print("on donne enfin","prod",self.production,"conso",self.consommation,"jour",self.monJour.value)
        # verifie si la queue est pleine
        if self.tabProduction.full() == False:
            # donne surplus de production uniquement
            with lockProduction:
                self.tabProduction.put(self.production - self.consommation)
            autorisationAchatMaison=1

    # thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self,lockProduction):
        # verifie si queue vide
        if self.tabProduction.empty() == False and self.autorisationAchatMaison==0:
            #print(self.numMaison,"on recup des maisons avant", "prod", self.production, "conso", self.consommation, "jour", self.monJour.value)
            # on augmente valeur conso en fonction de la valeur de production piochee
            with lockProduction:
                self.production += self.tabProduction.get()
            #print(self.numMaison,"on recup des maisons apres", "prod", self.production, "conso", self.consommation, "jour",self.monJour.value)
            self.autorisationAchatMaison=1

        else:
           # print(self.numMaison,"on recup du marche", "prod", self.production, "conso", self.consommation, "jour",self.monJour.value)
            # cas ou pas de prod dispo entre les maisons on achete a marche qui fait l equilibre
            with lockProduction:
                tupleSend = (self.numMaison, self.consommation - self.production)
            self.tabMarche.put(tupleSend)
            self.production = self.consommation
            # print("apres marche","produit",self.production,"consomme",self.consommation)


if __name__ == "__main__":

    N = 366  # Nombre de jours de la simulation
    listTemp = Array('d', range(N))  # Liste des températures

    suiviMaison=Array('d',range(N))

    # Méteo (process qui genere 300 temp dans memoire partagee listTemp
    pMeteo = Process(target=meteo, args=(listTemp, N))
    pMeteo.start()
    pMeteo.join()
    monJour = Value('i', 0)
    synCondition = Condition()

    vPrix = Array('d', range(N))  # prix gere par marche
    vPrix[0] = 0.8  # prix initial
    flagFinishTurn = Array('i', [False, False, False, False, False, False, False, False, False,
                                 False])  # se met a True chaque jour quand maison a finie ses echanges pour prevenir marche
    tabProduction = Queue()
    tabMarche = Queue()
    portefeuille = Array('d', [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000,
                               5000])  # creation d'un portefeuille pour les 10 maisons process

    # On lance le marché
    pMarche = Marche(vPrix, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition,suiviMaison)
    pMarche.start()
    # On lance les process maisons
    nMaison = 10  # nombre de maisons
    pMaison=[]
    for numMaison in range(nMaison):
        maison = Maison(numMaison, tabProduction, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition)
        maison.start()
        pMaison.append(maison)


    pMarche.join()
    for j in pMaison:
        j.terminate()

    P=[]

    if monJour.value == 365:
        # plot graphe
        suiviMaison[0]=5000
        M = []
        for i in range(N):
            M.append(i + 1)

        for p in vPrix[:] :
            P.append(p + 2.5)

        fig =plt.figure()
        plt.subplot(2,1,1)
        plt.plot(M, P,label="Mode Communiste")
        plt.title("Evolution du prix de l'énergie en fonction du jour")
        plt.xlabel('jours')
        plt.ylabel('Prix en €')
        plt.legend()

        plt.subplot(2,2,3)
        plt.title("Evolution de la températurature en fonction du jour")
        plt.plot(M,listTemp[:])
        plt.xlabel('jours')
        plt.ylabel('Température en °')

        plt.subplot(2,2,4)
        plt.title("Evolution du portefeuille de maison 1 en fonction du jour")
        plt.plot(M,suiviMaison,'+')
        plt.xlabel('jours')

        plt.ylabel('portefeuille en €')

        #plt.ylim(3000,5000)
        
        plt.show()