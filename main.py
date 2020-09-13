from typing import Dict, Any, Optional
import os

from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, Text
from pydantic import BaseModel, ValidationError

import database

app = Flask(__name__)


class PersonModel(BaseModel):
    name: str
    age: Optional[int]
    address: Optional[str]
    work: Optional[str]


class Person(database.Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    age = Column(Integer, nullable=True)
    address = Column(Text, nullable=True)
    work = Column(Text, nullable=True)

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "address": self.address,
            "work": self.work,
        }


def response_400(message: str, extra: Dict[str, Any] = None):
    return {"message": message, "errors": extra if extra else {}}, 400


def response_404(message: str):
    return {"message": message}, 404


@app.route('/persons/<person_id>', methods=["GET"])
def get_person(person_id: Any):
    """
    информация о человеке
    """
    try:
        person_id = int(person_id)
    except Exception:
        return response_400("bad person id", {"person_id": person_id})

    with database.Session() as s:
        person = s.query(Person).get(person_id)
        if not person:
            return response_404(f"Person with id={person_id} not found")
        return person.to_json(), 200


@app.route('/persons/', methods=["GET"])
def get_all_persons():
    """
    информация о всех человеках
    """
    with database.Session() as s:
        all_persons = s.query(Person).all()
        result = [person.to_json() for person in all_persons]
    return jsonify(result), 200


@app.route('/person/', methods=["POST"])
def create_person():
    """
    создать человека
    """
    input_json = request.get_json(force=True)
    if not isinstance(input_json, dict):
        return response_400("non-json input", {"input": input_json})

    try:
        person_model = PersonModel.parse_obj(input_json)
    except ValidationError as e:
        return response_400("bad input json", {"validation errors": e.errors()})

    try:
        with database.Session() as s:
            person = Person(**person_model.dict())
            s.add(person)
            s.flush()
            return person.to_json(), 201
    except Exception as e:
        return response_400("database error", {str(e): repr(e)})




@app.route('/person/<person_id>', methods=["DELETE"])
def delete_person(person_id: Any):
    """
    удалить человека
    """
    try:
        person_id = int(person_id)
    except Exception:
        return response_400("bad person id", {"person_id": person_id})

    with database.Session() as s:
        person = s.query(Person).get(person_id)
        if not person:
            return response_404(f"Person with id={person_id} not found")
        s.delete(person)
        return {"message": "success"}, 200


@app.route('/person/<person_id>', methods=["PATCH"])
def update_person(person_id: Any):
    """
    обновить человека
    """
    try:
        person_id = int(person_id)
    except Exception:
        return response_400("bad person id", {"person_id": person_id})

    input_json = request.get_json(force=True)
    if not isinstance(input_json, dict):
        return response_400("non-json input", {"input": input_json})

    try:
        person_model = PersonModel.parse_obj(input_json)
    except ValidationError as e:
        return response_400("bad input json", {"validation errors": e.errors()})

    with database.Session() as s:
        person = s.query(Person).get(person_id)
        if not person:
            return response_404(f"Person with id={person_id} not found")
        s.query(Person).filter(Person.id == person_id).update(person_model.dict())
        s.flush()
        return s.query(Person).get(person_id).to_json(), 200


if __name__ == '__main__':
    database.create_schema()
    app.run("0.0.0.0", os.environ.get("PORT"))  # дев-сервер (думаю, ради лабы поднимать wsgi нецелесообразно)






