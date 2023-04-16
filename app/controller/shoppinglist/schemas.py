from marshmallow import fields, Schema, EXCLUDE


class AddItemByName(Schema):
    name = fields.String(
        required=True
    )
    description = fields.String()


class AddRecipeItems(Schema):
    class RecipeItem(Schema):
        class Meta:
            unknown = EXCLUDE
        id = fields.Integer(required=True)
        name = fields.String(
            required=True,
            validate=lambda a: a and not a.isspace()
        )
        description = fields.String(
            load_default=''
        )
        optional = fields.Boolean(
            load_default=True
        )

    items = fields.List(fields.Nested(RecipeItem))


class CreateList(Schema):
    name = fields.String(
        required=True,
        validate=lambda a: a and not a.isspace()
    )


class UpdateList(Schema):
    name = fields.String(
        validate=lambda a: a and not a.isspace()
    )


class GetItems(Schema):
    orderby = fields.Integer()


class GetRecentItems(Schema):
    limit = fields.Integer(
        load_default=9,
        validate=lambda x: x > 0 and x <= 60
    )


class UpdateDescription(Schema):
    description = fields.String(
        required=True
    )

    # def validate_id(self, args):
    #     if not ShoppinglistItem.find_by_ids(args['id'], args['item_id']):
    #         raise ValidationError('Item does not exist')


class RemoveItem(Schema):
    item_id = fields.Integer(
        required=True,
    )
    removed_at = fields.Integer()

    # def validate_id(self, args):
    #     if not ShoppinglistItem.find_by_id(args['id'], args['item_id']):
    #         raise ValidationError('Item does not exist')
