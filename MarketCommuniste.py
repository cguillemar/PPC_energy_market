from multiprocessing import Process, Value, Array, Pool, Condition,Semaphore,Pipe
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
        #instanciation pipes avec evenementExt process fils
        parent_conn,child_conn = Pipe()
        pEvenementExt=Process(target=evenementExt,args=(child_conn,))
        pEvenementExt.start()
        while self.monJour.value != 365:
            parent_conn.send(self.monJour.value)
            dayEvent=parent_conn.recv();
            print(dayEvent)
            nrj=0

            # calcul du nouveau prix pour le jour suivant
            # self.vPrix[self.monJour.value+1]=0.5

            #print("nouveau prix", self.vPrix[self.monJour.value + 1])
            #print("nous sommes jour", self.monJour.value)
            while Marche.__test__(self) != True:
                while self.tabMarche.empty()==False:
                    indice, valeur = self.tabMarche.get()
                    #print(indice,valeur,"jour",self.monJour.value)
                    nrj=nrj+valeur
                    threadAchatMarche = threading.Thread(target=Marche.__achat_marche__, args=(self, indice, valeur))
                    threadAchatMarche.start()
                    threadAchatMarche.join()
                # maj du jour apres avoir verifie que les 10 process maisons ont finie leur tour

            self.vPrix[self.monJour.value + 1] = 0.99 * self.vPrix[self.monJour.value] + Marche.prixCapitaliste(nrj)+dayEvent
            self.monJour.value += 1
            #print("marche",self.monJour.value)
            self.synCondition.acquire()
            for i in range(10):
                self.flagFinishTurn[i] = False
            self.synCondition.notify_all()
            self.synCondition.release()
            self.suiviMaison[self.monJour.value] = self.portefeuille[-1]
        pEvenementExt.terminate()

    def __test__(self):
        for i in range(10):
           # print("Marche",self.flagFinishTurn[:],"jour",self.monJour.value)
            if self.flagFinishTurn[i] == False:
                return False
        return True

    # Thread qui fait le lien avec les maisons
    def __achat_marche__(self, i, valeur):
        # possible no need for lock : its a shared array memory (already implemented?
        self.portefeuille[i] += valeur * self.vPrix[self.monJour.value]

        #print(ancienneVal - valeur * self.vPrix[self.monJour.value],"ce qu on a fait",self.portefeuille[i])

        # print("portefeuille",i,"montant",self.portefeuille[i])

    def prixCommuniste(val):
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

    def prixCapitaliste(val):
        if val < 0:
            a = - 0.02

        if val >= 0 :
            a= 0.04

        return (a)


class Maison(Process):

    # __init__: constructeur, initialise tout les parametres
    def __init__(self, numMaison, tabProduction, tabMarche, listTemp,flagFinishTurn, monJour,
                 synCondition,etatSimulation,lockProduction):
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
        self.etatSimulation=etatSimulation
        self.lockProduction=lockProduction

    # run definie ce que fait le process
    def run(self):
        # print("creation maison",self.numMaison)
        # condition pour changement de jour quand marche a maj monJour

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
            if self.etatSimulation==0: #on entre dans le mode de gestion communiste
                if self.production > self.consommation:
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()
                    threadDonnerMaison.join()
                else:

                    threadAcheter = threading.Thread(target=Maison.__acheterCommuniste__, args=(self,))
                    threadAcheter.start()
                    threadAcheter.join()

            else: #on entre dans le mode de gestion capitaliste
                threadEchangeMarche=threading.Thread(target=Maison.__echangeMarche__,args=(self,))
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
        coefmaison = random.randint(10, 50)
        self.production = (1 - taux) * 100 + coefmaison
        self.consommation = taux * 100 + coefmaison
        # print("maison",self.numMaison,"produit",self.production,"consomme",self.consommation)

    def __donnerMaison__(self):
        with self.lockProduction:
            if self.tabProduction.empty()==False:
                cagnotteProdMaisons=self.tabProduction.get()
                cagnotteProdMaisons+=(self.production-self.consommation)
                self.tabProduction.put(cagnotteProdMaisons)
            else:
                self.tabProduction.put(self.production-self.consommation)

    # thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheterCommuniste__(self):

        if self.tabProduction.empty() == False:
            with self.lockProduction:
                cagnotteProdMaisons=self.tabProduction.get()
                if cagnotteProdMaisons >= (self.consommation-self.production):
                    cagnotteProdMaisons-=(self.consommation-self.production)
                    self.tabProduction.put(cagnotteProdMaisons)
                    self.production=self.consommation
                else:
                    self.production+=cagnotteProdMaisons
                    self.tabProduction.put(0)
        if self.production<self.consommation:
            tupleSend = (self.numMaison, self.production-self.consommation)
            self.tabMarche.put(tupleSend)

            # print("apres marche","produit",self.production,"consomme",self.consommation)
    def __echangeMarche__(self):
        #marche met a jour le portefeuille
        tupleSend = (self.numMaison, self.production-self.consommation)
        self.tabMarche.put(tupleSend)

def evenementExt(child_conn):
    #print("je suis un evenementExt")
    listEvenements=[0]*250+[random.uniform(0,0.04)]*50+[random.uniform(-0.02,0)]*50
    monJour=child_conn.recv();
    while monJour!=365:
        #generation aleatoire d un bonus ou d un malus
        randomValue=random.randint(0,1000)
        if randomValue<5:
            #evenement extraordinaire: croissance exceptionnelle ou crash boursier
            child_conn.send(-1+random.randint(0,1)*2)
        elif randomValue<900 and randomValue>100:
            #evenement extraordinaire: croissance exceptionnelle
            child_conn.send(0)
        else:
            child_conn.send(random.uniform(-0.02,0.02))
        monJour=child_conn.recv();


if __name__ == "__main__":
    etatSimulation=0 #0 vaut communiste 1 vaut capitaliste
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
    lockProduction=threading.Lock()
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
        maison = Maison(numMaison, tabProduction, tabMarche, listTemp,flagFinishTurn, monJour, synCondition,etatSimulation,lockProduction)
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
