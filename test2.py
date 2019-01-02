#auteurs: Guillemare Clément, Bernet-Rollande Agathe
from multiprocessing import Process, Value
from multiprocessing import Queue
import threading
import random
import time




class Maison(Process):
    def __init__(self,debutTimer):
        super().__init__()
        self.debutTimer=debutTimer
        self.consomation=10
        self.production=10
        #self.energie
    def run(self):
        print("Ma production ",self.production)


        threadProduire = threading.Thread(target=Maison.__produire__, args=(self,))
        threadProduire.start()
        threadProduire.join()
        print("Ma production ", self.production)

    #thread produire de l'energie
    def __produire__(self):
        timer=time.clock()
        while True:
            if (timer%5)==0:
                print(timer)
                self.production += random.randint(-5, 5)
                print("Ma production ", self.production)
                timer = time.clock()
            else:
                timer=time.clock()


    #thread donne de l'energie aux autres maisons
    def __donnerMaison__(self):
        if self.production>15 and self.consomation>5:
            print()




    #thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self):
        print("OK")
    #thread vendre sur le marche
    def __vendreMarche__(self):
        print("OK")



def __getTime__(monTemps,debut):
    return monTemps-debut
# main programme
if __name__ == '__main__':
    nMaison=10
    debutTimer=time.clock()

    pMaison=Maison(debutTimer)
    pMaison.start()
    pMaison.join()
