import colander


class Preset(colander.MappingSchema):
    number = colander.SchemaNode(colander.Int(), validator=colander.Range(1))
    name = colander.SchemaNode(colander.String())
    type = colander.SchemaNode(colander.String())
    layout = colander.SchemaNode(colander.Mapping(unknown='preserve'))
    active = colander.SchemaNode(colander.Boolean())


class Presets(colander.SequenceSchema):
    preset = Preset()


class Camera(colander.MappingSchema):
    id = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    nickname = colander.SchemaNode(colander.String())
    regexp = colander.SchemaNode(colander.String())
