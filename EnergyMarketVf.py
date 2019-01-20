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

#Process Marche
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
        
        #creation du process evenement exterrieur et communication par pipes
        parent_conn, child_conn = Pipe()
        pEvenementExt = Process(target=evenementExt, args=(child_conn,))
        pEvenementExt.start()
        
        # boucle while pour que la simulation fonctionne sur 366 jours
        while self.monJour.value != 365:
               
            #par pipes: Marche indique a Evenement ext quel jour on est
            parent_conn.send(self.monJour.value)
            
            #dayEvent: valeur aleatoire generee par evenement ext qui va influencer dans la formule du prix
            dayEvent = parent_conn.recv();
            
            #nrj: somme de tout les echanges (achats,ventes) entre Maisons et Marche
            nrj = 0
            
            #boucle while: fonctionne tant que tout les flags maisons ne sont pas True
            while Marche.__test__(self, self.nMaison) != True:
                
                while self.tabMarche.empty() == False:
                    #recupere et gere les donnees de tabMarche
                    indice, valeur = self.tabMarche.get()
                    nrj = nrj + valeur
                    threadAchatMarche = threading.Thread(target=Marche.__achat_marche__, args=(self, indice, valeur))
                    threadAchatMarche.start()
                    threadAchatMarche.join()
            #fin du jour:
            #maj du prix
            self.vPrix[self.monJour.value + 1] = (0.99 * self.vPrix[self.monJour.value] + Marche.prix(nrj) + dayEvent)
            
            #ecriture de la valeur du prix et du jour en cours dans Courbes.txt
            fichier = open("Courbes.txt", "a")
            fichier.write(str(self.vPrix[self.monJour.value] + 3.5) + "," + str(self.monJour.value) + "\n")
            fichier.close()
            
            #ecriture du jour dans nrj.txt
            fichier = open("nrj.txt", "a")
            fichier.write("Jour : " + str(self.monJour.value + 1) + "\n")
            fichier.close()
            
            #maj du jour 
            self.monJour.value += 1
            
            #on vide tabProduction
            if self.tabProduction.empty() == False:
                x = self.tabProduction.get()
            
            self.synCondition.acquire() #comme un semaphore (pas de limite de taille)
            
            #on remet tout les flags maisons a False
            for i in range(self.nMaison):
                self.flagFinishTurn[i] = False
            #on libere tout les process maisons qui etaient en attente (synCondition.wait())
            self.synCondition.notify_all()
            self.synCondition.release()#comme un semaphore (pas de limite de taille)

            self.suiviMaison[self.monJour.value] = self.portefeuille[-1] / 100
            self.suiviMaison2[self.monJour.value] = self.portefeuille[0] / 100
        
        #fin de la simulation pour Marche
        pEvenementExt.terminate() #on ferme le process fils evenement ext
        #on ferme les Queues
        self.tabMarche.close()
        self.tabMarche.join_thread()
        self.tabProduction.close()
        self.tabProduction.join_thread()
    
    #__test__: retourne vrai si toutes le flags du tableau partagee flagFinishTurn sont True
    def __test__(self, n):
        for i in range(n):
            if self.flagFinishTurn[i] == False:
                return False
        return True

    # Thread qui fait le lien avec les maisons
    def __achat_marche__(self, i, valeur):
        #maj du portefeuille de la maison i: valeur peut etre positif (vend) ou negatif(achete)
        self.portefeuille[i] += valeur * (self.vPrix[self.monJour.value] + 3.5)

    #prix en fonction de l offre et de la demande en energie (ensemble des echanges d energie avec marche en une journee)
    def prix(val):
        
        if val < 0:
            return (0.04)

        else:
            return (-0.03)

