from app.service.export_import import importFromDict, importFromLanguage
from .schemas import ImportSchema
from app.helpers import validate_args, authorizeFor
from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required

importBP = Blueprint('import', __name__)


@importBP.route('', methods=['POST'])
@jwt_required()
@validate_args(ImportSchema)
def importData(args, household_id):
    importFromDict(args)
    return jsonify({'msg': 'DONE'})


@importBP.route('/<lang>', methods=['GET'])
@jwt_required()
def importLang(household_id, lang):
    importFromLanguage(lang)
    return jsonify({'msg': 'DONE'})
