Auteurs: Guillemare Cl�ment, Bernet-Rollande Agathe

The Energy Market:

Pr�requis:
-fonctionne sur python 3.6 et +
-module matplotlib a telecharger (https://matplotlib.org/)

Contenu de l'archive:
-2 programmes pythons: EnergyMarketVf.py (g�re toute la simulation et l'affichage des graphes finaux)
		     Courbe.py (permet le tracage de l'evolution du prix du marche en fonction du jour et en temps reel)

-2 fichiers textes: Courbes.txt (ecrit par le programme EnergyMarketVf.py "prix,jour\n" et lu par Courbe.py )
	            nrj.txt (ecriture des echanges des maisons entre elles et avec marche pour chaque jour par EnergyMarketVf.py)

Fonctionnement:
-Vider le contenu des fichiers .txt
-Lancer s�paremment (sur 2 terminaux) les programmes EnergyMarketVf.py puis Courbe.py 
Remarque:
Comme Courbe.py attend que EnergyMarket.py ecrive sur le fichier Courbes.txt, il convient de d'abord configurer la simulation (mode utilis� et nombre de maisons voulus)
puis d'attendre le message "cr�ation march�" avant de lancer Courbe.py

-Nous avons remarqu� que la simulation ne supporte pas un nombre trop grand de maisons et que ce dernier d�pend aussi des capacit�s de l'ordinateur.
Pour une utilisation optimale, il convient de ne pas d�passer 50 maisons.
