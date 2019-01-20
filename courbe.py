import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


fig=plt.figure()


def animate(i):
	fichier = open("Courbes.txt","r")
	
	x=[]
	y=[]

	for ligne in fichier :
		if len(ligne)>1:
			a,b = ligne.split(",")
			x.append(float(b))
			y.append(float(a))

	fig.clear()
	plt.plot(x,y)
	plt.title("Evolution du prix en fonction du jour")
	plt.xlabel("Jour")
	plt.ylabel("Prix en centimes")
	plt.xlim(-20,380)
	plt.ylim(0,7)

ani = animation.FuncAnimation(fig,animate,interval = 10)
plt.show()



