def generate_prompt(food_type, ingredients, cuisine):
    return f"""As a professional chef give me the best recipe within the category of {food_type} food,
    the type of cooking is {cuisine}, with the following ingredients: {ingredients}. give me tips
    and tricks to get the best result, give me the recipe with the least amount of words possible."""


def change_object_id_to_string(db_objects):
    for item in db_objects:
        item["id"] = str(item["id"])
        item.pop("_id")
        if "user_id" in item:
            item["user_id"] = str(item["user_id"])
    return db_objects