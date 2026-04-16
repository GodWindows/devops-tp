from entities.greeting import GreetingEntity, GreetingRequestEntity, GreetingStatsEntity
from services.greeting_template_service import GreetingTemplateService


class GreetingService:
    def __init__(self, template_service: GreetingTemplateService) -> None:
        self._template_service = template_service
        self._request_count = 0
        self._requests_by_language: dict[str, int] = {}

    def create_greeting(self, request: GreetingRequestEntity) -> GreetingEntity:
        message = self._template_service.build_message(
            name=request.name,
            language=request.language,
            audience=request.audience,
            excited=request.excited,
        )

        self._request_count += 1
        self._requests_by_language[request.language] = self._requests_by_language.get(request.language, 0) + 1

        return GreetingEntity(
            message=message,
            language=request.language,
            audience=request.audience,
        )

    def get_stats(self) -> GreetingStatsEntity:
        return GreetingStatsEntity(
            total_requests=self._request_count,
            requests_by_language=dict(self._requests_by_language),
        )

    def get_supported_languages(self) -> list[str]:
        return self._template_service.list_supported_languages()