#Process Maison
class Maison(Process):

    # __init__: initialise tout les parametres
    def __init__(self, numMaison, tabProduction, tabMarche, listTemp, flagFinishTurn, monJour,
                 synCondition, etatSimulation, lockProduction):
        super().__init__()
        self.consommation = 100
        self.production = 0
        #numMaison: numero du process maison
        self.numMaison = numMaison
        self.tabProduction = tabProduction
        self.listTemp = listTemp
        self.portefeuille = portefeuille
        self.tabMarche = tabMarche
        self.monJour = monJour
        self.synCondition = synCondition
        self.flagFinishTurn = flagFinishTurn
        self.etatSimulation = etatSimulation
        self.lockProduction = lockProduction

    # run: definie ce que fait le process
    def run(self):
        
        # boucle while pour que la simulation fonctionne sur 366 jours
        while self.monJour.value != 365:
            # creation d'un thread qui va generee une valeur de production et une valeur de consommation
            threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
            threadProduire.start()
            threadProduire.join()

            if self.etatSimulation == 0:  # on entre dans le mode de gestion communiste(0)
                if self.production > self.consommation:
                    #on produit plus que ce que l'on consomme: on donne dans tabProduction notre surplus
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()
                    threadDonnerMaison.join()
                else:
                    #on a consomme plus que ce que l'on a produit
                    #on recupere aupres de la cagnotte dans tabProduction ou on achete au marche
                    threadAcheter = threading.Thread(target=Maison.__acheterCommuniste__, args=(self,))
                    threadAcheter.start()
                    threadAcheter.join()

            else:  # on entre dans le mode de gestion capitaliste(1)
                threadEchangeMarche = threading.Thread(target=Maison.__echangeMarche__, args=(self,))
                threadEchangeMarche.start()
                threadEchangeMarche.join()

            # fin des actions du jour pour ce process maison
            self.flagFinishTurn[self.numMaison] = True #avertie a marche qu'il a finit son jour
            self.synCondition.acquire() #comme un semaphore (pas de limite de taille)
            self.synCondition.wait() #se met en attente de self.synCondition.notify()
            self.synCondition.release() #libere son verroue de semaphore

    # thread produire de l'energie
    def __produire__(self):
        taux = abs(self.listTemp[self.monJour.value] - 20) / 20  # Nrj max pour 20°
        coefproduction = random.randint(10, 80)
        coefconso = random.randint(10, 80)
        self.production = (1 - taux) * 100 + coefproduction
        self.consommation = taux * 100 + coefconso

    def __donnerMaison__(self):
        #Mutex lockProduction (but): eviter le cas ou un process recupere la valeur de la cagnotte
        #et avant de remettre cette valeur, un autre la voyant vide y ajoute son surplus
        with self.lockProduction:
            if self.tabProduction.empty() == False:
                #on prend la valeur dans tabProduction et la stocke dans variable cagnotteProdMaisons
                cagnotteProdMaisons = self.tabProduction.get()
                cagnotteProdMaisons += (self.production - self.consommation)
                #on met dans tabProduction la valeur modifiee avec le surplus
                self.tabProduction.put(cagnotteProdMaisons)
               
                #ecriture dans fichier nrj.txt
                fichier = open("nrj.txt", "a")
                fichier.write(
                    "Maison " + str(self.numMaison) + " donne " + str(self.production - self.consommation) + " kW" + "\n")
                fichier.close()

            else:
                #on met directement dans tabProduction le surplus de production
                self.tabProduction.put(self.production - self.consommation)
                
                #ecriture dans fichier nrj.txt
                fichier = open("nrj.txt", "a")
                fichier.write(
                    "Maison " + str(self.numMaison) + " donne " + str(self.production - self.consommation) + " kW" + "\n")
                fichier.close()

    # thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheterCommuniste__(self):
        
        if self.tabProduction.empty() == False: #on peut prendre dans la cagnotte commune tabProduction
            with self.lockProduction:
                cagnotteProdMaisons = self.tabProduction.get()
                if cagnotteProdMaisons >= (self.consommation - self.production):
                    #cas ou la cagnotte contient plus que ce dont on a besoin
                    cagnotteProdMaisons -= (self.consommation - self.production)
                    self.tabProduction.put(cagnotteProdMaisons)

                    fichier = open("nrj.txt", "a")
                    fichier.write("Maison " + str(self.numMaison) + " achète " + str(
                        self.production - self.consommation) + " kW" + "\n")
                    fichier.close()
                    #maj de production pour eviter de rentrer dans la prochaine instruction if
                    self.production = self.consommation

                else:
                    #cas ou la cagnotte contient moins que ce dont on a besoin: on prend tout ce qu'il y a et maj de production
                    fichier = open("nrj.txt", "a")
                    fichier.write("Maison " + str(self.numMaison) + " achète " + str(cagnotteProdMaisons) + " kW" + "\n")
                    fichier.close()

                    self.production += cagnotteProdMaisons
                    self.tabProduction.put(0)

        if self.production < self.consommation:#achat au marche
            #tabProduction etait vide ou la cagnotte n a pas suffit pour combler le deficit
            
            fichier = open("nrj.txt", "a")
            fichier.write("Maison " + str(self.numMaison) + " achète au marché " + str(
                self.production - self.consommation) + " kW" + "\n")
            fichier.close()
            
            #on envoie dans tabMarche (queue) a destination de marche notre id (numMaison) et l energie qu il nous faut
            tupleSend = (self.numMaison, self.production - self.consommation)
            self.tabMarche.put(tupleSend)

            

    def __echangeMarche__(self):
        # marche met a jour le portefeuille
        fichier = open("nrj.txt", "a")
        fichier.write("Maison " + str(self.numMaison) + " échange au marché " + str(
            self.production - self.consommation) + " kW" + "\n")
        fichier.close()
        #si prod>conso on va ganger de l arget sinon la difference est negative=on perdra de l argent
        tupleSend = (self.numMaison, self.production - self.consommation)
        self.tabMarche.put(tupleSend)

