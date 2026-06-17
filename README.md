# devops-tp

API FastAPI structuree en couches avec deux services : greetings (en mémoire) et persons (persisté SQLite).

## Structure

```
app.py                          # point d'entrée FastAPI
database.py                     # moteur SQLAlchemy + session SQLite
entities/
  greeting.py                   # entités métier greetings
  person.py                     # modèle SQLAlchemy Person
repositories/
  person_repository.py          # accès base de données persons
services/
  greeting_service.py
  greeting_template_service.py
  person_service.py
controllers/
  greeting_controller.py
  person_controller.py
data/                           # base SQLite (créée au démarrage, gitignorée)
  persons.db
```

---

## Endpoints API

### Greetings

| Méthode | Chemin | Description |
|---------|--------|-------------|
| `GET` | `/hello-world` | Salutation formelle anglaise pour "World" |
| `POST` | `/greetings` | Créer une salutation personnalisée |
| `GET` | `/greetings/languages` | Lister les langues supportées (`en`, `es`, `fr`) |
| `GET` | `/greetings/stats` | Statistiques des requêtes de salutation |

#### POST /greetings — corps

```json
{
  "name": "Alice",
  "language": "fr",
  "audience": "casual",
  "excited": false
}
```

- `language` : `fr` | `en` | `es`
- `audience` : `casual` | `formal` | `vip`
- `excited` : `true` → ponctuation `!`, `false` → `.`

#### Réponse

```json
{
  "message": "Salut Alice.",
  "language": "fr",
  "audience": "casual",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

---

### Persons (CRUD — SQLite)

| Méthode | Chemin | Code succès | Description |
|---------|--------|-------------|-------------|
| `POST` | `/persons` | `201` | Créer une personne |
| `GET` | `/persons` | `200` | Lister toutes les personnes |
| `GET` | `/persons/stats` | `200` | Statistiques sur les personnes |
| `GET` | `/persons/{id}` | `200` | Obtenir une personne par ID |
| `PUT` | `/persons/{id}` | `200` | Remplacer une personne |
| `DELETE` | `/persons/{id}` | `204` | Supprimer une personne |
| `GET` | `/persons/{id}/greet` | `200` | Saluer une personne via son profil |

#### POST /persons et PUT /persons/{id} — corps

```json
{
  "name": "Alice",
  "age": 30,
  "language": "fr"
}
```

- `name` : 1–100 caractères
- `age` : entier entre 0 et 150
- `language` : code langue, 2–10 caractères

#### GET /persons/{id} — réponse

```json
{
  "id": 1,
  "name": "Alice",
  "age": 30,
  "language": "fr"
}
```

#### GET /persons/stats — réponse

```json
{
  "total": 3,
  "average_age": 34.67,
  "by_language": {
    "fr": 2,
    "en": 1
  }
}
```

#### GET /persons/{id}/greet — réponse

Retourne une salutation construite automatiquement depuis le profil de la personne :

- **langue** : celle de la personne, ou `en` si non supportée par le service de greetings
- **niveau de respect** déterminé par l'âge :

| Âge | Audience |
|-----|----------|
| < 18 | `casual` |
| 18 – 64 | `formal` |
| ≥ 65 | `vip` |

```json
{
  "message": "Hello Alice.",
  "language": "en",
  "audience": "formal",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

#### Codes d'erreur communs

| Code | Cas |
|------|-----|
| `400` | Langue non supportée (greetings) |
| `404` | Personne introuvable |
| `422` | Corps de requête invalide ou champ manquant |

---

## Lancer l'application

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Documentation interactive disponible sur `http://localhost:8000/docs`.

## Docker

```bash
docker build -t devops-tp .
docker run -p 8000:8000 -v $(pwd)/data:/app/data devops-tp
```

Le volume `-v $(pwd)/data:/app/data` persiste la base SQLite entre les redémarrages du conteneur.

## Tests Postman

Importer `devops-tp.postman_collection.json` dans Postman. La variable `{{baseUrl}}` pointe sur `http://localhost:8000` par défaut.

---

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

```bash
pip install -r requirements.txt -r requirements-dev.txt
coverage run -m unittest discover -s tests/unit -p "test_*.py"
coverage run --append -m unittest discover -s tests/web -p "test_*.py"
coverage report -m
coverage xml
```
