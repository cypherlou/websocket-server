import pprint
import random
import string

class Core( object ):

    def __init__( self, logger ):
        self.log = logger

    def test( self ):
        print( "test called" )
            
    def missing_command( self, payload ):
        self.log.warn( "payload missing 'request'." )
        return {
            'reason': 'request missing from payload - no command executed'
        }

    def stub( self, payload ):
        self.log.info( "running stub processing" )
        self.log.debug( pprint.pformat( payload ) )
        return {
            'success': True
        }

    def random_numbers( self, payload ):
        self.log.info( "running random_numbers processing with payload of {}".format( payload ) )
        return { 'numbers': ''.join( random.choice( string.digits ) for _ in range( 0, int( payload.get( 'length', '20' ) ) ) ) }

    def random_string( self, payload ):
        self.log.info( "running random_string processing with payload of {}".format( payload ) )
        return { 'string': ''.join( random.choice( string.ascii_letters ) for _ in range( 0, int( payload.get( 'length', '20' ) ) ) ) }
