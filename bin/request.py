#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Usage:
        request.py --help
        request.py 


Options:
        --start=start-date                              specify a start date for billing YYYY-MM-DD
        --end=end-date                                  specify an end date for billing YYYY-MM-DD
        --last-month                                    standard billing mode, i.e. bill for last month
        --email=recipient                               override the default destination of accounts@destar.co.uk
        --smpt-relay=<relay>                            set the SMTP relay to use [default: email01].
        --xero                                          use Xero API

"""
import docopt
import logging
import coloredlogs
import socketIO_client
import base64

import json
import socket

logger = logging.getLogger( __name__ )

def on_connect( ):
    logger.debug( "on_connect" )

def on_error(  ):
    logger.debug( "on_error:", error )

def on_disconnect(  ):
    logger.debug( "on_disconnect" )
    
def on_reconnect(  ):
    logger.debug( "on_reconnect" )

def on_response( args ):
    print( 'on_response (gwss_response)', args )

if __name__ == '__main__':
    opts = docopt.docopt( __doc__, version='GWSS Client v1.0' )
    delay = 2
    
    logger.setLevel( logging.DEBUG )
    # handler = logging.handlers.SysLogHandler( address = '/dev/log', facility=logging.handlers.SysLogHandler.LOG_USER )
    # handler.setLevel( logging.DEBUG )
    # logger.addHandler( handler )
    coloredlogs.install( level='DEBUG' )
    logger.info( "running websocket client" )    

    command = {
        "request": "slinky",
        "data": {
                    "item1": 100,
                    "item2": "bubble",
                    "item3": "bobble",
                    "item4": -1,
                },

    }
    
    ws = socketIO_client.SocketIO( 'localhost', 8080, socketIO_client.LoggingNamespace )
    logger.debug( "assigning event triggers" )
    ws.on( 'connect', on_connect )
    ws.on( 'error', on_error )
    ws.on( 'disconnect', on_disconnect )
    ws.on( 'reconnect', on_reconnect )
    ws.on( 'gwss_response', on_response )
    logger.debug( "sending gwss_request" )
    ws.emit( 'gwss_request', command )
    
    ws.wait( seconds = 1 )
    command.update( { "request": "stuff.slinky" } )
    command['data'].update( { 'peddles': 100 } )
    ws.emit( 'gwss_request', command )
    logger.info( "waiting {} seconds to exit".format( delay ) )
    ws.wait( seconds = delay )
            
