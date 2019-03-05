from microcosm_flask.swagger.parameters.decorated import SWAGGER_FORMAT, SWAGGER_TYPE


def swagger_field(swagger_type="string", swagger_format=None):
    """
    Decorator for an existing field type to coerce a specific swagger type/format.

    Usage:

        class MySchema(Schema):
             myfield = swagger_field(swagger_type="string")(fields.Foo())

    """
    def decorator(field):
        setattr(field, SWAGGER_TYPE, swagger_type)
        setattr(field, SWAGGER_FORMAT, swagger_format)
        return field

    return decorator
