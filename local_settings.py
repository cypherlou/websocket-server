import os
import uuid

env = {
    "SESSION_KEY": str(uuid.uuid4()),
    "SMTP_RELAY": "localhost",
    "LOG_FORMAT": "%(name)s %(funcName)-20s:%(lineno)-4d %(relativeCreated)-8d %(levelname)s - %(message)s",
    # Enable Mongo DB connection
    "ENABLE_MONOGODB": False,
    "MONGODB_HOST": "localhost",
    "MONGODB_DATABASE": "test",
    "MONGODB_REPLICA_SET": None,
    # Enable Celery component
    "ENABLE_CELERY": False,
    "CELERY_REDIS_DB": "3",
    "CELERY_TASK_RESULT_EXPIRES": 3600,
    "CELERY_DEFAULT_QUEUE": "gwss",
    "CELERY_VISIBILITY_TIMEOUT": 2592000,
    "CELERYD_STATE_DB": "gwss_celery_services.db",
    # Sentry DSN
    "SENTRY_DSN": "https://f0e7ef9882c147bbaa68b84e2d27f269@sentry.textmy.com/3",
    # Enable Redis component
    "ENABLE_REDIS": False,
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB": 3,
    # Websocket Server
    "SOCKETIO_CORS_ALLOWED_ORIGINS": "https://dev.hyphabit.io, https://api-dev.hyphabit.io, https://hyphabit.io",
    "SOCKETIO_ENGINEIO_LOGGER": False,
    # Misc
    "MIME_MAPPING": {
        "js": "text/javascript",
        "html": "text/html",
        "css": "text/css",
    },
    'STATIC_FOLDER': os.path.dirname( os.path.realpath( __file__ ) ) + "/static/"
}

# if env['ENABLE_CELERY']:
#     env.update( {
#         'CELERY_BACKEND': 'redis://{}:{}/{}'.format( env['REDIS_HOST'], env['REDIS_PORT'], env['CELERY_REDIS_DB'] ),
#         'CELERY_BROKER': 'redis://{}:{}/{}'.format(env['REDIS_HOST'], env['REDIS_PORT'], env['CELERY_REDIS_DB'] ),
#     } )
