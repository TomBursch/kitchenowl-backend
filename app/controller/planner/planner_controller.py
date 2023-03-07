from app.errors import NotFoundRequest
from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required
from app import db
from app.helpers import validate_args, authorizeFor
from app.models import Recipe, RecipeHistory, Planner
from .schemas import AddPlannedRecipe, RemovePlannedRecipe

planner = Blueprint('planner', __name__)


@planner.route('/recipes', methods=['GET'])
@jwt_required()
def getAllPlannedRecipes():
    plannedRecipes = db.session.query(Planner.recipe_id).group_by(
        Planner.recipe_id).scalar_subquery()
    recipes = Recipe.query.filter(Recipe.id.in_(
        plannedRecipes)).order_by(Recipe.name).all()
    return jsonify([e.obj_to_full_dict() for e in recipes])


@planner.route('/', methods=['GET'])
@jwt_required()
def getPlanner():
    plans = Planner.query.all()
    return jsonify([e.obj_to_full_dict() for e in plans])


@planner.route('/recipe', methods=['POST'])
@jwt_required()
@validate_args(AddPlannedRecipe)
def addPlannedRecipe(args):
    recipe = Recipe.find_by_id(args['recipe_id'])
    if not recipe:
        raise NotFoundRequest()
    day = args['day'] if 'day' in args else -1
    planner = Planner.find_by_day(recipe_id=recipe.id, day=day)
    if not planner:
        if day >= 0:
            old = Planner.find_by_day(recipe_id=recipe.id, day=-1)
            if old: old.delete()
        elif len(recipe.plans) > 0:
            return jsonify(recipe.obj_to_dict())
        planner = Planner()
        planner.recipe_id = recipe.id
        planner.day = day
        if 'yields' in args:
            planner.yields = args['yields']
        planner.save()

        RecipeHistory.create_added(recipe)

    return jsonify(recipe.obj_to_dict())


@planner.route('/recipe/<int:id>', methods=['DELETE'])
@jwt_required()
@validate_args(RemovePlannedRecipe)
def removePlannedRecipeById(args, id):
    recipe = Recipe.find_by_id(id)
    if not recipe:
        raise NotFoundRequest()
    
    day = args['day'] if 'day' in args else -1
    planner = Planner.find_by_day(recipe_id=recipe.id, day=day)
    if planner:
        planner.delete()
        RecipeHistory.create_dropped(recipe)
    return jsonify(recipe.obj_to_dict())


@planner.route('/recent-recipes', methods=['GET'])
@jwt_required()
def getRecentRecipes():
    recipes = RecipeHistory.get_recent()
    return jsonify([e.recipe.obj_to_full_dict() for e in recipes])


@planner.route('/suggested-recipes', methods=['GET'])
@jwt_required()
def getSuggestedRecipes():
    # all suggestions
    suggested_recipes = Recipe.find_suggestions()
    # remove recipes on recent list
    recents = [e.recipe.id for e in RecipeHistory.get_recent()]
    suggested_recipes = [s for s in suggested_recipes if s.id not in recents]
    # limit suggestions number to maximally 9
    if len(suggested_recipes) > 9:
        suggested_recipes = suggested_recipes[:9]
    return jsonify([r.obj_to_full_dict() for r in suggested_recipes])


@planner.route('/refresh-suggested-recipes', methods=['GET'])
@jwt_required()
def getRefreshedSuggestedRecipes():
    # re-compute suggestion ranking
    Recipe.compute_suggestion_ranking()
    # return suggested recipes
    return getSuggestedRecipes()
