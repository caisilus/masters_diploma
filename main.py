from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel, HttpUrl
from tasks import generate_mesh_task

app = FastAPI()

with open("config.json", "r", encoding="utf-8") as file:
    models_config = json.load(file)

@app.get("/models")
async def get_models():
    """
    Возвращает JSON с описанием доступных моделей и их параметров.
    """
    return models_config

class GenerationRequest(BaseModel):
    model: str
    parameters: dict
    mesh_size: float
    webhook_url: HttpUrl

@app.post("/generate")
async def generate_mesh(request: GenerationRequest):
    """
    Генерирует файл сетки для заданной модели и параметров. Отправляет результат по веб-хуку
    """
    if request.model != "branching_structure":
        raise HTTPException(status_code=400, detail="Unsupported model")

    task = generate_mesh_task.delay(request.parameters, request.mesh_size, str(request.webhook_url))
    return {"task_id": task.id, "status": "Task submitted"}
