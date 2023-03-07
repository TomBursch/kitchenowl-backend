from app.helpers import validate_args, authorizeFor
from flask import jsonify, Blueprint
from app.errors import NotFoundRequest
from flask_jwt_extended import jwt_required
from app.models import Household
from .schemas import AddHousehold, UpdateHousehold

household = Blueprint('household', __name__)


@household.route('', methods=['GET'])
@jwt_required()
def getUserHouseholds():
    return jsonify([e.obj_to_dict() for e in Household.all()])


@household.route('/<int:household_id>', methods=['GET'])
@jwt_required()
def getHousehold(id):
    household = Household.find_by_id(id)
    if not household:
        raise NotFoundRequest()
    return jsonify(household.obj_to_dict())


@household.route('', methods=['POST'])
@jwt_required()
@validate_args(AddHousehold)
def addHousehold(args):
    household = Household()
    household.name = args['name']
    household.save()
    return jsonify(household.obj_to_dict())


@household.route('/<int:household_id>', methods=['POST'])
@jwt_required()
@validate_args(UpdateHousehold)
def updateHousehold(args, id):
    household = Household.find_by_id(id)
    if not household:
        raise NotFoundRequest()

    if 'name' in args:
        household.name = args['name']
    household.save()
    return jsonify(household.obj_to_dict())


@household.route('/<int:household_id>', methods=['DELETE'])
@jwt_required()
def deleteHouseholdById(id):
    Household.delete_by_id(id)
    return jsonify({'msg': 'DONE'})
