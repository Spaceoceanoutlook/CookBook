import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_list_ingredients_success(client):
    client.post("/ingredients/", json={"name": "salt"})
    client.post("/ingredients/", json={"name": "Sugar"})

    response = client.get("/ingredients/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    names = {item["name"] for item in data}
    assert names == {"salt", "sugar"}


def test_create_ingredient_success(client):
    payload = {"name": "pepper"}

    response = client.post("/ingredients/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "pepper"
    assert "id" in data


def test_create_ingredient_conflict(client):
    payload = {"name": "meet"}
    client.post("/ingredients/", json=payload)
    response = client.post("/ingredients/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_ingredient_validation_error(client):
    payload = {"name": ""}

    response = client.post("/ingredients/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_delete_ingredient_success(client):
    payload = {"name": "water"}
    create_response = client.post("/ingredients/", json=payload)
    created_ingredient = create_response.json()
    ingredient_id = created_ingredient["id"]

    response = client.delete(f"/ingredients/{ingredient_id}")

    assert response.status_code == status.HTTP_200_OK
    deleted_data = response.json()
    assert deleted_data["id"] == ingredient_id
    assert deleted_data["name"] == "water"


def test_delete_ingredient_not_found(client):
    non_existent_id = 9

    response = client.delete(f"/ingredients/{non_existent_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
