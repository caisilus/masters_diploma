from fastapi import FastAPI
import json

app = FastAPI()

with open("config.json", "r", encoding="utf-8") as file:
    models_config = json.load(file)

@app.get("/models")
async def get_models():
    """
    Возвращает JSON с описанием доступных моделей и их параметров.
    """
    return models_config
