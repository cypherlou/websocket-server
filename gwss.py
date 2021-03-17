#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import logging
import functools
import pprint
import logging.handlers
import json
import syslog
from flask import Flask, request, render_template, send_from_directory
import flask_socketio
import datetime
import traceback

import local_settings
config = local_settings.env

import gwsslib
import gwsslib.stuff

app = Flask( config.get( 'APPLICATION_NAME', 'gwss' ) )
app.secret_key = config.get( 'SESSION_KEY' )
app.config['TEMPLATES_AUTO_RELOAD'] = True

log = logging.getLogger( app.logger.name )
log.setLevel( logging.DEBUG )
handler = logging.handlers.SysLogHandler( address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_USER )
handler.setFormatter( logging.Formatter( config['LOG_FORMAT'] ) )
handler.setLevel( logging.DEBUG )
app.logger.addHandler( handler )

# Redis Database connection
__redis = None
if config.get( 'ENABLE_REDIS' ):
    import redis
    __redis = redis.StrictRedis(
        host = config['REDIS_HOST'],
        port = config['REDIS_PORT'],
        db = config['REDIS_DB']
    )
    app.logger.debug( "Redis database enabled" )

# Celery stuff
__celery = None
if config.get( 'ENABLE_CELERY'):
    import celery
    from kombu import Queue, Exchange

    __celery = celery.Celery( 'services', broker=config.get('CELERY_BROKER'), backend=config.get('CELERY_BROKER') )
    __celery.conf.update(
        CELERY_DEFAULT_QUEUE = config.get('CELERY_DEFAULT_QUEUE'),
        CELERY_TASK_RESULT_EXPIRES = config.get('CELERY_TASK_RESULT_EXPIRES'),
        CELERYD_STATE_DB = config.get( 'CELERYD_STATE_DB' ),
        CELERY_DISABLE_RATE_LIMITS = True,
        CELERY_REDIRECT_STDOUTS = True,
        CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG',
        CELERYD_LOG_COLOR = False,
        CELERY_QUEUES = (
            Queue(
                config.get('CELERY_DEFAULT_QUEUE'),
                Exchange(config.get('CELERY_DEFAULT_QUEUE')),
                routing_key=config.get('CELERY_DEFAULT_QUEUE')),
        ),
        BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': config.get('CELERY_VISIBILITY_TIMEOUT') },
    )
    app.logger.debug( "Celery client enabled" )

# SocketIO Wrapper
caos = config.get( 'SOCKETIO_CORS_ALLOWED_ORIGINS', '' ).replace( ' ', '' )
caos = caos.split( ',' )
for cao in caos:
    app.logger.info( "adding {} to cors_allowed_origins".format( cao ) )

socketio = flask_socketio.SocketIO(
    app,
    manage_session = False,
    # Uncomment to get the engineio to log. Only for 'proper' debugging!
    # engineio_logger=app.logger,
    async_mode='gevent',
    cors_allowed_origins=caos,
    logger=app.logger,
)


# Logging
log_format = logging.Formatter( config['LOG_FORMAT'] )

# Database connection
if config.get( 'ENABLE_MONGODB' ):
    import pymongo
    client = pymongo.MongoClient( config.get( 'MONGODB_HOST' ), replicaset=config.get( 'MONGODB_REPLICA_SET' ), connect=False )
    __db = client[ config.get( 'MONGODB_DATABASE' ) ]
    app.logger.debug( "Mongo database enabled" )


__commands = gwsslib.Commands( logger = log )

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Use on functions that can only be run if the user has a valid session.
def authenticated( f ):
    @functools.wraps( f )
    def wrapped( *args, **kwargs ):
        """
Add session validation and chain to client - ignore for the time being
        app.logger.debug( "** authenticated - called to check session against '%s'" % f.func_name )
        if not valid_session( ):
            app.logger.debug( "** authenticated - failed to validate session" )
            if 'gwss_cmd' in f.func_name:
                return logged_out_socket_wrapper( *args, **kwargs )
            else:
                return flask.redirect( '/' )

        else:
            app.logger.debug( "** authenticated - session valid" )
            return f( *args, **kwargs )
        """
        app.logger.debug( "** authenticated - session valid" )
        return f( *args, **kwargs )

    return wrapped


