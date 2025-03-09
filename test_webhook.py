from fastapi import FastAPI, Request

webhook_app = FastAPI()

@webhook_app.post("/webhook")
async def receive_file(request: Request):
    data = await request.form()
    file = data.get("file")
    print("Получен файл:", file.filename if file else "Нет файла")
    return {"status": "ok"}
