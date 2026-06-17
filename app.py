from fastapi import FastAPI

import database
import entities.person  # noqa: F401 — registers PersonModel with Base metadata
from controllers.greeting_controller import GreetingController
from controllers.person_controller import PersonController
from services.greeting_service import GreetingService
from services.greeting_template_service import GreetingTemplateService


def create_app() -> FastAPI:
    database.Base.metadata.create_all(bind=database.engine)

    application = FastAPI(title="DevOps TP API", version="1.0.0")

    template_service = GreetingTemplateService()
    greeting_service = GreetingService(template_service=template_service)
    greeting_controller = GreetingController(service=greeting_service)
    person_controller = PersonController()

    application.include_router(greeting_controller.router)
    application.include_router(person_controller.router)
    return application

app = create_app()