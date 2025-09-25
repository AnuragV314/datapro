from fastapi import FastAPI

app = FastAPI()

@app.get("/articles/")
def get_articles():
    # Fetch from DBs
    return {"message": "Articles fetched"}