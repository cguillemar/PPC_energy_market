from multiprocessing import Process
from multiprocessing import Queue
import threading
import random
import sysv_ipc

class Meteo(Process):
    def __init__(self,date,temperature):
        self.date=date
        self.temperature=temperature

    def __lectureFichier__(self):
        #on lit dans un fichier texte contenant des temperatures moy en fonction des jours

    def run(self):
        #
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

#process Marche gere toutes les transactions entre les maisons ou entre maisons et Marché
class Marche(Process):

    def __init__(self,monPrixInitial,pMaison,etat):

        #evolution du prix du marche en fonction du temps pour tracer une courbe
        self.prix=[]
        self.pMaison=pMaison
        prix.append(monPrixInitial)
        if etat==0:#communiste mode
            __communisteMode__()
        else:
            __capitalisteMode__()

    def __communisteMode__(self,pMaison):
    #on créé un thread=chaque thread communique en Pipes avec une maison pour récupérer les valeurs de l'energie et la stocke dans un tableau commun
    #on compare les valeurs
    #on créé un thread=chaque thread communique en Pipes avec une maison pour ajuster l'energie
    #s'il manque de l'energie ou s'il y a un surplus on met a jour le prix du marche

    def __capitalisteMode__(self,pMaison):
    # on créé un thread=chaque thread communique en Pipes avec une maison pour récupérer les valeurs de l'energie et la stocke dans un tableau commun
    # on met des seuils d'énergie si la demande est supérieur à un certain seuil on augmente le prix
    #Si la demande est inférieur à un certain seuil on baisse le prix
    # on créé un thread=chaque thread communique en Pipes avec une maison pour ajuster l'energie
    #en fonction du nouveau prix du marche(et donc en fonction de ses possibilités pour gérer la demande

    def __communicationAvecFils__(self):
    #on recupere les donnees des evenements ext par signaux

    def run(self):
        __calculPrix__(#arguments)
        #creation process fils Evenement Ext
        pEvenementExt=EvenExt(#arguments)
        prixActuel=prix[-1]

    def __calculPrix__(self):
        #prix a l indice n+1 depend du prix a l indice n
        #formule donnee dans le sujet
        prix.append(gamma * prix[-1] + sommeExt)

    def Tracerlacourbe(self,prix,date):
        #On plot la courbe

class EvenExt(Process):

    def __init__(self,beta,u,sommeExt,evenements):

        self.u #apparition d'un evenement (0 ou 1)
        #evenements est un dictionnaire d'évènements ayant une valeur pouvant modifier le prix du marché
        self.evenements
        self.sommeExt=0

    def run(self,beta):
       #dosomething

    def gestionevenements(self):
        #tirage aléatoire des évenements dans le dictionnaire evenements
        #on les met dans la liste eve
        eve=[]

        for i in eve :
            sommeExt=sommeExt+i

        sommeExt=beta*sommeExt

        #communication de sommeExt par pipes puis sommeEXt=0

# main programme
if __name__=='__main__':

    #alpha coefficient facteurs météorologiques
    alpha=constante
    #beta coefficient facteurs évènements extérieurs
    beta=constante

    #generation de N process maisons aleatoire
    N=random.randint(5,100)
    pMaison=[] #tableau de process Maisons
    for i in range(N):
        pMaison.append(Maison(#arguments))
        pMaison.start()

    #generation de 1 process marche
    # etat= "communiste(0)" et "capitaliste(1)" definie aleatoirement
    etat = random.randint(0, 1)
    pMarche=Marche(prixInitial du marche,pMaison,etat)
    pMarche.start()

    #creation process Meteo
    #creation des variables en memoire partagee
    with Manager() as manager:
        date=manager.list(0)
        temperature=manager.list(0)
    pMeteo=Meteo(date,temperature)