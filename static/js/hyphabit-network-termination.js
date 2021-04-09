"use strict" ;
import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.4.0?module' ;

class HyphabitNetworkTerminationList extends LitElement {
    static get properties() {
	return {
	    serverData: { type: Object },
	    websocket: { type: String },
	    source: { type: String },
	    generation: { type: String },
	    debug: { type: Boolean },
	    country_selector: { type: String, attribute: true },
	    band_selector: { type: String, attribute: true },
	    start_colour: { type: String },
	    end_colour: { type: String },
	} ;
    }
    
    constructor(){
	super();
	this.generations = {} ;
	this.countries = {}
	this.country_selector = "All" ;
	this.band_selector = "All" ;
	this.generation = "2g" ;
	this.start_colour = '#4fb3bf' ;
	this.end_colour = '#005662';
    }

    static get styles() {
	return css`
        :host {
          min-height: 350px ;
          line-height: 1.0 ;
        }`;
    }
    
    construct_network_data( source ) {
	var self = this ;
	source.forEach( function( e ) {
	    self.countries[e.country] = 1 ;
	    e.bands.split(",").forEach( function(b) {
		self.generations[b] = 1 ;
	    } ) ;
	} ) ;

	this.serverData = html`
<div class="filter-selector">
<hyphabit-network-filter 
  .options=${this.countries} 
  name="Country"
  .choice=${this.country_selector} 
  @changed="${(e) => this.country_filter_updated(e)}">
</hyphabit-network-filter>
<hyphabit-network-filter 
  .options=${this.generations}
  name="Frequency"
  .choice=${this.band_selector} 
  @changed="${(e) => this.band_filter_updated(e)}">
</hyphabit-network-filter>
</div><div class="network-listings">
${source.map( item => html`<hyphabit-network-termination 
  .network=${item.network}
  .shade=${item.colour}
  .abbreviation=${item.country_abbreviation}
  .date=${item.date}
  .bands=${item.bands}
  country_choice=${this.country_selector}
  .band_choice=${this.band_selector}
  .country=${item.country} closed>
</hyphabit-network-termination>` )}
</div>`;
    }
    
    connectedCallback() {
	super.connectedCallback() ;
	
	this.websocket = document.querySelector( '#'+ this.websocket ).handler ;
	this.websocket.name = this.id ;

	var self = this ;
	var processResponse = function( data ) {
	    self.construct_network_data( data.data.networks ) ;
	}
	this.websocket.register( this.source, processResponse ) ;
	this.websocket.send( this.source, { object: this.id, request: this.source, data: { generation: this.generation, start_colour: this.start_colour, end_colour: this.end_colour } } ) ;
    }
/*
    attributeChangedCallback(name, oldVal, newVal) {
	super.attributeChangedCallback(name, oldVal, newVal);
	console.log('HyphabitNetworkTerminationList attribute change: ', name, oldVal, newVal);
    }
    updated(changedProperties) {
	changedProperties.forEach((oldValue, propName) => {
	    console.log(`HyphabitNetworkTerminationList property ${propName} changed. oldValue: ${oldValue}`);
	});
    }
*/
    country_filter_updated(e) {
	var country = e.detail.name ;
	this.country_selector = country ;
	this.renderRoot.querySelectorAll('hyphabit-network-termination').forEach( function( e ) {
	    e.country_changed( country ) ;
	} ) ;
    }
    band_filter_updated(e) {
	var band = e.detail.name ;
	this.band_selector = band ;
	this.renderRoot.querySelectorAll('hyphabit-network-termination').forEach( function( e ) {
	    e.band_changed( band ) ;
	} ) ;
    }
    render() {
	return html`<div class="list-container">${this.serverData}</div>`;
    }

}
customElements.define('hyphabit-network-termination-list', HyphabitNetworkTerminationList);


class HyphabitNetworkFilter extends LitElement {
    static get properties() {
	return {
	    options: { type: Object },
	    name: { type: String },
	    choice: {
		type: String,
		reflect: true
	    },
	} ;
    }

