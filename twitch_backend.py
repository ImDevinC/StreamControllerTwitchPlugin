import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import threading
import requests

from loguru import logger as log
from twitchpy.client import Client
from twitchpy.errors import ClientError

from streamcontroller_plugin_tools import BackendBase


def make_handler(plugin_backend: 'Backend'):
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

            plugin_backend.new_code(query_params['code'][0])

    return AuthHandler


class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.twitch: Client = None
        self.user_id: str = None
        self.token_path: str = None
        self.client_secret: str = None
        self.client_id: str = None
        self.httpd: HTTPServer = None
        self.httpd_thread: threading.Thread = None
        self.auth_code: str = None

    def set_token_path(self, path: str) -> None:
        self.token_path = path

    def on_disconnect(self, conn):
        if self.httpd is not None:
            self.httpd.shutdown()
        super().on_disconnect(conn)

    def create_clip(self) -> None:
        if not self.twitch:
            return
        self.validate_auth()
        self.twitch.create_clip(self.user_id)

    def create_marker(self) -> None:
        if not self.twitch:
            return
        self.validate_auth()
        self.twitch.create_stream_marker(self.user_id)

    def get_viewers(self) -> str:
        if not self.twitch:
            return
        self.validate_auth()
        streams = self.twitch.get_streams(first=1, user_id=self.user_id)
        if not streams:
            return '-'
        return str(streams[0].viewer_count)

    def toggle_chat_mode(self, mode: str) -> str:
        if not self.twitch:
            return
        self.validate_auth()
        current = self.twitch.get_chat_settings(self.user_id, self.user_id)
        updated = not getattr(current, mode)
        self.twitch.update_chat_settings(
            self.user_id, self.user_id, **{mode: updated})
        return str(updated)

    def get_chat_settings(self) -> dict:
        if not self.twitch:
            return {}
        self.validate_auth()
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
        self.validate_auth()
        self.twitch.send_chat_message(self.user_id, self.user_id, message)

    def update_client_credentials(self, client_id: str, client_secret: str) -> None:
        if None in (client_id, client_secret) or "" in (client_id, client_secret):
            return
        self.client_id = client_id
        self.client_secret = client_secret
        params = {
            'client_id': client_id,
            'redirect_uri': 'http://localhost:3000/auth',
            'response_type': 'code',
            'scope': 'user:write:chat channel:manage:broadcast moderator:manage:chat_settings clips:edit channel:read:subscriptions'
        }
        encoded_params = urlencode(params)
        if not self.httpd:
            self.httpd = HTTPServer(('localhost', 3000), make_handler(self))
        if not self.httpd_thread or not self.httpd_thread.is_alive():
            self.httpd_thread = threading.Thread(
                target=self.httpd.serve_forever, daemon=True)
        if not self.httpd_thread.is_alive():
            self.httpd_thread.start()

        url = f'https://id.twitch.tv/oauth2/authorize?{encoded_params}'
        check = requests.get(url, timeout=5)
        if check.status_code != 200:
            print('invalid client ID')
            self.auth_failed()
            return

        webbrowser.open(
            f'https://id.twitch.tv/oauth2/authorize?{encoded_params}')

    def new_code(self, auth_code: str) -> None:
        self.auth_with_code(self.client_id, self.client_secret, auth_code)

    def validate_auth(self) -> None:
        try:
            _ = self.twitch.get_streams(first=1, user_id=self.user_id)
        except ClientError:
            self.auth_with_code(
                self.client_id, self.client_secret, self.auth_code)

    def auth_with_code(self, client_id: str, client_secret: str, auth_code: str) -> None:
        try:
            self.twitch = Client(client_id=client_id, client_secret=client_secret,
                                 tokens_path=self.token_path, redirect_uri='http://localhost:3000/auth', authorization_code=auth_code)
            users = self.twitch.get_users()
            self.auth_code = auth_code
            self.user_id = users[0].user_id
            self.client_id = client_id
            self.client_secret = client_secret
            self.frontend.save_auth_settings(
                client_id, client_secret, auth_code)
            self.frontend.on_auth_callback(True)
        except Exception as e:
            log.error("failed to authenticate", e)
            self.auth_failed()

    def auth_failed(self) -> None:
        self.user_id = None
        self.frontend.on_auth_callback(False)

    def is_authed(self) -> bool:
        return self.user_id != None


backend = Backend()
