from sqlalchemy.orm import Session

from entities.greeting import AudienceLevel, GreetingEntity
from repositories.person_repository import PersonRepository
from services.greeting_template_service import GreetingTemplateService


def _age_to_audience(age: int) -> AudienceLevel:
    if age < 18:
        return AudienceLevel.CASUAL
    if age < 65:
        return AudienceLevel.FORMAL
    return AudienceLevel.VIP


class PersonGreetingService:
    def __init__(self, db: Session) -> None:
        self._repo = PersonRepository(db)
        self._template = GreetingTemplateService()

    def greet(self, person_id: int) -> GreetingEntity | None:
        person = self._repo.get_by_id(person_id)
        if person is None:
            return None

        audience = _age_to_audience(person.age)

        supported = self._template.list_supported_languages()
        language = person.language if person.language in supported else "en"

        message = self._template.build_message(
            name=person.name,
            language=language,
            audience=audience,
            excited=False,
        )
        return GreetingEntity(message=message, language=language, audience=audience)
