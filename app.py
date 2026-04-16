from fastapi import FastAPI

from controllers.greeting_controller import GreetingController
from services.greeting_service import GreetingService
from services.greeting_template_service import GreetingTemplateService



def create_app() -> FastAPI:
    application = FastAPI(title="DevOps TP API", version="1.0.0")

    template_service = GreetingTemplateService()
    greeting_service = GreetingService(template_service=template_service)
    greeting_controller = GreetingController(service=greeting_service)

    application.include_router(greeting_controller.router)
    return application

app = create_app()