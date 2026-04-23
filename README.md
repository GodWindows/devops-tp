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

- Les tests unitaires (`tests/unit`)
- Les tests web (`tests/web`)
- La generation d'un rapport de couverture de code (`coverage.xml`)

La couverture est informative uniquement: elle n'est pas bloquante et ne fait pas echouer le workflow, quel que soit le resultat.

Le fichier de couverture est publie comme artifact CI sous le nom `coverage-report`.

## Couverture en local

Commandes utiles pour generer la couverture localement:

```bash
pip install -r requirements.txt -r requirements-dev.txt
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report -m
coverage xml
```