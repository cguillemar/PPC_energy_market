from multiprocessing import *
from threading import *
from random import *
from time import *
from queue import *

def meteo(result,N):
	#Entrée : N nombre de jours à étudier

	#Liste des températures 
	temp=[3.3,4.2,7.8,10.8,14.3,17.5,19.4,19.1,16.4,11.6,7.2,4.2]		#Temperatures moyennes sur 1 année de janvier à décembre
	tempf=[]
	for i in range(len(temp)-1):
		for j in range(29):
			tempf.append(round(uniform(temp[i],temp[i+1]),1))	#Temperatures pour 300 jours environ	


	for i in range (N):

		result[i]=abs(tempf[i]-20)/20			#
		

def Maison(temp):

	produc=Queue()
	consom=Queue()

	t=Thread(target=production, args=(temp,produc))
	t.start()
	t.join()


	
	print(produc.get())


def production(temp,produc):
	maxi = 100           #Le maximum de la production est défini pour une température de 20°
	coefproduc=uniform(10,50)
	for i in range (len(temp)):
		produc.put(temp[i]*maxi+coefproduc)

def consommation(temp):
	maxi = 100  

	for i in range (len(temp)):
		consom.put((1-temp[i])*maxi)








if __name__=="__main__":

	N=200

	result=Array('d',range(N))
	p=Process(target=meteo , args=(result,N))

	p.start()
	p.join()

	#print(result[:-1])					#si résult=1 meteo ok sinon pas ok

	N=randint(5,10)




	pMaisons=[]


	for i in range(N) :
		maison=Process(target=Maison, args=(result,))
		pMaisons.append(maison)

	for j in pMaisons:
		j.start()
		j.join()





