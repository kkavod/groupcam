from groupcam.api import handlers


urls = (
    (r'/cameras', handlers.CamerasHandler, {}, 'cameras'),
    (r'/users', handlers.UsersHandler, {}, 'users'),
)
