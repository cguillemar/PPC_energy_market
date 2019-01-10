
from multiprocessing import Process, Value, Array, Pool
from multiprocessing import Queue
import threading
from random import *
import time
import matplotlib.pyplot as plt
import signal
import os

def meteo(listTemp,N):
	#Entrée : N nombre de jours à étudier

	#Liste des températures
    temp=[3.3,4.2,7.8,10.8,14.3,17.5,19.4,19.1,16.4,11.6,7.2,4.2]		#Temperatures moyennes sur 1 année de janvier à décembr
    tempf=[]
    for i in range(len(temp)-1):
        for j in range(29):
            tempf.append(round(uniform(temp[i],temp[i+1]),1))	#Temperatures pour 300 jours environ
    for i in range (N):
        listTemp[i]=tempf[i]


class Marche(Process):
    def __init__(self,vPrix,tabMarche,listTemp,portefeuille,flagFinishTurn,monJour):
        super().__init__()
        self.vPrix=vPrix
        self.tabMarche=tabMarche
        self.listTemp=listTemp
        self.portefeuille=portefeuille
        self.flagFinishTurn=flagFinishTurn
        self.monJour=monJour

    def run(self):
        print("creation marche")
        while self.monJour.value!=299:

            #calcul du nouveau prix pour le jour suivant
            self.vPrix[self.monJour.value+1]=(0.99*self.vPrix[self.monJour.value]+Marche.prix(self.listTemp[self.monJour.value]))
            print("nouveau prix",self.vPrix[self.monJour.value+1])
            while Marche.__test__(self)!=True:
                    if self.tabMarche.empty()==False:
                        indice,valeur=self.tabMarche.get()
                        threadAchatMarche=threading.Thread(target=Marche.__achat_marche__,args=(self,indice,valeur))
                        threadAchatMarche.start()
                        threadAchatMarche.join()
            #maj du jour apres avoir verifie que les 10 process maisons ont finie leur tour
            self.monJour.value+=1
            print("nous sommes jour",self.monJour.value)

    def __test__(self):
        for i in range(10):
            if self.flagFinishTurn[i]==False:
                return False
        return True



    #Thread qui fait le lien avec les maisons
    def __achat_marche__(self,i,valeur):
        #possible no need for lock : its a shared array memory (already implemented?
            self.portefeuille[i]=self.portefeuille[i]-valeur*self.vPrix[self.monJour.value]
            print("portefeuille",i,"montant",self.portefeuille[i])



    def prix(val):
        if val < 5 :
            a= 0.5
        if val <10 and val >=5 :
            a=0.4

        if val <15 and val >=10 :
            a=0.3

        if val <20 and val >=15 :
            a=0.3

        if val <25 and val >=20 :
            a=-0.3
            a=-0.4

        if val <35 and val>= 30:
            a=-0.5


        return(a)


class Maison(Process):

    #__init__: constructeur, initialise tout les parametres
    def __init__(self,numMaison,tabProduction,tabMarche,listTemp,portefeuille,flagFinishTurn,monJour):
        #penser a mettre le super sinon ca marche pas
        super().__init__()
        #valeurs arbitraires
        self.consommation=100
        self.production=0
        #on recupere le numero du process maison en cours
        self.numMaison=numMaison
        #queue tabProduction
        self.tabProduction=tabProduction

        self.listTemp=listTemp
        #Portefeuilles maisons
        self.portefeuille=portefeuille
        self.tabMarche=tabMarche
        self.flagFinishTurn=flagFinishTurn
        self.monJour=monJour


    #run definie ce que fait le process
    def run(self):
        print("creation maison",self.numMaison)
        while self.monJour.value!=299:
            self.flagFinishTurn[self.numMaison]=False
            #creation d'un thread (un thread par maison) qui va produire
            threadProduire =threading.Thread(target=Maison.__produire__, args=(self,))
            threadProduire.start()
            threadProduire.join()

            # boucle while pour que le process ne gere pas un autre jour tant qu'on a pas l equilibre prod/conso
            while self.production!=self.consommation:
                #condition pour donner
                if self.production > self.consommation:
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()
                    threadDonnerMaison.join()
                else:
                    threadAcheter = threading.Thread(target=Maison.__acheter__, args=(self,))
                    threadAcheter.start()
                    threadAcheter.join()
            #avertie qu'il a fini son jour
            self.flagFinishTurn[self.numMaison]=True





    #thread produire de l'energie
    def __produire__(self):
        taux=abs(self.listTemp[self.monJour.value]-20)/20 								#Nrj max pour 20°
        coefmaison=randint(5,10)
        self.production=(1-taux)*100+coefmaison
        self.consommation=taux*100+coefmaison
        print("maison",self.numMaison,"produit",self.production,"consomme",self.consommation)
    def __donnerMaison__(self):
        print("on donne enfin")
        #verifie si la queue est pleine
        if self.tabProduction.full() == False:
            #donne surplus de production uniquement
            self.tabProduction.put(self.production-self.condition)
        self.production=self.condition

    #thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self):
        #verifie si queue vide
        if self.tabProduction.empty()==False:

            #on augmente valeur conso en fonction de la valeur de production piochee
            self.production+=self.tabProduction.get()

        else:
            #cas ou pas de prod dispo entre les maisons on achete a marche qui fait l equilibre
            tupleSend=(self.numMaison,self.consommation-self.production)
            self.tabMarche.put(tupleSend)
            self.production=self.consommation

if __name__=="__main__":

    N=300                          #Nombre de jours de la simulation
    listTemp=Array('d',range(N))     #Liste des températures

    #Méteo (process qui genere 300 temp dans memoire partagee listTemp
    pMeteo=Process(target=meteo , args=(listTemp,N))
    pMeteo.start()
    pMeteo.join()
    monJour=Value('i',0)

    vPrix=Array('d',range(N))      #prix gere par marche
    vPrix[0]=2 #prix initial
    flagFinishTurn=Array('i',[False,False,False,False,False,False,False,False,False,False]) #se met a True chaque jour quand maison a finie ses echanges pour prevenir marche
    tabProduction = Queue()
    tabMarche = Queue()
    portefeuille=Array('d',[50,50,50,50,50,50,50,50,50,50])   #creation d'un portefeuille pour les 10 maisons process

    # On lance le marché
    pMarche=Marche(vPrix,tabMarche,listTemp,portefeuille,flagFinishTurn,monJour)
    pMarche.start()

    # On lance les process maisons
    pTotal = []  # Liste des process maisons+Marche en marche
    nMaison = 10  # nombre de maisons
    for numMaison in range(nMaison):
        maison = Maison(numMaison,tabProduction,tabMarche,listTemp,portefeuille,flagFinishTurn,monJour)
        pTotal.append(maison)
        maison.start()

    pTotal.append(pMarche)
    pMarche.join()

    if monJour.value==299:
        #plot graphe
        M=[]
        for i in range(N):
            M.append(i+1)
            M.append(i+1)
        plt.plot(M,vPrix)
        plt.title("Evolution du prix de l'énergie en fonction du jour")
        plt.xlabel('jour')
        plt.ylabel('Prix en €')
        plt.show()

