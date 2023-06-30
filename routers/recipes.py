from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List
from food_api.database.models import Cuisine, Ingredient, FoodType
from food_api.routers.auth import admin_only, get_current_user, oauth2_scheme
from food_api.utils import change_object_id_to_string

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)


async def get_ingredients_db(request: Request):
    ingredients_collection = request.app.mongodb["ingredients"]
    ingredients = await ingredients_collection.find().to_list(length=100)
    return [ingredient["name"] for ingredient in ingredients]


async def get_cuisines_db(request: Request):
    cuisines_collection = request.app.mongodb["cuisines"]
    cuisines = await cuisines_collection.find().to_list(length=100)
    return [cuisine["name"] for cuisine in cuisines]


async def get_food_type_db(request: Request):
    food_type_collection = request.app.mongodb["food_type"]
    food_type = await food_type_collection.find().to_list(length=100)
    return [category["name"] for category in food_type]


@router.get("/ingredients")
async def get_ingredients(request: Request, token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    return JSONResponse({"ingredients": await get_ingredients_db(request)})


@router.get("/category")
async def get_category(request: Request, token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    return JSONResponse(
        {
            "category": await get_food_type_db(request),
        }
    )


@router.get("/cuisines")
async def get_cuisines(request: Request, token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    return JSONResponse(
        {
            "cuisines": await get_cuisines_db(request),
        }
    )


@router.post("/add-ingredients")
@admin_only()
async def add_ingredients(request: Request, ingredients: List[str]):
    ingredients_collection = request.app.mongodb["ingredients"]
    ingredients_data = [Ingredient(name=ingredient.capitalize()).dict() for ingredient in ingredients]
    await ingredients_collection.insert_many(ingredients_data)
    return JSONResponse(
        {"message": f"{len(ingredients_data)} Ingredients added successfully"}
    )


@router.post("/add-cuisines")
@admin_only()
async def add_cuisines(request: Request, cuisines: List[str]):
    cuisines_collection = request.app.mongodb["cuisines"]
    cuisines_data = [Cuisine(name=cuisine.capitalize()).dict() for cuisine in cuisines]
    await cuisines_collection.insert_many(cuisines_data)
    return JSONResponse(
        {"message": f"{len(cuisines_data)} Cuisines added successfully"}
    )


@router.post("/add-food_type")
@admin_only()
async def add_food_type(request: Request, food_type: List[str]):
    food_type_collection = request.app.mongodb["food_type"]
    food_type_data = [FoodType(name=category.capitalize()).dict() for category in food_type]
    await food_type_collection.insert_many(food_type_data)
    return JSONResponse(
        {"message": f"{len(food_type_data)} food_type added successfully"}
    )

# get my recipes
@router.get("/my-recipes")
async def get_my_recipes(request: Request, token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    recipes_collection = request.app.mongodb["recipes"]
    # find recipes by user_id, user_id should be a bson object
    recipes = await recipes_collection.find({"user_id": ObjectId(user["id"])}).to_list(length=100)
    recipes_response = change_object_id_to_string(recipes)
    return JSONResponse(
        {
            "recipes": recipes_response,
        }
    )