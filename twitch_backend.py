import os

from twitchpy.client import Client
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import threading

from streamcontroller_plugin_tools import BackendBase


def make_handler(plugin_backend: 'Backend', client_id: str, client_secret: str):
    class AuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if not self.path.startswith('/auth'):
                self.send_response(201)
                return
            url_parts = urlparse(self.path)
            query_params = parse_qs(url_parts.query)
            if 'error' in query_params:
                message = query_params['error_description'] if 'error_description' in query_params else 'Something went wrong!'
                status = 500
            else:
                message = 'Success! You may now close this browser window'
                status = 200
            shutdown = threading.Thread(
                target=self.server.shutdown, daemon=True)
            shutdown.start()

            self.protocol_version = 'HTTP/1.1'
            self.send_response(status)
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(bytes(message, 'utf8'))

            if status != 200:
                plugin_backend.auth_failed()
                return

            plugin_backend.auth_with_code(
                client_id, client_secret, query_params['code'][0])
    return AuthHandler


class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.twitch: Client = None
        self.user_id: str = None
        self.token_path: str = None
        self.httpd: HTTPServer = None
        self.httpd_thread: threading.Thread = None
        self.auth_callback_fn: callable = None

    def set_token_path(self, path: str) -> None:
        self.token_path = path

    def on_disconnect(self, conn):
        if self.httpd is not None:
            self.httpd.shutdown()
        super().on_disconnect(conn)

    def create_clip(self) -> None:
        if not self.twitch:
            return
        self.twitch.create_clip(self.user_id)

    def create_marker(self) -> None:
        if not self.twitch:
            return
        self.twitch.create_stream_marker(self.user_id)

    def get_viewers(self) -> str:
        if not self.twitch:
            return
        streams = self.twitch.get_streams(first=1, user_id=self.user_id)
        if not streams:
            return '-'
        return str(streams[0].viewer_count)

    def toggle_chat_mode(self, mode: str) -> str:
        if not self.twitch:
            return
        current = self.twitch.get_chat_settings(self.user_id, self.user_id)
        updated = not getattr(current, mode)
        self.twitch.update_chat_settings(
            self.user_id, self.user_id, **{mode: updated})
        return str(updated)

    def get_chat_settings(self) -> dict:
        if not self.twitch:
            return
        current = self.twitch.get_chat_settings(self.user_id, self.user_id)
        return {
            'subscriber_mode': current.subscriber_mode,
            'follower_mode': current.follower_mode,
            'emote_mode': current.emote_mode,
            'slow_mode': current.slow_mode
        }

    def send_message(self, message: str) -> None:
        if not self.twitch:
            return
        self.twitch.send_chat_message(self.user_id, self.user_id, message)

    def update_client_credentials(self, client_id: str, client_secret: str, callbackfn: callable) -> None:
        if None in (client_id, client_secret) or "" in (client_id, client_secret):
            return
        self.auth_callback_fn = callbackfn
        params = {
            'client_id': client_id,
            'redirect_uri': 'http://localhost:3000/auth',
            'response_type': 'code',
            'scope': 'user:write:chat channel:manage:broadcast moderator:manage:chat_settings clips:edit'
        }
        encoded_params = urlencode(params)
        if not self.httpd:
            self.httpd = HTTPServer(('localhost', 3000), make_handler(
                self, client_id, client_secret))
        if not self.httpd_thread or not self.httpd_thread.is_alive():
            self.httpd_thread = threading.Thread(
                target=self.httpd.serve_forever, daemon=True)
        if not self.httpd_thread.is_alive():
            self.httpd_thread.start()

        webbrowser.open(
            f'https://id.twitch.tv/oauth2/authorize?{encoded_params}')

    def auth_with_code(self, client_id: str, client_secret: str, auth_code: str) -> None:
        try:
            self.twitch = Client(client_id=client_id, client_secret=client_secret,
                                 tokens_path=self.token_path, redirect_uri='http://localhost:3000/auth', authorization_code=auth_code)
            users = self.twitch.get_users()
            self.user_id = users[0].user_id
            self.frontend.save_auth_settings(
                client_id, client_secret, auth_code)
            if self.auth_callback_fn:
                print('auth callback')
                self.auth_callback_fn(True)
        except:
            self.auth_failed()

    def auth_failed(self) -> None:
        if self.auth_callback_fn:
            self.auth_callback_fn(False)

    def is_authed(self) -> bool:
        return self.user_id != None


backend = Backend()