# authentication routines
def valid_session( record_event=True ):
    # do session validation here and return True or False
    return False


# 
def logged_out_socket_wrapper( *args, **kwargs ):
    app.logger.warn( "** authenticated - user logged out, sending response to command channel" )
    flask_socketio.emit( 'global/resp_connection_control_channel', {
        'success': False,
        'logged_out': True,
        'url': '/expired'
    } )

    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Websocket routines
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# websocket interaction - show connection and disconnection of the websocket for debug purposes
@socketio.on_error()
def error_handler(e):
    app.logger.error( e )
    app.logger.error( traceback.format_exc() )

@socketio.on( 'connect' )
def connect():
    app.logger.debug( 'websocket connection from %s' % request.sid )
    # flask_socketio.emit( 'gwss_response', { 'success': True, 'id': flask.request.sid, 'response': 'connection' } )

@socketio.on( 'disconnect' )
# @flask_login.login_required
def disconnect():
    app.logger.debug( "socket %s disconnected" % request.sid )

# @socketio.on( 'json' )
# def json( payload ):
#     app.logger.debug( "on.json({})".format( pprint.pformat( payload ) ) )
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
{
    "request": "stub",
    "data": {
        "item1": 100,
        "item2": "bubble",
        "item3": "bobble",
        "item4": -1,
    },
    
}
"""
@socketio.on( 'message' )
def message( *args ):
    app.logger.debug( "on.message({})".format( pprint.pformat( args ) ) )

    request, payload = args
    app.logger.debug( pprint.pformat( payload ) )
    function_name = payload.get( 'request', 'missing_command' )
    response = { }

    response.update( __commands.run( function = function_name, payload = payload['data'] ) )
    reply_to = payload.get( 'return_route', 'general' )
    app.logger.debug( "emit( {}, {} )".format( reply_to, response ) )
    flask_socketio.emit( reply_to, response )
    return { 'ff': 100, 'd': True }

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HTTP routines
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ERROR HANDLING
@app.errorhandler( 500 )
def internal_500_error( exception ):
     app.logger.exception( exception )
     return pprint.pformat( exception ), 500, { 'Content-Type': 'text/plain' }


@app.errorhandler( 404 )
def internal_404_error( exception ):
    app.logger.debug( '-' * 40 )
    app.logger.warn( request.url )
    app.logger.warn( exception )
    app.logger.debug( '-' * 40 )
    return 'dashboard\n%s\n%s' % ( pprint.pformat( exception ), request.url ), 404, { 'Content-Type': 'text/plain' }


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PAGE MAPPED ROUTES

@app.route('/expired', methods=['GET'])
def expired():

    # make sure the session is logged out/cleared
    user = valid_session()
    if user:
        app.logger.debug( "user session expired %s" % user.username )
        user.logout()
    # return the "expired" page
    return render_template( 'expired.html' )


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# STATIC ROUTES
@app.route('/static/<directory>/<file_name>.<file_type>', methods=['GET'])
def static_file( directory, file_name, file_type):

    app.logger.debug( "sending static file: [%s] %s.%s" % ( directory, file_name, file_type ) )
    return send_from_directory(
        config['STATIC_FOLDER'] + "/" + directory,
        "%s.%s" % ( file_name, file_type )
    ), { 'Content-Type': config['MIME_MAPPING'].get( file_type, 'application/octet-stream' ) }


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/logout', methods=['GET'])
@authenticated
def logout():

    user = valid_session()
    if user:
        if user.valid:
            app.logger.debug( "user %s requesting logout" % user.username )
            user.logout()

    return flask.redirect( '/' )


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/', methods=['GET'])
def home():
    return render_template( "index.html" )
