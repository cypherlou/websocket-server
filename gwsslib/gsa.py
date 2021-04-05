import gwsslib
import pickle
import datetime
from typing import Dict, Any
import pprint
import codecs
from colour import Color

GLOBAL_SPECTRUM='data/global-spectrum-availability.p'
START_COLOR="#4fb3bf"
END_COLOR="#005662"

class Gsa(gwsslib.GwssObject):

    __gsa_data = pickle.load( open( GLOBAL_SPECTRUM, "rb" ) )


    def network_termination(self, payload):

        self.log.debug(f"{__name__} payload: {payload}")
        payload['generation'] = payload['generation'].upper().split( ',' )
        response:Dict[str, Any] = { 'networks': [], 'year': datetime.datetime.now().year, 'generation': payload['generation']}
        self.log.debug( pprint.pformat( self.__gsa_data['United Kingdom'], indent=4))
        for country in self.__gsa_data:
            for network in self.__gsa_data[country]:
                bands = []
                for e in self.__gsa_data[country][network]:

                    if not self.__gsa_data[country][network][e]:
                        continue

                    if self.__gsa_data[country][network][e].get( 'generation' ) not in payload['generation']:
                        continue

                    if self.__gsa_data[country][network][e].get( 'terminates' ):
                        bands.append( e )
                        terminates = self.__gsa_data[country][network][e]['terminates']

                if bands:
                    parts = country.split( " " )

                    initials = ''
                    for p in parts:
                        initials += p[:1]

                    response['networks'].append(
                        {
                            'country': country,
                            'country_abbreviation': initials,
                            'network': network,
                            'date': terminates,
                            'bands': ','.join(bands),
                            'closed': True,
                        }
                    )

        countries = [k['country'] for k in response['networks'] if k.get('country')]
        countries = len(set(countries))
        self.log.debug(f"producing colour range for {countries} colours" )
        start = Color('#4fb3bf')
        colours = list(start.range_to(Color('#005662'),countries))
        country = ''
        for n in response['networks']:
            if country != n['country']:
                country = n['country']
                colour = colours.pop().get_hex()
            n['colour'] = colour

        response['networks'] = sorted(response['networks'], key=lambda k: k['date'])

        return {"success": True, "data": response}
