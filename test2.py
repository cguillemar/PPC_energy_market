#auteurs: Guillemare Clément, Bernet-Rollande Agathe
from multiprocessing import Process, Value, Array, Pool
from multiprocessing import Queue
import threading
import random
import time


class Maison(Process):
    def __init__(self,debutTimer,numMaison,tabProduction):
        super().__init__()
        self.debutTimer=debutTimer
        self.consomation=100
        self.production=0
        self.numMaison=numMaison
        self.tabProduction=tabProduction


    def run(self):
        threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
        threadProduire.start()




    #thread produire de l'energie
    def __produire__(self):
        timer=time.clock()
        while True:
            if (timer%5)==0:
                print(timer)

                #production aleatoire
                self.production= random.randint(-5,10)
                if self.production<5:
                    self.consomation = self.consomation - 5 + self.production
                    threadAcheter = threading.Thread(target=Maison.__acheter__, args=(self,))
                    threadAcheter.start()
                else:
                    #consommation en fonction de ce qui est produit
                    self.production-=5
                    #gestion des threads qui gerent en fonction de la valeur de production et de consommation
                    threadDonnerMaison = threading.Thread(target=Maison.__donnerMaison__, args=(self,))
                    threadDonnerMaison.start()


                #maj du temps
                timer = time.clock()
            else:
                #maj du temps
                timer=time.clock()


    #thread donne de l'energie aux autres maisons
    def __donnerMaison__(self):
        if self.tabProduction.full() == False:
            #condition de production suffisante
            self.tabProduction.put(self.production)



    #thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self):
        if self.tabProduction.empty()==False:
            #condition de production suffisante
            print("num ",self.numMaison," ma conso avant ",self.consomation)
            self.consomation+=self.tabProduction.get(self.production)
            print("num ",self.numMaison,"ma conso apres" ,self.consomation)


    #thread vendre sur le marche
    def __vendreMarche__(self):
        print("OK")



def __getTime__(monTemps,debut):
    return monTemps-debut
# main programme
if __name__ == '__main__':
    nMaison=10
    debutTimer=time.clock()
    tabProduction=Queue()

    pMaisons=[]
    for i in range(nMaison):
        maison =Maison(debutTimer,i,tabProduction)
        pMaisons.append(maison)

    for j in pMaisons:
        j.start()
