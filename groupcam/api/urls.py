from groupcam.api import handlers


urls = (
    (r'/cameras',
     handlers.CamerasHandler, {}, 'cameras'),
    (r'/cameras/(?P<camera_id>\S+)/presets',
     handlers.PresetsHandler, {}, 'presets'),
    (r'/users',
     handlers.UsersHandler, {}, 'users'),
)
