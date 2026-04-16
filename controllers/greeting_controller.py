from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from entities.greeting import AudienceLevel, GreetingRequestEntity
from services.greeting_service import GreetingService


class GreetingCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    language: str = Field(default="fr")
    audience: AudienceLevel = Field(default=AudienceLevel.CASUAL)
    excited: bool = Field(default=False)


class GreetingResponse(BaseModel):
    message: str
    language: str
    audience: AudienceLevel
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GreetingStatsResponse(BaseModel):
    total_requests: int
    requests_by_language: dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class GreetingController:
    def __init__(self, service: GreetingService) -> None:
        self._service = service
        self.router = APIRouter(tags=["greetings"])
        self.router.add_api_route("/hello-world", self.hello_world, methods=["GET"], response_model=GreetingResponse)
        self.router.add_api_route("/greetings", self.create_greeting, methods=["POST"], response_model=GreetingResponse)
        self.router.add_api_route("/greetings/languages", self.list_languages, methods=["GET"], response_model=list[str])
        self.router.add_api_route("/greetings/stats", self.stats, methods=["GET"], response_model=GreetingStatsResponse)

    def hello_world(self) -> GreetingResponse:
        entity = self._service.create_greeting(
            GreetingRequestEntity(name="World", language="en", audience=AudienceLevel.FORMAL)
        )
        return GreetingResponse.model_validate(entity)

    def create_greeting(self, payload: GreetingCreateRequest) -> GreetingResponse:
        normalized_language = payload.language.strip().lower()
        try:
            entity = self._service.create_greeting(
                GreetingRequestEntity(
                    name=payload.name,
                    language=normalized_language,
                    audience=payload.audience,
                    excited=payload.excited,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return GreetingResponse.model_validate(entity)

    def list_languages(self) -> list[str]:
        return self._service.get_supported_languages()

    def stats(self) -> GreetingStatsResponse:
        return GreetingStatsResponse.model_validate(self._service.get_stats())
