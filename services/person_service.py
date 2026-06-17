from sqlalchemy.orm import Session

from entities.person import PersonModel
from repositories.person_repository import PersonRepository


class PersonService:
    def __init__(self, db: Session) -> None:
        self._repo = PersonRepository(db)

    def create(self, name: str, age: int, language: str) -> PersonModel:
        return self._repo.create(name=name, age=age, language=language)

    def get_all(self) -> list[PersonModel]:
        return self._repo.get_all()

    def get_by_id(self, person_id: int) -> PersonModel | None:
        return self._repo.get_by_id(person_id)

    def update(self, person_id: int, name: str, age: int, language: str) -> PersonModel | None:
        return self._repo.update(person_id=person_id, name=name, age=age, language=language)

    def delete(self, person_id: int) -> bool:
        return self._repo.delete(person_id)

    def get_stats(self) -> dict:
        return self._repo.get_stats()
