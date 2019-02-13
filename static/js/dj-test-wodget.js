
import {LitElement, html} from 'https://unpkg.com/lit-element@2.0.0-rc.5?module' ;
    
class TestWodget extends LitElement {
    // make sure to add websocketConnected as a property, otherwise LitElement won't trigger
    // a render when the property is set
    static get properties() {
	return {
	    serverDataX: { type: Object },
	    websocket: { type: String },
	    source: { type: String },
	    debug: { type: Boolean }
	} ;
    }
    
    connectedCallback() {
	super.connectedCallback() ;
	this.websocket = document.querySelector( '#'+ this.websocket ).handler ;
	this.debug = true ;
	this.websocket.name = this.id ;
	var self = this ;
	var processResponseX = function( data ) {
	    console.trace() ;
	    console.log( this ) ;
	    console.log( data ) ;
	    console.log( self ) ;
	    self.serverDataX = JSON.stringify( data ) ;
	}
	this.websocket.register( this.source, processResponseX ) ;
	if ( this.debug ) console.log( "emitting data to "+ this.source +" endpoint" ) ;
	this.websocket.send( this.source, { 'object': this.id, 'request': this.source, data: { length: 50 } } ) ;
    }
    
    // Define the HTML of your element
    render() {
	return html`<div>
	Some data from the server: ${this.serverDataX}
	</div>`;
    }

}
// Register your element
customElements.define('dj-test-wodget', TestWodget);
