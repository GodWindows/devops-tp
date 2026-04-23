# devops-tp

API FastAPI structuree en couches:

- Entites metier dans [entities/greeting.py](entities/greeting.py)
- Services applicatifs dans [services/greeting_service.py](services/greeting_service.py) et [services/greeting_template_service.py](services/greeting_template_service.py)
- Controleur web dans [controllers/greeting_controller.py](controllers/greeting_controller.py)

Endpoints:

- `GET /hello-world`
- `POST /greetings`
- `GET /greetings/languages`
- `GET /greetings/stats`

## CI

Le pipeline CI (GitHub Actions) execute:

- 3 etapes de verification:
	- tests unitaires (`tests/unit`)
	- tests web (`tests/web`)
	- couverture de code (`coverage.xml`)
- 1 etape de qualite de code SonarQube (si credentials presents)

La couverture est informative uniquement: elle n'est pas bloquante et ne fait pas echouer le workflow, quel que soit le resultat.

Le fichier de couverture est publie comme artifact CI sous le nom `coverage-report`.

## SonarQube (qualite de code)

Le job CI de scan SonarQube est configure dans le workflow et utilise `sonar-project.properties` a la racine du projet.

Credentials requis dans GitHub Actions:

- `SONAR_TOKEN`
- `SONAR_HOST_URL`

Ou les configurer:

- GitHub repo > Settings > Secrets and variables > Actions > New repository secret

Ou recuperer les credentials:

- `SONAR_TOKEN`: dans SonarQube/SonarCloud > votre profil utilisateur > Security > Generate Token
- `SONAR_HOST_URL`: URL de votre serveur SonarQube (exemple SonarCloud: `https://sonarcloud.io`)

## Couverture en local

Commandes utiles pour generer la couverture localement:

```bash
pip install -r requirements.txt -r requirements-dev.txt
coverage run -m unittest discover -s tests/unit -p "test_*.py"
coverage run --append -m unittest discover -s tests/web -p "test_*.py"
coverage report -m
coverage xml
```