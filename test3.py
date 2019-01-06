#auteurs: Guillemare Clément, Bernet-Rollande Agathe
from multiprocessing import Process, Value, Array, Pool
from multiprocessing import Queue
import threading
import random
import time


#process maison: ca fonctionne comme avec def (cest juste une classe qui herite de l objet Process)
#difference avec def: init et run sont reunies
class Maison(Process):

    #__init__: constructeur, initialise tout les parametres
    def __init__(self,debutTimer,numMaison,tabProduction):
        #penser a mettre le super sinon ca marche pas
        super().__init__()
        #en fait debutTimer ne sert a rien ici
        self.debutTimer=debutTimer
        #valeurs arbitraires
        self.consomation=100
        self.production=0
        #on recupere le numero du process maison en cours
        self.numMaison=numMaison
        #queue tabProduction
        self.tabProduction=tabProduction

    #run definie ce que fait le process
    def run(self):
        #creation d'un thread (un thread par maison) qui va produire (variable production++) toute les 5 sec
        threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
        threadProduire.start()




    #thread produire de l'energie
    def __produire__(self):
        #comme on a initialise le timer (debutTimer): timer donne le temps depuis debutTimer
        timer=time.clock()
        #boucle infinie pour que le thread ne s'arrete pas a chaque fois qu'il a produit
        while True:
            #condition pour produire toute les 5 sec
            if (timer%5)==0:
                print(timer)

                #production aleatoire
                self.production= random.randint(-5,10)
                #Si production<aux depenses (conso qui diminue de 5 toute les 5sec)
                if self.production<5:
                    #maj val conso
                    self.consomation = self.consomation - 5 + self.production
                    #on va acheter (demander) de l energie aux autres maisons
                    threadAcheter = threading.Thread(target=Maison.__acheter__, args=(self,))
                    threadAcheter.start()
                else:
                    #on a produit plus que prevu: on va aider les autres maions avec le surplus
                    #pas besoin de decrementer consommation
                    self.production-=5

                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()


                #maj du temps
                timer = time.clock()
            else:
                #maj du temps
                timer=time.clock()


    #thread donne de l'energie aux autres maisons
    def __donnerMaison__(self):
        #verifie si la queue est pleine
        if self.tabProduction.full() == False:
            #donne surplus de production qui sera convertie en valeur incrementee de conso pour les autres maisons
            self.tabProduction.put(self.production)



    #thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self):
        #verifie si la queue est vide
        if self.tabProduction.empty()==False:
            print("num ",self.numMaison," ma conso avant ",self.consomation)
            #on augmente valeur conso en fonction de la valeur de production piochee
            self.consomation+=self.tabProduction.get(self.production)
            print("num ",self.numMaison,"ma conso apres" ,self.consomation)


    #thread vendre sur le marche
    def __vendreMarche__(self):
        print("OK")




# main programme
if __name__ == '__main__':
    #nbre de process maison
    nMaison=10
    #time.clock() donne le temps en sec a partir du premier appel de la methode
    #debutTimer est donc l'origine des temps
    debutTimer=time.clock()
    #tabproduction est une queue permettant aux maisons de se partager des valeurs de production
    tabProduction=Queue()

    #creation des process Maison
    pMaisons=[]
    for i in range(nMaison):
        maison =Maison(debutTimer,i,tabProduction)
        pMaisons.append(maison)

    for j in pMaisons:
        j.start()
