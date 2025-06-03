import math
import gmsh
import os
import requests
from celery import Celery

from mesh_generators.volume_generator_factory import VolumeGeneratorFactory

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("tasks", broker=redis_url)

@celery_app.task(bind=True)
def generate_mesh_task(self, model, parameters, mesh_size, webhook_url):
    gmsh.initialize()
    gmsh.model.add(model)

    volume_generator = VolumeGeneratorFactory.build(model, parameters)

    all_elements = volume_generator.generate_volume()

    min_size = 0.9 * mesh_size
    max_size = 1.1 * mesh_size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

    # Генерация сетки
    gmsh.model.mesh.generate(3)

    output_filename = f"mesh_{generate_mesh_task.request.id}.msh"

    # Сохранение в файл
    gmsh.write(output_filename)

    gmsh.finalize()

    try:
        with open(output_filename, "rb") as file:
            files = {"file": (output_filename, file, "application/octet-stream")}
            response = requests.post(webhook_url, files=files)
            response.raise_for_status()

        os.remove(output_filename)
    except Exception as e:
        print("Ошибка при отправке файла:", e)

    return "Генерация и отправка сетки завершены"
