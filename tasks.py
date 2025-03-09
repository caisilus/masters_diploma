import math
import gmsh
import os
import requests
from celery import Celery

from branching_elements_generator import BranchingElementsGenerator

REDIS_IP = "172.18.225.19"
# REDIS_IP = "localhost"
celery_app = Celery("tasks", broker=f"redis://{REDIS_IP}:6379/0")

@celery_app.task(bind=True)
def generate_mesh_task(self, parameters, mesh_size, webhook_url):
    # Извлекаем параметры с установкой значений по умолчанию
    r_root = parameters.get("r_root", 0.5)
    h_root = parameters.get("h_root", 4.0)
    r_branch = parameters.get("r_branch", 0.4)
    h_branch = parameters.get("h_branch", 3.0)
    num_branches = parameters.get("num_branches", 4)
    angle = math.radians(parameters.get("angle", 30))

    num_elements_x = parameters.get("num_elements_x", 2)
    num_elements_y = parameters.get("num_elements_y", 2)
    num_elements_z = parameters.get("num_elements_z", 2)

    gmsh.initialize()
    gmsh.model.add("branch_element")

    element_generator = BranchingElementsGenerator(r_root, h_root, r_branch, h_branch, num_branches, angle)

    all_elements = element_generator.generate_volume(num_elements_x, num_elements_y, num_elements_z)

    gmsh.model.mesh.setSize(gmsh.model.getEntities(0), mesh_size)

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
    except Exception as e:
        print("Ошибка при отправке файла:", e)

    return "Генерация и отправка сетки завершены"
