import json

import pytest
from sqlalchemy import create_engine

from main import app, Person
import database

# test data
ID = 1
NAME = 'John'
AGE = 40
ADDRESS = 'Hobo'
WORK = "Google"

person_response = {"id": ID, "name": NAME, "age": AGE, "address": ADDRESS, "work": WORK}
new_person_response = {"id": ID+1, "name": NAME, "age": AGE, "address": ADDRESS, "work": WORK}
no_name_error_response = {
    "errors": {
        "validation errors": [{"loc": ["name"], "msg": "field required", "type": "value_error.missing"}]
    },
    "message": "bad input json"
}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    database.engine = create_engine(f"sqlite:///")

    with app.test_client() as client:
        database.create_schema()
        with database.Session() as s:
            s.add(Person(id=ID, name=NAME, age=AGE, address=ADDRESS, work=WORK))
        yield client


@pytest.mark.parametrize('person_id, expected_status_code, expected_response', [
    (ID, 200, person_response),
    (-1, 404, {"message": "Person with id=-1 not found"})
])
def test_get_person(client, person_id, expected_status_code, expected_response):
    response = client.get(f"/persons/{person_id}")
    assert response.status_code == expected_status_code
    assert json.loads(response.data) == expected_response


def test_get_all_persons(client):
    response = client.get("/persons/")
    assert response.status_code == 200

    response = json.loads(response.data)
    assert response == [person_response]


@pytest.mark.parametrize('input_json, expected_status_code, expected_response', [
    ({"name": NAME, "age": AGE, "address": ADDRESS, "work": WORK}, 201, new_person_response),
    ({"name": NAME}, 201, {"id": ID+1, "name": NAME, "age": None, "address": None, "work": None}),
    ({"age": AGE}, 400, no_name_error_response),
])
def test_create_person(client, input_json, expected_status_code, expected_response):
    response = client.post("/person/", json=input_json)
    assert response.status_code == expected_status_code

    response = json.loads(response.data)
    assert response == expected_response


@pytest.mark.parametrize('person_id, expected_status_code, expected_response', [
    (ID, 200, {"message": "success"}),
    (-1, 404, {"message": "Person with id=-1 not found"})
])
def test_delete_person(client, person_id, expected_status_code, expected_response):
    response = client.delete(f"/person/{person_id}")
    assert response.status_code == expected_status_code

    response = json.loads(response.data)
    assert response == expected_response


@pytest.mark.parametrize('person_id, input_json, expected_status_code, expected_response', [
    (1, {"name": "someone"}, 200, {"id": ID, "name": "someone", "age": None, "address": None, "work": None}),
    (1, {"name": NAME, "age": AGE, "address": ADDRESS, "work": WORK}, 200, person_response),
    (1, {"age": AGE}, 400, no_name_error_response),
    (-1, {"name": NAME}, 404, {"message": "Person with id=-1 not found"}),
])
def test_update_person(client, person_id, input_json, expected_status_code, expected_response):
    response = client.patch(f"/person/{person_id}", json=input_json)
    print(response.data)
    assert response.status_code == expected_status_code

    response = json.loads(response.data)
    assert response == expected_response