# Epic Events
Ce projet est un CRM à destination de 3 pôles de collaborateurs : commercial, support et gestion.
Chaque acteur aura la possibilité de lire, modifier ou supprimer des éléments en fonction de son rôle.

# Installation
Assurez-vous d'avoir Python et pip installés sur votre système.

Clonez ce dépôt vers votre machine locale :

```
git clone https://github.com/AurelienAllenic/epic_events-p12
cd mon_projet
```

Installez les dépendances requises en exécutant :
```
pip install -r requirements.txt
```
# Configuration
Configurez votre base de données dans le fichier settings.py.

Appliquez les migrations nécessaires avec la commande :
```
python manage.py migrate
```

# Utilisation
Pour démarrer le serveur de développement, exécutez la commande suivante :
```
python manage.py runserver
```

L'application sera alors accessible à l'adresse http://127.0.0.1:8000/.

# Endpoints API
Pas encore d'endpoints délimités

# Licence
Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.