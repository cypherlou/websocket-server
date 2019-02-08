import gwsslib
class Stuff( gwsslib.GwssObject ):

    def slinky( self, payload ):
        self.log.debug( 'Stuff.slinky payload: {}'.format( payload ) )
        return { 'success': True }
