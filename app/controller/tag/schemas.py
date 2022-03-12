from marshmallow import fields, Schema


class SearchByNameRequest(Schema):
    query = fields.String(
        required=True,
        validate=lambda a: len(a) > 0
    )


class AddTag(Schema):
    name = fields.String(
        required=True
    )