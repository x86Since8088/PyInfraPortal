from sanic import Sanic, response
from sanic.response import json
import asyncio
import time

app = Sanic('app')

@app.websocket('/feed')
async def feed(request, ws):
    last_keepalive = time.time()

    while True:
        if time.time() - last_keepalive > 30:
            break  # End the loop if 30 seconds have passed since the last keepalive

        data = await ws.recv()
        print(f"Received: {data}")

        if data == "keepalive":
            last_keepalive = time.time()  # Reset keepalive time on receiving a keepalive signal
            await ws.send(json({"message": "keepalive received"}))
        else:
            now = time.time()
            response_data = {"message": f"Echo: {data}", "timestamp": now}
            await ws.send(json(response_data))

        await asyncio.sleep(10)  # Wait for keepalive or other messages

@app.route('/')
async def handle_request(request):
    return response.html("""
    <html><head>
    <title>Sanic WebSocket Example</title>
    <script>
    const ws = new WebSocket("ws://" + location.host + '/feed');
    ws.onmessage = event => {
      console.log(event.data);
      let out = document.getElementById('out');
      out.innerHTML += `<li><p>${event.data}</p></li>`;
    }
    document.querySelector('form').addEventListener('submit', (event) => {
      event.preventDefault();
      let message = document.querySelector("#message").value;
      ws.send(message);
      document.querySelector("#message").value = "";
    })
    setInterval(() => ws.send("keepalive"), 10000);  // Send keepalive every 10 seconds
    </script>
    </head>
    <body>
      <h1>Main</h1>
      <div><form><input type="text" id="message" name="message"></form></div>
      <div><ul id="out"></ul></div>
    </body>
    </html>
    """)

app.run(host="127.0.0.1", port=8000, dev=True, debug=True, access_log=True, auto_reload=True, workers=1, protocol=0, backlog=100, stop_event=None, register_sys_signals=True, access_log_format=None, request_timeout=None, keep_alive=True, ssl=None, websocket_max_size=None, websocket_max_queue=None, websocket_read_limit=None, websocket_write_limit=None, websocket_ping_interval=None, websocket_ping_timeout=None, websocket_pong_timeout=None, websocket_pong_receive_timeout=None, websocket_close_timeout=None, websocket_max_message_size=None, websocket_handler_class=None, websocket_compress=None, origins=None, load_env=True, env_prefix='SANIC_', error_handler=None, configure_logging=True, log_config=None, log_formatter=None, log_handler=None, log_level=None, log_request_context=True, log_request_headers=False, log_request_payload=False, log_response_headers=False, log_tracebacks=True, log_config_schema=None, request_class=None, strict_slashes=None, ignore_http_methods=None, keep_alive_timeout=None, body_size=None, request_buffer_queue_size=None, request_buffer_size=None, response_buffer_size=None, request_timeout_notify=None, graceful_shutdown_timeout=None, register=False, debug_toolbar=None, static=False, host=None, port=None, unix=None, fd=None, loop=None, protocol_class=None, backlog=None, ssl_host=None, ssl_port=None, ssl_keyfile=None, ssl_certfile=None, ssl_ca_certs=None, ssl_handshake_timeout=None, sock=None, run_multiple=None, workers=None, run_async=False, stop_event=None, auto_reload=None, access_log=None, access_log_file=None, access_log_format=None, error_log_file=None, configure_logging=None, log_config=None, log_formatter=None, log_handler=None, log_level=None, log_request_context=None, log_request_headers=None, log_request_payload=None, log_response_headers=None, log_tracebacks=None, log_config_schema=None, request_class=None, strict_slashes=None, ignore_http_methods=None, keep_alive_timeout=None, body_size=None, request_buffer_queue_size=None, request_buffer_size=None, response_buffer_size=None, request_timeout_notify=None, graceful_shutdown_timeout=None, websocket_max_size=None, websocket_max_queue=None, websocket_read_limit=None, websocket_write_limit=None, websocket_ping_interval=None, websocket_ping_timeout=None, websocket_pong_timeout=None, websocket_pong_receive_timeout=None, websocket_close_timeout=None, websocket_max_message_size=None, websocket_handler_class=None, websocket_compress=None, origins=None, load_env=None, env_prefix=None, error_handler=None, debug_toolbar=None, static=None,)
