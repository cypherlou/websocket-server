# websocket-server
Gunicorn/Flask Websocket Server

## Install
Optional virtual environment.
`virtualenv -p $(which python3) env; source env/bin/activate`

Install libraries.
`pip install -r requirements.txt`

## Run the server
```
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:8000 \
    hyphabit_api:app --keep-alive 2 --timeout 100 --pid hyphabit_api.pid --reload --daemon
```
