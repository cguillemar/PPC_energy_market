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



#Fonction qui gère la communication entre les maisons 
def maisons(meteo,conn):


	production=[]			#Production des maisons
	consommation=[]			#Consommation des maisons

	produc=Queue()
	consom= Queue()


	N=randint(5,10)		#nombre aléatoire de maisons
				#liste des process maison 
	for i in range(N) :
		maison=Thread(target=Maison, args=(meteo,produc,consom))
		maison.start()
		maison.join()


		production.append(produc.get())
		consommation.append(consom.get())


	s=vente(production,consommation)
	nrj=capitaliste(production,consommation)

	conn.send(s)
	conn.send(nrj)
	conn.close()
		


def Maison(meteo,produc,consom):

	coefmaison=uniform(-5,5)				#Ona une variation en fonction des maisons


	t0=Thread(target=Production, args=(meteo,produc,coefmaison))
	t1=Thread(target=Consommation, args=(meteo,consom,coefmaison))
	t0.start()
	t1.start()

	t0.join()
	t1.join()



def vente(production,consommation):

	s=0

	l=len(production)
	for i in range (l):
		s=s+production[i]
		s=s-consommation[i]

	return(s)
	
def capitaliste(production,consommation):
	nrjfin=[]
	l=len(production)

	for i in range (l):
		nrjfin.append(production[i]-consommation[i])

	return(nrjfin)

def Production(meteo,produc,coefmaison):		
	taux=abs(meteo-20)/20 								#Nrj max pour 20°

	produc.put((1-taux)*meteo+coefmaison)





def Consommation(meteo,consom,coefmaison):
	taux=abs(meteo-20)/20							#Nrj max pour 1°

	consom.put(taux*meteo+coefmaison)


def Marché(meteo,prix):

	parent_conn, child_conn = Pipe()
	p=Process(target=maisons, args=(meteo,child_conn))
	p.start()
	val=parent_conn.recv()
	p.join()

	prix.value=Prix(val)

def Prix(val):
	if val < -20:
		return(0.05)

	if val < -15 and val >= -20:
		return(0.049)

	if val < -10 and val >= -15:
		return(0.048)

	if val < -5 and val >= -10:
		return(0.047)

	if val < 0 and val >= -5:
		return(0.046)

	if val < 5 and val >= 0:
		return(-0.045)

	if val < 10 and val >= 5:
		return(-0.044)

	a=-0.044

	for i in range(10,150,10):
		if val < i and val >= i+10:
			a=a-0.001
			return(a)






if __name__=="__main__":

	N=300

	evolutionprixmaisons=[]

	result=Array('d',range(N))
	pi=Process(target=meteo , args=(result,N))

	pi.start()
	pi.join()


	prix=Value('d',0.0)
	

	for i in range(N):
		meteojour=result[i]
		p=Process(target=Marché, args=(meteojour,prix))
		p.start()
		p.join()
		evolutionprixmaisons.append(prix.value)

	prix=[0.145]
	for i in range(N-1):
		prix.append(0.99*prix[i]+evolutionprixmaisons[i])

   
	M=[]
	for i in range(N):
		M.append(i+1)

	plt.plot(M,prix)
	plt.title("Evolution du prix de l'énergie en fonction du jour")
	plt.xlabel('jour')
	plt.ylabel('Prix en €')
	plt.show()



	


