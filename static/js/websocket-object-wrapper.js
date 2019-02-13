"use strict" ;
window.websocketObjectWrapper = window.websocketObjectWrapper || function( ) {

    this.socket = undefined ;
    this.debug = true ;
    this.target = '//' + document.domain + ':443' ;

    this.connect = function( target, connect=function(){}, disconnect=function(){} ) {

	if ( this.host ) {
	    if ( this.host != target ) {
		if ( this.debug ) console.warn( "** socket already connected to "+ this.host +", can't now connect to "+ target +" **" ) ;
	    } else {
		if ( this.debug ) console.debug( "** socket already connected to "+ this.host +", using that connection **" ) ;
	    }
	} else {
	    this.socket =  io.connect( this.target ) ;
	    this.socket.on( 'connect', connect ) ;
	    this.socket.on( 'disconnect', disconnect ) ;
	    this.socket.on( 'message', function( data ) { console.log( data ) } ) ;
	}
    }

    this.register = function( route, func ) {
	name = this.name +"/"+ route ;
	if ( this.debug ) console.log( "registering function against endpoint " + name ) ;
	this.socket.on( name, func ) ;
	
    } ;

    this.send = function( route, data ) {
	name = this.name +"/"+ route ;
	if ( this.debug ) console.log( "sending data with expected endpoint " + name ) ;
	data.return_route = name ;
	console.log( data ) ;
	this.socket.send( name, data ) ;
    } ;

    this.deregister = function( ) {
	// this.socket.deregisterAll( this.element ) ;
    } ;

    return this ;
}
