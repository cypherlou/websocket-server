"use strict" ;
import {LitElement, html} from 'https://unpkg.com/lit-element@2.4.0?module' ;

class WebSocket extends LitElement {
    // make sure to add websocketConnected as a property, otherwise LitElement won't trigger
    // a render when the property is set
    static get properties() {
	return {
	    handler: { type: Object },
	    socket: { type: Object },
	    websocketConnected: { type: Boolean }
	};
    }
    
    connectedCallback() {
	super.connectedCallback();
	/* 
	   Set self so that callbacks have access to the Lit object and don't think they are dealing with 
	   self, which would be the socket.io library.
	   The following two examples connected and disconnected routines just illustrate this. When the
	   socket connects it will set the property websocketConnected to true and the opposite if it
	   disconnects.
	 */
	self = this ;
	var socketConnected = function( ) {
	    self.websocketConnected = true ;
	}
	
	var socketDisconnected = function( ) {
	    self.websocketConnected = false ;
	}
	/*
	  Create the websocket object and connect it to the current domain, passing in the above two
	  handlers as described above.
	 */
	this.handler = new websocketObjectWrapper() ;
	this.handler.connect( '//' + document.domain + ':443', socketConnected, socketDisconnected ) ;
	
    }
    
    // Define the HTML of your element
    render() {
/*	return html`<div>
	Websocket connected: ${this.websocketConnected}
	</div>`;*/
    }

}
// Register your element
customElements.define('hyphabit-websocket', WebSocket);
