import pprint
import os
import sys
import importlib
import traceback

dir_path = os.path.dirname( os.path.realpath( __file__ ) )
sys.path.append( dir_path )

class Commands( object ):

        def __init__( self, logger ):
            self.log = logger
            self.modules = []
            self.modules_by_name = {}

            for file in os.listdir( dir_path ):
                if file == '__init__.py': continue
                full_path = os.path.join( dir_path, file )
                
                if file.endswith(".py"):
                    file = file.split( '.' )[0]
                    core_module = importlib.import_module( file )
                    instantiated = getattr( core_module, file.title() )( logger= self.log )
                    self.modules.append( { 'module_location': full_path, 'module': instantiated, 'module_name': file } )
                    self.modules_by_name[file] = { 'module_location': full_path, 'module': instantiated, 'module_name': file }

            for f in self.functions_list():
                self.log.debug( f )

        """
          Format the various functions into a string so they can be dumped out nicely if necessary.
        """
        def functions_list( self ):
            a = []
            for m in self.modules_by_name:
                s = "{}: ".format( m )
                cs = []

                for c in dir( self.modules_by_name[m]['module'] ):
                    if c[:2] == "__": continue
                    if c == 'log': continue
                    cs.append( c )
                s += ', '.join( cs )
                a.append( s )
            return a

        def run( self, function, payload ):
            func = None
            response = { 'success': False, 'request': function }

            if '.' in function:
                module, subfunction = function.split( '.' )
                endpoint = subfunction
                func = self._module_by_name( module, subfunction, payload )

            if not func:
                endpoint = function
                func = self._module_sequential_search( function, payload )
            
            if not func:
                response = { 'success': False, 'reason': "Can't find function '{}'".format( function ), 'detail': 'None of the loaded classes contain this method' }

            else:
                self.log.debug( "running function '{}'".format( function ) )
                try:
                    response.update( func( payload ) )

                except Exception as e:
                    self.log.error( 'failed to call {}: {}'.format( function, e ) )
                    self.log.error( traceback.format_exc() )
                    response = { 'success': False, 'reason': "Failed to execute {}".format( function ), 'detail': str( e ) }

            response['endpoint'] = endpoint
            return response

        def _module_by_name( self, module, function, payload ):
            self.log.debug( "looking for function '{}' in module '{}'".format( function, module ) )
            func = None
            if module in self.modules_by_name:
                m = self.modules_by_name[module]
                self.log.debug( "checking {}".format( m['module_name'] ) )
                try:
                    self.log.debug( "finding function '{}'".format( function ) )
                    func = getattr( m['module'], function )

                except Exception as e:
                    self.log.debug( 'failed to find {}: {}'.format( function, e ) )
                    
            return func
                
        def _module_sequential_search( self, function, payload ):
            self.log.debug( "searching modules for {}".format( function ) )
            func = None
            for m in self.modules:
                self.log.debug( "checking {}".format( m['module_name'] ) )
                try:
                    self.log.debug( "finding function '{}'".format( function ) )
                    func = getattr( m['module'], function )

                except Exception as e:
                    self.log.debug( 'failed to find {}: {}'.format( function, e ) )
                    
            return func
        
        def missing_function( self, payload ):
            self.log.warn( "payload missing 'request'." )
            return {
                'reason': 'request missing from payload - no function executed'
            }

        def stub( self, payload ):
            self.log.info( "running stub processing" )
            self.log.debug( pprint.pformat( payload ) )
            return {
                'success': True
            }

class GwssObject( object ):

        def __init__( self, logger ):
            self.log = logger
