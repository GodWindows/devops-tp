from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from controllers.greeting_controller import GreetingResponse
from database import SessionLocal
from services.person_greeting_service import PersonGreetingService
from services.person_service import PersonService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PersonCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)
    language: str = Field(min_length=2, max_length=10)


class PersonUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)
    language: str = Field(min_length=2, max_length=10)


class PersonResponse(BaseModel):
    id: int
    name: str
    age: int
    language: str

    model_config = ConfigDict(from_attributes=True)


class PersonStatsResponse(BaseModel):
    total: int
    average_age: float
    by_language: dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class PersonController:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/persons", tags=["persons"])
        self.router.add_api_route("", self.create_person, methods=["POST"], response_model=PersonResponse, status_code=201)
        self.router.add_api_route("", self.list_persons, methods=["GET"], response_model=list[PersonResponse])
        self.router.add_api_route("/stats", self.get_stats, methods=["GET"], response_model=PersonStatsResponse)
        self.router.add_api_route("/{person_id}", self.get_person, methods=["GET"], response_model=PersonResponse)
        self.router.add_api_route("/{person_id}", self.update_person, methods=["PUT"], response_model=PersonResponse)
        self.router.add_api_route("/{person_id}", self.delete_person, methods=["DELETE"], status_code=204)
        self.router.add_api_route("/{person_id}/greet", self.greet_person, methods=["GET"], response_model=GreetingResponse)

    def create_person(self, payload: PersonCreateRequest, db: Session = Depends(get_db)) -> PersonResponse:
        person = PersonService(db).create(name=payload.name, age=payload.age, language=payload.language)
        return PersonResponse.model_validate(person)

    def list_persons(self, db: Session = Depends(get_db)) -> list[PersonResponse]:
        persons = PersonService(db).get_all()
        return [PersonResponse.model_validate(p) for p in persons]

    def get_stats(self, db: Session = Depends(get_db)) -> PersonStatsResponse:
        return PersonStatsResponse.model_validate(PersonService(db).get_stats())

    def get_person(self, person_id: int, db: Session = Depends(get_db)) -> PersonResponse:
        person = PersonService(db).get_by_id(person_id)
        if person is None:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
        return PersonResponse.model_validate(person)

    def update_person(self, person_id: int, payload: PersonUpdateRequest, db: Session = Depends(get_db)) -> PersonResponse:
        person = PersonService(db).update(person_id=person_id, name=payload.name, age=payload.age, language=payload.language)
        if person is None:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
        return PersonResponse.model_validate(person)

    def delete_person(self, person_id: int, db: Session = Depends(get_db)) -> None:
        deleted = PersonService(db).delete(person_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    def greet_person(self, person_id: int, db: Session = Depends(get_db)) -> GreetingResponse:
        result = PersonGreetingService(db).greet(person_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
        return GreetingResponse.model_validate(result)
