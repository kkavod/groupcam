import colander


class Camera(colander.MappingSchema):
    id = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    nickname = colander.SchemaNode(colander.String())
    regexp = colander.SchemaNode(colander.String())