#Process Fils evenement exterieur (communique par pipes avec Marche)
def evenementExt(child_conn):
    #monJour: valeur du jour synchronise avec Marche
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


#main programm
if __name__ == "__main__":

    print(" !! Ne pas oublier de créer les fichiers textes : Courbes.txt nrj.txt")
    print(" ### ------------ SIMULATION --------------- ###")
    
     # etatSimulation : 0 vaut communiste 1 vaut capitaliste
    etatSimulation = int(input(
        "Quel mode de simulation voulez vous faire ? (0 : communiste, 1: capitaliste) ")) 
    N = 366  # Nombre de jours de la simulation
    listTemp = Array('d', range(N))  # Liste des températures
    nMaison = int(input("Quel nombre de maisons voulez vous pour la simulation ? "))  # nombre de maisons
    suiviMaison = Array('d', range(N)) 
    suiviMaison2 = Array('d', range(N))

    # Méteo (process qui genere 300 temp dans la memoire partagee listTemp)
    pMeteo = Process(target=meteo, args=(listTemp, N))
    pMeteo.start()
    pMeteo.join()
    
    monJour = Value('i', 0) #variable partagee entre Marche et Maison et qui donne le jour en cours
    
    synCondition = Condition() #semaphore particulier pour synchroniser les maisons avec le marche
    
    vPrix = Array('d', range(N))  #tableau partage: prix gere et mis a jour par marche
    vPrix[0] = 0.8  # prix initial
    
    # flagFinishTurn: drapeau de fin de jour =se met a True chaque jour quand maison a finie ses echanges pour prevenir marche
    flagFinishTurn = Array('i', [False] * nMaison)  
    
    #tabProduction: Queue partagee entre les maisons et qui gere les echanges de surplus de prod entre les maisons (cagnotte commune)
    tabProduction = Queue()
    #lockProduction: Mutex pour gerer l'acces partage a tabProduction entre les maisons
    lockProduction = Lock()
    #tabMarche: Queue partagee entre les maisons et marches pour gere les echanges d energie
    tabMarche = Queue()
    #portefeuille:Tableau partage gere par Marche dans notre simulation 
    #(chaque maison a un portefeuille maj en fonction des echanges avec Marche)
    portefeuille = Array('d', [0] * nMaison)  

    # On lance le marché
    pMarche = Marche(vPrix, tabMarche, listTemp, portefeuille, flagFinishTurn, monJour, synCondition, suiviMaison,
                     tabProduction, nMaison, suiviMaison2)
    pMarche.start()
    
    
    # On lance les process maisons
    pMaison = [] #tableau de process :utilise a la fin de la simulation pour terminer les process maisons 
    for numMaison in range(nMaison):
        maison = Maison(numMaison, tabProduction, tabMarche, listTemp, flagFinishTurn, monJour, synCondition,
                        etatSimulation, lockProduction)
        maison.start()
        pMaison.append(maison)

    #fin de la simulation: on ferme les process pMarche et maison
    pMarche.join()
    for j in pMaison:
        j.terminate()

   

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
