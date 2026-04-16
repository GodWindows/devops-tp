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