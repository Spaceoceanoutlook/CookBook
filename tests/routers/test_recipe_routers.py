import pytest
from fastapi import status


def test_create_recipe_success(client):
    client.post("/ingredients/", json={"name": "Salt"})

    payload = {
        "title": "Soup",
        "description": "Tasty soup",
        "ingredients": [
            {"name": "salt"},
            {"name": "Pepper"},
        ],
    }

    response = client.post("/recipes/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["title"] == "soup"
    assert len(data["ingredients"]) == 2
    names = {item["name"] for item in data["ingredients"]}
    assert names == {"salt", "pepper"}


def test_get_recipe_success(client):
    client.post("/ingredients/", json={"name": "sugar"})

    payload = {
        "title": "Cake",
        "description": "Sweet cake",
        "ingredients": [{"name": "sugar"}],
    }

    create_res = client.post("/recipes/", json=payload)
    recipe = create_res.json()
    recipe_id = recipe["id"]

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == recipe_id
    assert data["title"] == "cake"
    assert data["ingredients"][0]["name"] == "sugar"


def test_get_recipe_not_found(client):
    response = client.get("/recipes/9")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_recipe_success(client):
    client.post("/ingredients/", json={"name": "milk"})

    create_res = client.post(
        "/recipes/",
        json={
            "title": "Pancakes",
            "description": "Simple pancakes",
            "ingredients": [{"name": "milk"}],
        },
    )
    recipe_id = create_res.json()["id"]

    update_payload = {
        "title": "New pancakes",
        "description": "Better pancakes",
        "ingredients": [{"name": "flour"}],
    }

    response = client.put(f"/recipes/{recipe_id}", json=update_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["title"] == "new pancakes"
    assert data["ingredients"][0]["name"] == "flour"


def test_update_recipe_not_found(client):
    payload = {}
    response = client.put("/recipes/9", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_recipe_success(client):
    client.post("/ingredients/", json={"name": "water"})

    create_res = client.post(
        "/recipes/",
        json={
            "title": "Tea",
            "description": "Hot tea",
            "ingredients": [{"name": "water"}],
        },
    )
    recipe_id = create_res.json()["id"]

    response = client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == status.HTTP_200_OK

    deleted = response.json()
    assert deleted["id"] == recipe_id
    assert deleted["title"] == "tea"


def test_delete_recipe_not_found(client):
    response = client.delete("/recipes/9")
    assert response.status_code == status.HTTP_404_NOT_FOUND
