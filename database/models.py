from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# mongodb model for ingredients
class Ingredient(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {"example": {"name": "Tomato"}}


# mongodb model for cuisines
class Cuisine(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {"example": {"name": "Italian"}}


# mongodb model for food types (breakfast, lunch, dinner, dessert)
class FoodType(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {"example": {"name": "Dinner"}}


# mongodb model for recipes (recipe text as a string, the recipes belong to a user and have a cuisine and food type)
class Recipe(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    text: str = Field(...)
    recipe_title: str = Field(...)
    user_id: PyObjectId = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "text": "This is a recipe",
                "user_id": "5f8f6d0a1c9d440000d8e9a1",
                "recipe_title": "Recipe Title",
            }
        }


# mongodb model for user
class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    role: str = Field(default="user")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johnd@gmail.com",
                "hashed_password": "Oerj$dfas432X",
            }
        }



# mongodb model for user sign up
class UserSignUp(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(
        ...,
        min_length=8,
        regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johnd@gmail.com",
                "password": "Oerj$dfas432X",
            }
        }

