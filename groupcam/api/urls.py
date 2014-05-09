from groupcam.api import handlers


urls = (
    (r'/cameras',
     handlers.CamerasHandler, {}, 'cameras'),
    (r'/cameras/(?P<camera_id>\S+)/presets',
     handlers.PresetsHandler, {}, 'presets'),
    (r'/cameras/(?P<camera_id>\S+)/presets/(?P<number>\d+)',
     handlers.PresetHandler, {}, 'preset'),
    (r'/users',
     handlers.UsersHandler, {}, 'users'),
)
