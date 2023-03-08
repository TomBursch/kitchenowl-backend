from app.helpers import validate_args, authorizeFor
from flask import jsonify, Blueprint
from app.errors import InvalidUsage, NotFoundRequest
from flask_jwt_extended import jwt_required
from app.models import Item, RecipeItems, Recipe, Category
from .schemas import SearchByNameRequest, UpdateItem

item = Blueprint('item', __name__)
itemHousehold = Blueprint('item', __name__)

@itemHousehold.route('', methods=['GET'])
@jwt_required()
def getAllItems(household_id):
    return jsonify([e.obj_to_dict() for e in Item.all_by_name_with_filter(household_id)])


@item.route('/<int:id>', methods=['GET'])
@jwt_required()
def getItem(id):
    item = Item.find_by_id(id)
    if not item:
        raise NotFoundRequest()
    return jsonify(item.obj_to_dict())


@item.route('/<int:id>/recipes', methods=['GET'])
@jwt_required()
def getItemRecipes(id):
    items = RecipeItems.query.filter(
        RecipeItems.item_id == id, RecipeItems.optional == False).join(  # noqa
        RecipeItems.recipe).order_by(
        Recipe.name).all()
    return jsonify([e.obj_to_recipe_dict() for e in items])


@item.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteItemById(id):
    Item.delete_by_id(id)
    return jsonify({'msg': 'DONE'})


@itemHousehold.route('/search', methods=['GET'])
@jwt_required()
@validate_args(SearchByNameRequest)
def searchItemByName(args, household_id):
    return jsonify([e.obj_to_dict() for e in Item.search_name(args['query'], household_id)])


@item.route('/<int:id>', methods=['POST'])
@jwt_required()
@validate_args(UpdateItem)
def updateItem(args, id):
    item = Item.find_by_id(id)
    if not item:
        raise NotFoundRequest()
    if 'category' in args:
        if not args['category']:
            item.category = None
        elif 'id' in args['category']:
            item.category = Category.find_by_id(args['category']['id'])
        else:
            raise InvalidUsage()
    if 'icon' in args:
        item.icon = args['icon']
    item.save()
    return jsonify(item.obj_to_dict())
