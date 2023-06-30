import os
from dotenv import load_dotenv
from fastapi import FastAPI
from food_api.database.database import get_mongo_client
from food_api.routers import recipes, food_gpt, auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(debug=True)
load_dotenv()

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(food_gpt.router)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8015",
    # Add more allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add db object to the request state
@app.on_event("startup")
async def startup():
    mongo_client = get_mongo_client()
    app.mongodb = mongo_client[os.getenv("MONGO_DB")]
    # check connection and print ok or fail
    try:
        await app.mongodb.command("ping")
        print("MongoDB connection: OK")
    except Exception as e:
        print(e)



# add db object to the request state
@app.on_event("shutdown")
async def shutdown():
    app.mongodb = None


if __name__ == "__main__":
    uvicorn.run("food_api.app.main:app", host="localhost", port=8000, reload=True)
