from app.helpers import validate_args, authorizeFor, AccessType
from flask import jsonify, Blueprint
from app.errors import NotFoundRequest, UnauthorizedRequest
from flask_jwt_extended import jwt_required
from app.models import Category
from .schemas import AddCategory, DeleteCategory, UpdateCategory

category = Blueprint('category', __name__)


@category.route('', methods=['GET'])
@jwt_required()
def getAllCategories():
    return jsonify([e.obj_to_dict() for e in Category.all_by_ordering()])


@category.route('/<int:id>', methods=['GET'])
@jwt_required()
def getCategory(id):
    category = Category.find_by_id(id)
    if not category:
        raise NotFoundRequest()
    return jsonify(category.obj_to_dict())


@category.route('', methods=['POST'])
@jwt_required()
@validate_args(AddCategory)
def addCategory(args):
    category = Category()
    category.name = args['name']
    category.save()
    return jsonify(category.obj_to_dict())


@category.route('/<int:id>', methods=['POST', 'PATCH'])
@jwt_required()
@validate_args(UpdateCategory)
def updateCategory(args, id):
    category = Category.find_by_id(id)
    if not category:
        raise NotFoundRequest()

    if 'name' in args:
        category.name = args['name']
    if 'ordering' in args and category.ordering != args['ordering']:
        category.reorder(args['ordering'])
    category.save()
    return jsonify(category.obj_to_dict())


@category.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteCategoryById(id):
    Category.delete_by_id(id)
    return jsonify({'msg': 'DONE'})


@category.route('', methods=['DELETE'])
@jwt_required()
@validate_args(DeleteCategory)
def deleteCategoryByName(args):
    if "name" in args:
        category = Category.find_by_name(args['name'])
        if category:
            category.delete()
            return jsonify({'msg': 'DONE'})
    raise NotFoundRequest()
