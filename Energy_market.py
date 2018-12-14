from multiprocessing import Process
from multiprocessing import Queue
import threading
import random
import sysv_ipc



class Meteo(Process):

    def __init__(self,date,ensoleilement,temperature,vent):
        self.date=[]
        self.temperature

    def __lectureFichier__(self):
        #on lit dans un fichier texte contenant des temperatures moy en fonction des jours

    def run(self):
        #creation memoire partagee des variables (meteo en mode ecriture):
        sharedMem=sysv_ipc.MessageQueue(none, sysv_ipc.IPC_CREAT)




class Maison(Process):

    def __init__(self,consume,product,etat):

        self.consume
        self.product
        self.energie

    def __calculProd__(self):
        #lit dans la memoire partagee et en fonction de la temp
        if (temperature favorable):
            #on recupere une bonne valeur de production
            self.product=bonne valeur
        else:
            #on recupere une mauvaise valeur de production
            self.product=mauvaise valeur

    def __calculCons__(self):
        #lit dans la memoire partagee et en fonction de la temp
        if (temperature favorable):
            #on recupere une faible conso
            self.consume=bonne valeur
        else:
            #on recupere une haute conso
            self.consume=mauvaise valeur

    def __calculEnergie__(self):
        self.energie=self.product-self.consume

    def run(self):
        #on recupere date et temperature dans la memoire partage (mettre des mutex pour proteger la lecture de ces donnees)
        #on traite les donnees recuperees
        threadProd= threading.Thread(target=__calculProd__, args=(temperature,))
        threadProd.start()
        threadProd.join()





class Marche(Process):

    def __init__(self,monPrixInitial,pMaison):

        #evolution du prix du marche en fonction du temps pour tracer une courbe
        self.prix=[]
        self.pMaison=pMaison
        prix.append(monPrixInitial)

    def __calculPrix__(self):
        i=0
        while True:
            prix.append(gamma*prix[i]+sommeExt)
            i+=1

    def __communicationAvecFils__(self):
        #on recupere les signaux des evenements ext

    def __communicationAvecMaisons__(self,prixActuel):
        #on cree un thread qui communique avec les maisons


    def run(self):
        __calculPrix__(#arguments)
        #creation process fils Evenement Ext
        pEvenementExt=EvenExt(#arguments)
        prixActuel=prix[-1]

class EvenExt(Process):

    def __init__(self,beta,u,sommeExt,evenements):

        self.u #apparition d'un evenement (0 ou 1)
        #evenements est un dictionnaire d'évènements ayant une valeur pouvant modifier le prix du marché
        self.evenements

    def run(self):
        #do something


# main programme

def __communisteMode__(pMaison):
    # faire communication interprocess entre Maisons
    # Si prod>conso on donne une partie de energie
    # Si conso>prod on recoit une partie de energie

def __capitalisteMode__(pMaison):
    # faire communication avec Process Marche
    # Si prod>conso on vend au marche de l'energie
    # Si conso>prod on achete au marche de l'energie


if __name__=='__main__':

    #alpha coefficient facteurs météorologiques
    alpha=constante
    #beta coefficient facteurs évènements extérieurs
    beta=constante
    # etat= "communiste(0)" et "capitaliste(1)" definie aleatoirement
    etat=random.randint(0,1)






    #generation de N process maisons aleatoire
    N=random.randint(5,100)
    pMaison=[] #tableau de process Maisons
    for i in range(N):
        pMaison.append(Maison(#arguments))
        pMaison.start()

    #generation de 1 process marche
    pMarche=Marche(#arguments)
    pMarche.start()

    #creation process Meteo
    pMeteo=Meteo(#arguments)

    if etat == 0:  # communiste mode
        threadCommuniste = threading.Thread(target=__communisteMode__, args=(pMaison,))
        threadCommuniste.start()
    else:  # capitaliste mode
        threadCapitaliste = threading.Thread(target=__capitalisteMode__, args=(pMaison,))
        threadCapitaliste.start()