    constructor() {
	super();
	this.options = [] ;
	this.choice="All";
    }
    static get styles() {
	return css`
:host {
  line-height: 1.0 ;
}
.custom-select {
  border-bottom: 1px solid #015b67;
  display: inline-block ;
  margin: 5px 15px ;
}
select {
  margin: 10px;
  box-shadow: none;
  outline: none;
  padding: 15px 5px 0px 5px ;
  font-size: 20px;
  border: 0 ;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
.name {
    color: #148998;
    position: relative;
    top: 16px;
}
@media only screen and (max-width: 376px) {
  select {
    font-size: 17px ;
  }
}
`;
    }

    connectedCallback() {
	super.connectedCallback() ;
	this.options_data = Object.keys(this.options).sort() ;
    }
    
    option_selected( e ) {
	this.choice = this.options_data[e.srcElement.selectedIndex-1] ;
	if (this.choice == undefined ) {
	    this.choice = 'All' ;
	}
	var event_data = { index: e.srcElement.selectedIndex, name: this.choice } ;
	let event = new CustomEvent('changed', { detail: event_data } );
	this.dispatchEvent(event);
    }
    

    render() {
	return html`
<div class="custom-select">
  <div class="name">${this.name}</div>
    <select @change=${this.option_selected}><option value="_">All</option>
      ${this.options_data.map((c) => html`<option value="${c}">${c}</option>`)}
    </select>
</div>`;
    }

}
customElements.define('hyphabit-network-filter', HyphabitNetworkFilter);


class HyphabitNetworkTermination extends LitElement {
    static get properties() {
	return {
	    network: { type: String },
	    shade: { type: String },
	    abbreviation: { type: String },
	    date: { type: String },
	    bands: { type: String },
	    country: { type: String },
	    closed: { type: Boolean, value: true },
	    country_choice: { type: String, },
	    band_choice: { type: String, },
	} ;
    }

    filterResults( countries, bands ) {
	console.log( countries, bands ) ;
    }
    
    expandNetworkBlock(e) {
	this.closed = !this.closed ;
    }
    
    connectedCallback() {
	super.connectedCallback() ;
	this.hidden = false ;
	this.country_selected = true ;
	this.band_selected = true ;
    }

