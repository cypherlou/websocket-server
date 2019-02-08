#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Usage:
        request.py --help
        request.py [--host=host] [--port=port]


Options:
        --host=host                                     Host [default: localhost]
        --port=port                                     Port number [default: 8080]

"""
import docopt
import logging
import coloredlogs
import socketIO_client
import pprint
import sys

import json
import socket

logger = logging.getLogger( __name__ )
opts = docopt.docopt( __doc__, version='GWSS Client v1.0' )
ws = socketIO_client.SocketIO( host=opts.get( '--host' ), port=int( opts.get( '--port' ) ) )

        
def on_response( data ):
    d = socketIO_client.parsers.parse_socketIO_packet_data( data )
    logger.debug( 'on_response ({}): {}'.format( d.args[0], d.args[1] ) )

if __name__ == '__main__':
    delay = 2
    
    logger.setLevel( logging.DEBUG )
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
    
    logger.debug( "assigning event triggers" )
    # ws.on( 'connect', on_connect )
    # ws.on( 'error', on_error )
    # ws.on( 'disconnect', on_disconnect )
    # ws.on( 'reconnect', on_reconnect )
    # ws.on( 'slinky', on_response )
    ws.on( 'message', on_response )

    logger.debug( "sending gwss_request" )
    ws.emit( 'gwss_request', command )
    ws.wait( seconds = 1 )

    c = 100
    while c < 110:
        command.update( { "request": "stuff.slinky" } )
        command['data'].update( { 'peddles': c } )
        ws.emit( 'gwss_request', command )
        c += 1
        
    logger.info( "waiting {} seconds to exit".format( delay ) )
    ws.wait( seconds = delay )
            
