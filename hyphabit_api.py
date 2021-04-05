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
from flask import Flask, request, render_template, send_from_directory, redirect
import flask_socketio
import datetime
import traceback
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import local_settings
import gwsslib

if local_settings.env.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=local_settings.env["SENTRY_DSN"], integrations=[FlaskIntegration()]
    )


app = Flask(str(local_settings.env.get("APPLICATION_NAME")))
app.secret_key = str(local_settings.env.get("SESSION_KEY"))
app.config["TEMPLATES_AUTO_RELOAD"] = True

log = logging.getLogger(app.logger.name)
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(
    address="/dev/log", facility=logging.handlers.SysLogHandler.LOG_USER
)
handler.setFormatter(logging.Formatter(str(local_settings.env["LOG_FORMAT"])))
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

# Redis Database connection
__redis = None
if local_settings.env.get("ENABLE_REDIS"):
    import redis

    __redis = redis.StrictRedis(
        host=str(local_settings.env["REDIS_HOST"]),
        port=int(str(local_settings.env["REDIS_PORT"])),
        db=int(str(local_settings.env["REDIS_DB"])),
    )
    app.logger.debug("Redis database enabled")

# Celery stuff
__celery = None
if local_settings.env.get("ENABLE_CELERY"):
    import celery
    from kombu import Queue, Exchange

    __celery = celery.Celery(
        "services",
        broker=local_settings.env.get("CELERY_BROKER"),
        backend=local_settings.env.get("CELERY_BROKER"),
    )
    __celery.conf.update(
        CELERY_DEFAULT_QUEUE=local_settings.env.get("CELERY_DEFAULT_QUEUE"),
        CELERY_TASK_RESULT_EXPIRES=local_settings.env.get("CELERY_TASK_RESULT_EXPIRES"),
        CELERYD_STATE_DB=local_settings.env.get("CELERYD_STATE_DB"),
        CELERY_DISABLE_RATE_LIMITS=True,
        CELERY_REDIRECT_STDOUTS=True,
        CELERY_REDIRECT_STDOUTS_LEVEL="DEBUG",
        CELERYD_LOG_COLOR=False,
        CELERY_QUEUES=(
            Queue(
                local_settings.env.get("CELERY_DEFAULT_QUEUE"),
                Exchange(local_settings.env.get("CELERY_DEFAULT_QUEUE")),
                routing_key=local_settings.env.get("CELERY_DEFAULT_QUEUE"),
            ),
        ),
        BROKER_TRANSPORT_OPTIONS={
            "visibility_timeout": local_settings.env.get("CELERY_VISIBILITY_TIMEOUT")
        },
    )
    app.logger.debug("Celery client enabled")

# SocketIO Wrapper
caos = (
    str(local_settings.env.get("SOCKETIO_CORS_ALLOWED_ORIGINS", ""))
    .replace(" ", "")
    .split(",")
)
socketio = flask_socketio.SocketIO(
    app,
    manage_session=False,
    # Uncomment to get the engineio to log. Only for 'proper' debugging!
    # engineio_logger=app.logger,
    async_mode="gevent",
    cors_allowed_origins=caos,
    logger=app.logger,
)


# Database connection
if local_settings.env.get("ENABLE_MONGODB"):
    import pymongo

    client = pymongo.MongoClient(
        local_settings.env.get("MONGODB_HOST"),
        replicaset=local_settings.env.get("MONGODB_REPLICA_SET"),
        connect=False,
    )
    __db = client[local_settings.env.get("MONGODB_DATABASE")]
    app.logger.debug("Mongo database enabled")


__commands = gwsslib.Commands(logger=log)


def authenticated(f):
    """
    Use on functions that can only be run if the user has a valid session.
    """

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
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
        app.logger.debug("** authenticated - session valid")
        return f(*args, **kwargs)

    return wrapped


# authentication routines
def valid_session(record_event=True):
    # do session validation here and return True or False
    return False


#
def logged_out_socket_wrapper(*args, **kwargs):
    app.logger.warn(
        "** authenticated - user logged out, sending response to command channel"
    )
    flask_socketio.emit(
        "global/resp_connection_control_channel",
        {"success": False, "logged_out": True, "url": "/expired"},
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Websocket routines
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# websocket interaction - show connection and disconnection of the websocket for debug purposes
@socketio.on_error()
def error_handler(e):
    app.logger.error(e)
    app.logger.error(traceback.format_exc())


@socketio.on("connect")
def connect():
    app.logger.debug("websocket connection from %s" % request.sid)
    # flask_socketio.emit( 'gwss_response', { 'success': True, 'id': flask.request.sid, 'response': 'connection' } )


@socketio.on("disconnect")
# @flask_login.login_required
def disconnect():
    app.logger.debug("socket %s disconnected" % request.sid)


# @socketio.on( 'json' )
# def json( payload ):
#     app.logger.debug( "on.json({})".format( pprint.pformat( payload ) ) )


@socketio.on("message")
def message(*args):
    app.logger.debug("on.message({})".format(pprint.pformat(args)))

    request, payload = args
    app.logger.debug(pprint.pformat(payload))
    function_name = payload.get("request", "missing_command")
    response = {}

    response.update(__commands.run(function=function_name, payload=payload["data"]))
    reply_to = payload.get("return_route", "general")
    app.logger.debug("emit( {}, {} )".format(reply_to, response))
    flask_socketio.emit(reply_to, response)
    return {"ff": 100, "d": True}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HTTP routines
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ERROR HANDLING
@app.errorhandler(500)
def internal_500_error(exception):
    app.logger.exception(exception)
    return pprint.pformat(exception), 500, {"Content-Type": "text/plain"}


@app.errorhandler(404)
def internal_404_error(exception):
    app.logger.debug("-" * 40)
    app.logger.warn(request.url)
    app.logger.warn(exception)
    app.logger.debug("-" * 40)
    return (
        "dashboard\n%s\n%s" % (pprint.pformat(exception), request.url),
        404,
        {"Content-Type": "text/plain"},
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PAGE MAPPED ROUTES


@app.route("/expired", methods=["GET"])
def expired():

    # make sure the session is logged out/cleared
    user = valid_session()
    if user:
        app.logger.debug("user session expired %s" % user.username)
        user.logout()
    # return the "expired" page
    return render_template("expired.html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# STATIC ROUTES
@app.route("/static/<directory>/<file_name>.<file_type>", methods=["GET"])
def static_file(directory, file_name, file_type):

    app.logger.debug(
        "sending static file: [%s] %s.%s" % (directory, file_name, file_type)
    )
    return send_from_directory(
        local_settings.env["STATIC_FOLDER"] + "/" + directory,
        "%s.%s" % (file_name, file_type),
    ), {
        "Content-Type": local_settings.env["MIME_MAPPING"].get(
            file_type, "application/octet-stream"
        )
    }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route("/logout", methods=["GET"])
@authenticated
def logout():

    user = valid_session()
    if user:
        if user.valid:
            app.logger.debug("user %s requesting logout" % user.username)
            user.logout()

    return redirect("/")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")
