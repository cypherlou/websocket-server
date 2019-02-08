import os
import uuid

env = {
    'HOME_DIR': os.path.dirname( os.path.realpath( __file__ ) ),
    'VIRTUALENV_DIR': os.path.dirname( os.path.realpath( __file__ ) ) +  "/env/lib/python2.7/site-packages",
    'SESSION_KEY': str( uuid.uuid4() ),
    'SMTP_RELAY': 'localhost',
    'LOG_FORMAT': "%(name)s %(funcName)-20s:%(lineno)-4d %(relativeCreated)-8d %(levelname)s - %(message)s",

    # Enable Mongo DB connection
    'ENABLE_MONOGODB': True,
    'MONGODB_HOST': 'localhost',
    'MONGODB_DATABASE': 'test',
    'MONGODB_REPLICA_SET': None,
    
    # Enable Celery component
    'ENABLE_CELERY': True,
    'CELERY_REDIS_DB': '3',
    'CELERY_TASK_RESULT_EXPIRES': 3600,
    'CELERY_DEFAULT_QUEUE': 'gwss',
    'CELERY_VISIBILITY_TIMEOUT': 2592000,
    'CELERYD_STATE_DB': 'gwss_celery_services.db',
    
    # Enable Redis component
    'ENABLE_REDIS': True,
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': 6379,
    'REDIS_DB': 3,
}

if env['ENABLE_CELERY']:
    env.update( {
        'CELERY_BACKEND': 'redis://{}:{}/{}'.format( env['REDIS_HOST'], env['REDIS_PORT'], env['CELERY_REDIS_DB'] ),
        'CELERY_BROKER': 'redis://{}:{}/{}'.format(env['REDIS_HOST'], env['REDIS_PORT'], env['CELERY_REDIS_DB'] ),
    } )
