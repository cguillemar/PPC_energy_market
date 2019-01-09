
from multiprocessing import *
from threading import *
from random import *
from time import *
from queue import *
import matplotlib.pyplot as plt

def meteo(result,N):
	#Entrée : N nombre de jours à étudier

	#Liste des températures
    temp=[3.3,4.2,7.8,10.8,14.3,17.5,19.4,19.1,16.4,11.6,7.2,4.2]		#Temperatures moyennes sur 1 année de janvier à décembre
    tempf=[]
    for i in range(len(temp)-1):
        for j in range(29):
            tempf.append(round(uniform(temp[i],temp[i+1]),1))	#Temperatures pour 300 jours environ


    for i in range (N):
        result[i]=tempf[i]

def Marche(vprix,tabProduc,tabMarche,result,i):

    vprix[i+1]=(0.99*vprix[i]+Prix(result[i]))

    while True:
    
        if tabMarche.empty==False:

            indice,valeur=tabMarche.get()
            threadAchatMarche=Thread(target=__achat_marche__,args=(Sousmaisons,indice,valeur,vprix[-1]))


    indice,valeur=tabMarche.get()

    #Thread qui fait le lien avec les maisons
def __achat_marche__(Sousmaisons,i,valeur,prix):
    #lock
    print("je suis la!!!")
    Sousmaisons[i]=Sousmaisons[i]-valeur*prix.value



def Prix(val):
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
    def __init__(self,numMaison,k,tabProduc,tabMarche,result,Sousmaisons):
        #penser a mettre le super sinon ca marche pas
        super().__init__()
        #valeurs arbitraires
        self.consommation=100
        self.production=0
        #on recupere le numero du process maison en cours
        self.numMaison=numMaison
        #queue tabProduction
        self.tabProduction=tabProduc
        #indice météo
        self.imeteo=k
        #Portefeuilles maisons
        self.Sousmaisons=Sousmaisons

        self.tabMarche=tabMarche

    #run definie ce que fait le process
    def run(self):

        #creation d'un thread (un thread par maison) qui va produire (variable production++) toute les 5 sec
        threadProduire =Thread(target=Maison.__produire__, args=(self,))
        threadProduire.start()

    #thread produire de l'energie
    def __produire__(self):

        #production aleatoire

        taux=abs(self.imeteo-20)/20 								#Nrj max pour 20°
        coefmaison=randint(5,10)
        self.production=(1-taux)*100+coefmaison
        self.consommation=taux*100+coefmaison
        #print("prod ",self.production,"conso ",self.consommation,"num",self.numMaison)
        if self.production-self.consommation <0 :

            threadAcheter =Thread(target=Maison.__acheter__, args=(self,))
            threadAcheter.start()


        else:
            #on a produit plus que prevu: on va aider les autres maions avec le surplus
            #pas besoin de decrementer consommation

            self.production=self.production-self.consommation
            threadDonnerMaison =Thread(target=Maison.__donnerMaison__,args=(self,))
            threadDonnerMaison.start()



    def __donnerMaison__(self):
        print("donne ","prod ",self.production,"conso ",self.consommation,"num",self.numMaison)
        #verifie si la queue est pleine
        if self.tabProduction.full() == False:
            #donne surplus de production qui sera convertie en valeur incrementee de conso pour les autres maisons
            self.tabProduction.put(self.production)




    #thread achete de l'energie sur le marche ou entre les maisons disponibles
    def __acheter__(self):
        print("achat ","prod ",self.production,"conso ",self.consommation,"num",self.numMaison)

        if self.tabProduction.empty()==False:

            print("num ",self.numMaison," ma conso avant ",self.consommation)
                #on augmente valeur conso en fonction de la valeur de production piochee
            self.production+=self.tabProduction.get(self.production)
            print("num ",self.numMaison,"ma conso apres" ,self.consommation)
        else:

            self.tabMarche.put((self.numMaison,self.consommation-self.production))

        #gere le cas ou on a un surplus d energie
        self.production=self.production-self.consommation
        threadDonnerMaison =Thread(target=Maison.__donnerMaison__, args=(self,))
        threadDonnerMaison.start()
        threadDonnerMaison.join()














if __name__=="__main__":

    N=300                          #Nombre de jours de la simulation



    result=Array('d',range(N))     #Liste des températures

    #Méteo
    pi=Process(target=meteo , args=(result,N))
    pi.start()
    pi.join()

    vprix=Array('d',[2]+[0]*299)

    Sousmaisons=Array('d',[50,50,50,50,50,50,50,50,50,50])

    for k in range(N):             #On lance la simulation


        pMaisons=[]                                   #Liste des process maisons
        nMaison = 10                      #nombre de maisons

        tabProduc=Queue()
        tabMarche=Queue()

        marche = Process(target=Marche, args=(vprix,tabProduc,tabMarche,result,k))         #On lance le marché
        marche.start()


        for i in range(nMaison):                     #On lance les process maisons
            maison = Maison(i,k,tabProduc,tabMarche,result,Sousmaisons)
            pMaisons.append(maison)

        for j in pMaisons:
            j.start()



        marche.join()
        for jj in pMaisons:
            jj.join()

    M=[]
    for i in range(N):
        M.append(i+1)

    plt.plot(M,vprix)
    plt.title("Evolution du prix de l'énergie en fonction du jour")
    plt.xlabel('jour')
    plt.ylabel('Prix en €')
    plt.show()