    static get styles() {
	return css`
        :host {
	  width: 100%;
          line-height: 1.0 ;
        }
      .hidden { display: none }
      .icon {
        width: 70px;
        height: 70px;
        line-height: 70px;
        border-radius: 50%;
        text-align: center;
        background-color: #ffdb49;
        color: #fff;
        font-size: 28px ;
      }
      .mno {
        font-size: 30px ;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
	line-height: 1.3;
      }
      .closure-date {
        font-size: 24px ;
        color: darkgrey ;
      }

      .row {
	padding: 5px 2px ;
        display: grid;
        grid-template-columns: 80px auto 50px;
        grid-template-rows: 65% 35%;
      }
      .grid-item-icon {
        grid-column-start: 1;
        grid-column-end: 2;
        grid-row-start: 1;
        grid-row-end: 3;
        align-self: center;
      }
      .grid-item-network {
        grid-column-start: 2;
        grid-column-end: 3;
        grid-row-start: 1;
        grid-row-end: 2;
        align-self: center;
      }
      .grid-item-date {
        grid-column-start: 2;
        grid-column-end: 3;
        grid-row-start: 2;
        grid-row-end: 3;
        align-self: center;
      }
      .grid-open {
        grid-column-start: 3;
        grid-column-end: 4;
        grid-row-start: 1;
        grid-row-end: 3;
        align-self: center;
        justify-self: end;
      }
      .dividing-row {
        background: #bbb;
        height: 1px ;
        width: calc(100%-80px) ;
        margin: 5px 0 5px 80px ;
      }
      .material-icon {
          font-family: 'Material Icons';
          font-size: 34px;
          border-radius: 50%;
          color: #000 ;
          width: 40px;
          height: 40px;
          margin: 5px;
          cursor: pointer;
      }
      .expand-button {
        border-radius: 50%;
        text-align: center;
        width: 40px;
        height: 40px;
        line-height: 40px;
	background-color: #eee;
	outline: none;
	user-select: none;
	-webkit-tap-highlight-color: transparent;
      }
      .band-loz {
        background-color: #eee;
        display: inline-block;
        padding: 5px;
        border-radius: 3px;
        margin: 3px;
      }
      .bands-country {
	border-bottom: solid 1px #bbb;
        margin: 5px 0;
        padding: 5px;
      }
      .country {
	font-size: 30px;
	color: #666;
	padding: 5px ;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      @media only screen and (min-width: 377px) {
	.container {
	  padding: 3px ;
          width: 300px ;
          height: 180px ;
          border: 1px solid #eee ;
          box-shadow: 0px 2px 3px rgba(0,0,0,0.12), 0px 2px 2px rgba(0,0,0,0.24);
          transition: all 0.3s cubic-bezier(.25,.8,.25,1);
          border-radius: 5px ;
          display: inline-block ;
          margin: 3px ;
          float: left ;
          margin: 10px 6px ;
          background-color: #fbfbfb ;
	}
	.mno {
	  font-size: 20px ;
	}
	.expand-button { display: none; }
        .bands-country {
	  border-bottom: 0;
	  padding: 10px 5px ;
	}
        .hidden { display: inline-block ; }
	.band-loz {
	  font-size: 14px ;
	}
        .icon {
          width: 60px;
          height: 60px;
          line-height: 60px;
	  font-size: 26px ;
	}
      }
      .hard-off { display: none }

      .expand-more {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 0 24 24' width='24'%3E%3Cpath d='M0 0h24v24H0V0z' fill='none'/%3E%3Cpath d='M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14l-6-6z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: 100% ;
      }
      .expand-less {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 0 24 24' width='24'%3E%3Cpath d='M24 24H0V0h24v24z' fill='none' opacity='.87'/%3E%3Cpath d='M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6-1.41-1.41z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: 100% ;
      }
`;
    }

    country_changed( country ) {
	this.country_choice = country ;
	if ( this.country_choice != this.country & this.country_choice != 'All' ) {
	    this.country_selected = false ;
	} else {
	    this.country_selected = true ;
	}
	this.filter_networks();
    }
    band_changed(band) {
	this.band_choice = band ;
	if ( !this.bands.includes(this.band_choice) & this.band_choice != 'All' ) {
	    this.band_selected = false ;
	} else {
	    this.band_selected = true ;
	}
	this.filter_networks();
    }

    filter_networks() {
	if ( this.band_selected & this.country_selected ) {
	    this.hidden = false ;
	} else {
	    this.hidden = true ;
	}
    }
    
    // Define the HTML of your element
    render() {
	return html`
  <div class="container ${this.hidden ? 'hard-off' : ''}">
    <div class="row">
      <div class="icon grid-item-icon" style="background-color: ${this.shade}">${this.abbreviation}</div>
      <div class="mno grid-item-network">${this.network}</div>
      <div class="closure-date grid-item-date">${this.date}</div>
      <div class="expand-button grid-open material-icon" @click=${(e) => {this.expandNetworkBlock(e)}}>
	<div class="expand-more ${this.closed ? '' : 'hidden'}">&nbsp;</div>
	<div class="expand-less ${this.closed ? 'hidden' : ''}">&nbsp;</div>
      </div>
    </div>
    <div class="dividing-row ${this.closed ? '' : 'hidden'}"></div>
    <div class="bands-country ${this.closed ? 'hidden' : ''}">
	<div>${this.format_bands(this.bands)}</div>
	<div class="country">${this.country}</div>
    </div>
  </div>
` ;
    }


    format_bands(b) {
	var band_list = b.split(",") ;
	return band_list.map(band => html`<div class="band-loz">${band}</div>`) ;
    }
    
}
customElements.define('hyphabit-network-termination', HyphabitNetworkTermination);
