from sqlalchemy.orm import Session

from entities.person import PersonModel


class PersonRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, name: str, age: int, language: str) -> PersonModel:
        person = PersonModel(name=name, age=age, language=language)
        self._db.add(person)
        self._db.commit()
        self._db.refresh(person)
        return person

    def get_all(self) -> list[PersonModel]:
        return self._db.query(PersonModel).all()

    def get_by_id(self, person_id: int) -> PersonModel | None:
        return self._db.query(PersonModel).filter(PersonModel.id == person_id).first()

    def update(self, person_id: int, name: str, age: int, language: str) -> PersonModel | None:
        person = self.get_by_id(person_id)
        if person is None:
            return None
        person.name = name
        person.age = age
        person.language = language
        self._db.commit()
        self._db.refresh(person)
        return person

    def delete(self, person_id: int) -> bool:
        person = self.get_by_id(person_id)
        if person is None:
            return False
        self._db.delete(person)
        self._db.commit()
        return True

    def get_stats(self) -> dict:
        persons = self.get_all()
        total = len(persons)
        average_age = round(sum(p.age for p in persons) / total, 2) if total > 0 else 0.0
        by_language: dict[str, int] = {}
        for p in persons:
            by_language[p.language] = by_language.get(p.language, 0) + 1
        return {"total": total, "average_age": average_age, "by_language": by_language}
