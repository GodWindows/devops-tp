from fastapi import FastAPI

app = FastAPI()

@app.get("/hello-world")
def hello():
    return {"message": "Hello World"}