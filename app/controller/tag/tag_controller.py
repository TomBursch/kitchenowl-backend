from app.helpers import validate_args, authorizeFor
from flask import jsonify, Blueprint
from app.errors import NotFoundRequest
from flask_jwt_extended import jwt_required
from app.models import Tag, RecipeTags, Recipe
from .schemas import SearchByNameRequest, AddTag, UpdateTag

tag = Blueprint('tag', __name__)
tagHousehold = Blueprint('tag', __name__)


@tagHousehold.route('', methods=['GET'])
@jwt_required()
def getAllTags(household_id):
    return jsonify([e.obj_to_dict() for e in Tag.all_from_household_by_name(household_id)])


@tag.route('/<int:id>', methods=['GET'])
@jwt_required()
def getTag(id):
    tag = Tag.find_by_id(id)
    if not tag:
        raise NotFoundRequest()
    return jsonify(tag.obj_to_dict())


@tag.route('/<int:id>/recipes', methods=['GET'])
@jwt_required()
def getTagRecipes(id):
    tags = RecipeTags.query.filter(
        RecipeTags.tag_id == id).join(
        RecipeTags.recipe).order_by(
        Recipe.name).all()
    return jsonify([e.recipe.obj_to_dict() for e in tags])


@tagHousehold.route('', methods=['POST'])
@jwt_required()
@validate_args(AddTag)
def addTag(args, household_id):
    tag = Tag()
    tag.name = args['name']
    tag.household_id = household_id
    tag.save()
    return jsonify(tag.obj_to_dict())


@tag.route('/<int:id>', methods=['POST'])
@jwt_required()
@validate_args(UpdateTag)
def updateTag(args, id):
    tag = Tag.find_by_id(id)
    if not tag:
        raise NotFoundRequest()

    if 'name' in args:
        tag.name = args['name']

    tag.save()
    return jsonify(tag.obj_to_dict())


@tag.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteTagById(id):
    Tag.delete_by_id(id)
    return jsonify({'msg': 'DONE'})
