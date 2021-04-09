# Hyphabit Server
Gunicorn/Flask Websocket Server

## Install
`virtualenv -p $(which python3) env; source env/bin/activate`

Install libraries.
`pip install -r requirements.txt`

## Run the server
```
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:8000 \
    hyphabit_api:app --keep-alive 2 --timeout 100 --pid hyphabit_api.pid --reload --daemon
```

## Custom Elements
To add the various custom elements to the Hyphabit WP site you need to include some base libraries along with specific Custom Element in a RAW container in the Pro editor. There are a variety of Custom Elements, all of which require slightly different resources so it is important to C&P the appropriate code snippet.

### Network Termination tables.
There are currently 2 Network Termination tables, 2G and 3G. The 2G version actually covers 2G and 2.5G (EDGE) variations.

#### `hyphabit-network-termination-list` - 2G
To add the 2G `hyphabit-network-termination-list` tag to the page, insert a raw element (using the Pro Editor) into the appropriate point in the page and then paste the following;
```html
<script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script src="/hyphabit-api/static/js/websocket-object-wrapper.js"></script>
<script type="module" src="/hyphabit-api/static/js/hyphabit-websocket.js"></script>
<script type="module" src="/hyphabit-api/static/js/hyphabit-network-termination.js"></script>
<hyphabit-websocket id="hyphabit-ws"></hyphabit-websocket>
<hyphabit-network-termination-list id="gntl-2g" websocket="hyphabit-ws" source="network_termination" generation="2g,2.5g" start_colour="#4fb3bf" end_colour="#005662"></hyphabit-network-termination-list>
```
Note that the `generation` attribute defines which generations are in use and the `start_colour` and `end_colour` attributes define the range of colours that will be applied to the country avatar. If omitted then the generation defaults to `2g` and start and end colours default to `#4fb3bf` and `#005662` respectively.


#### `hyphabit-network-termination-list` - 3G
See the instructions above for the insertion of the `hyphabit-network-termination-list` for 3G networks. The key difference are the `generation`, `start_colour` and `end_colour` attributes on the `hyphabit-network-termination-list` element. This configuration uses the orange instead of the teal colours for the network avatars.
```html
<script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script src="/hyphabit-api/static/js/websocket-object-wrapper.js"></script>
<script type="module" src="/hyphabit-api/static/js/hyphabit-websocket.js"></script>
<script type="module" src="/hyphabit-api/static/js/hyphabit-network-termination.js"></script>
<hyphabit-websocket id="hyphabit-ws"></hyphabit-websocket>
<hyphabit-network-termination-list id="gntl-3g" websocket="hyphabit-ws" source="network_termination" generation="3g" start_colour="#ffc046" end_colour="#c56000"></hyphabit-network-termination-list>
```
