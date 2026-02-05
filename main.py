from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from typing import List

app = FastAPI()

DATA_FILE = "data.json"


# -------------------- Utils --------------------

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------- Schema --------------------

class Item(BaseModel):
    id: int
    name: str


class ItemUpdate(BaseModel):
    name: str


class ItemCreate(BaseModel):
    name: str


# -------------------- CRUD APIs --------------------

@app.post("/items", response_model=Item , status_code=201)
def create_item(item: ItemCreate):
    data = read_data()

    # determine next id
    next_id = max([i["id"] for i in data], default=0) + 1

    new_item = {
        "id": next_id,
        "name": item.name
    }

    data.append(new_item)
    write_data(data)

    return new_item


@app.get("/items", response_model=List[Item], status_code=200)
def get_items():
    return read_data()


@app.get("/items/{item_id}", response_model=Item, status_code=200) 
def get_item(item_id: int):
    data = read_data()

    for item in data:
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail="Item not found")




@app.put("/items/{item_id}", response_model=Item, status_code=200)
def update_item(item_id: int, updated_item: ItemUpdate):
    data = read_data()

    for index, item in enumerate(data):
        if item["id"] == item_id:
            data[index] = {"id": item_id, **updated_item.dict()}
            write_data(data)
            return data[index]

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: int):
    data = read_data()

    for index, item in enumerate(data):
        if item["id"] == item_id:
            data.pop(index)
            write_data(data)
            return {"message": "Item deleted successfully"}

    raise HTTPException(status_code=404, detail="Item not found")



# search query parameter
@app.get("/search", response_model=List[Item], status_code=200)
def search_items(name: str):
    data = read_data()
    result = [item for item in data if name.lower() in item["name"].lower()]
    return result