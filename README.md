Programme en version 1.5.1.


# Qu'est-ce que SeriesWatcher ?

SeriesWatcher permet de visualiser des séries TV présentes sur le disque dur en y ajoutant des informations telles que le titre de chaque épisode, une image et la description de l'épisode. Il permet de naviguer facilement entre les saisons d'une série et permet de rechercher un épisode en fonction de son titre.


# Comment installer SeriesWatcher ?

D'abord, veuillez extraire les fichiers du ZIP.


## Pour Windows

Il faut installer :

- [Python 2.7](http://python.org/ftp/python/2.7.3/python-2.7.3.msi)
- [PyQt 4.9 pour Python 2.7](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.9.5/PyQt-Py2.7-x86-gpl-4.9.5-1.exe/download)

Enfin, vous pouvez exécuter le fichier `serieswatcher.pyw`.


## Pour Linux

Télécharger les sources de SeriesWatcher. Si PyQt4 n'est pas installé sur votre machine, vous pouvez faire :

    sudo apt-get install python-qt4

Pour lancer SeriesWatcher, vous devez éxecuter le fichier `serieswatcher.pyw` :

    python2.7 serieswatcher.pyw


# Mise à jour

## Avant la 1.2

Déplacer les fichiers `series-watcher.cfg` et `database` de SeriesWatcher 1.1 dans le nouveau dossier de SeriesWatcher. Ouvrez ensuite SeriesWatcher normalement.


## Après la 1.2

Pour mettre à jour SeriesWatcher, il faut extraire les fichiers de l’archive ZIP de la nouvelle version dans un dossier. Ensuite il faut déplacer le dossier `user` de l’ancienne installation dans le nouveau dossier. Ouvrez ensuite SeriesWatcher et cliquez sur « Oui » pour mettre à jour l’ancienne base de données.


# Fonctionnalités additionnelles

SeriesWatcher contient un lecteur vidéo intégré basé sur VLC 2. Il faut donc avoir installé celui-ci pour pouvoir en profiter.