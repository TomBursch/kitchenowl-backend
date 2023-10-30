from app.models import Recipe, RecipeHistory
from app import app, db
import datetime

from app.models.recipe_history import Status

# minimum hours on planner until a recipe is considered to have been cooked
MEAL_THRESHOLD = 3


def findMealInstancesFromHistory(household_id: int):
    return findMealInstances(
        RecipeHistory.query.filter(RecipeHistory.status == Status.ADDED, RecipeHistory.household_id == household_id).all(),
        RecipeHistory.query.filter(RecipeHistory.status == Status.DROPPED, RecipeHistory.household_id == household_id).all())


def findMealInstances(added, dropped):
    # pointers for added and dropped recipes
    # both lists are marched through together in chronological order
    added_pointer = 0
    dropped_pointer = 0
    # key:recipe_id, value:created_at
    added_recipes = dict()
    dropped_recipes = dict()
    
    # meals that are considered to have been cooked
    meals = list()

    while added_pointer < len(added) and dropped_pointer < len(dropped):
        # add the currently added recipe to the dict added_recipes if it has not yet been dropped
        current_added = added[added_pointer]
        if (current_added.recipe_id in dropped_recipes and dropped_recipes[current_added.recipe_id] - current_added.created_at < 0):
            added_recipes[current_added.recipe_id] = current_added.created_at
        added_pointer += 1

        # look for whether the current dropped recipe has yet been added
        current_dropped = dropped[dropped_pointer]
        while (current_dropped.recipe_id in added_recipes):
            # compute duration while recipe on the planner
            added_time = added_recipes[current_dropped.recipe_id]
            dropped_time = current_dropped.created_at
            # if duration threshold is met, consider it as a cooked meal
            if (dropped_time - added_time >=
                    datetime.timedelta(hours=MEAL_THRESHOLD)):
                meal = {
                    "recipe_id": current_dropped.recipe_id,
                    "cooked_at": dropped_time}
                meals.append(meal)

            # proceed to next dropped recipe
            added_recipes.pop(current_dropped.recipe_id)
            dropped_recipes[current_dropped.recipe_id] = current_dropped.created_at
            
            dropped_pointer += 1
            # break if no more dropped recipes
            if not (dropped_pointer < len(dropped)):
                break
            current_dropped = dropped[dropped_pointer]
    app.logger.info("meal instances are identified")
    return meals


def computeRecipeSuggestions(household_id: int):
    meal_instances = findMealInstancesFromHistory(household_id)
    # group meals by their id
    meal_hist = dict()
    for m in meal_instances:
        id = m["recipe_id"]
        if id not in meal_hist:
            meal_hist[id] = []
        meal_hist[id].append(m["cooked_at"])

    # 0) reset all suggestion scores
    for r in Recipe.all_from_household(household_id):
        r.suggestion_score = 0
        db.session.add(r)

    # 1) count cooked instances in last six months
    six_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=182)
    for id in meal_hist:
        cooking_count = 0
        for cooked in meal_hist[id]:
            if cooked > six_months_ago:
                cooking_count += 1
        # set suggestion_score to cooking_count
        r = Recipe.find_by_id(id)
        r.suggestion_score = cooking_count
        db.session.add(r)

    # 2) do not suggest recent meals
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    # find recently cooked meals
    for id in meal_hist:
        for cooked in meal_hist[id]:
            if cooked > week_ago:
                r = Recipe.find_by_id(id)
                r.suggestion_score = 0
                db.session.add(r)

    # commit changes to db
    db.session.commit()
    app.logger.info("computed and stored new suggestion scores")
