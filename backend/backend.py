from streamcontroller_plugin_tools import BackendBase
import json

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import requests
import threading


def make_handler(backend: 'Backend', client_id: str, client_secret: str):
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
                message = "Success! You can close this browser window"
                status = 200

            threading.Thread(target=self.server.shutdown, daemon=True)
            r = requests.post('https://id.twitch.tv/oauth2/token', data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': query_params['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:3000/auth'
            }, timeout=5)
            if r.status_code != 200:
                message = r.text
                status = 500

            self.protocol_version = "HTTP/1.1"
            self.send_response(status)
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(bytes(message, 'utf8'))
            if status != 200:
                backend.show_error(r.text)
                return
            access_token = r.json()['access_token']
            refresh_token = r.json()['refresh_token']
            backend.set_tokens(access_token, refresh_token)
    return AuthHandler


class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.counter: int = 0
        self.auth_callback: callable = None
        self.error_callback: callable = None
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.user_id: str = ""
        self.client_id: str = ""
        self.client_secret: str = ""

    def set_error_callback(self, callback: callable):
        self.error_callback = callback

    def set_auth_callback(self, callback: callable):
        self.auth_callback = callback

    def refresh_access_token(self) -> bool:
        if not self.client_id or not self.client_secret or not self.refresh_token:
            return False
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        r = requests.post('https://id.twitch.tv/oauth2/token',
                          data=data, timeout=5)
        if r.status_code != 200:
            return False
        payload = r.json()
        self.set_tokens(payload['access_token'], payload['refresh_token'])
        return True

    def do_twitch_api_post(self, path: str, body: dict) -> dict:
        if not self.validate_token():
            if not self.refresh_access_token():
                self.start_auth_flow(self.client_id, self.client_secret)
                return
        r = requests.post(path, json=body, headers={
            'Authorization': f'Bearer {self.access_token}',
            'Client-Id': self.client_id
        }, timeout=5)
        return r.json()

    def show_error(self, message: str) -> None:
        print(message)
        if self.error_callback:
            self.error_callback()

    def do_twitch_api_get(self, path: str) -> dict:
        if not self.validate_token():
            if not self.refresh_token:
                self.start_auth_flow(self.client_id, self.client_secret)
                return
        r = requests.get(path, headers={
            'Authorization': f'Bearer {self.access_token}',
            'Client-Id': self.client_id,
        }, timeout=5)
        return r.json()

    def do_twitch_api_patch(self, path: str, body: dict) -> dict:
        if not self.validate_token():
            if not self.refresh_token:
                self.start_auth_flow(self.client_id, self.client_secret)
                return
        r = requests.patch(path, json=body, headers={
            'Authorization': f'Bearer {self.access_token}',
            'Client-Id': self.client_id,
        }, timeout=5)
        return r.json()

    def set_client_creds(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    def start_auth_flow(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        params = {
            'client_id': client_id,
            'redirect_uri': 'http://localhost:3000/auth',
            'response_type': 'code',
            'scope': 'user:write:chat channel:manage:broadcast moderator:manage:chat_settings'
        }
        encoded_params = urlencode(params)
        webbrowser.open(
            f"https://id.twitch.tv/oauth2/authorize?{encoded_params}")
        httpd = HTTPServer(('localhost', 3000), make_handler(
            self, client_id, client_secret))
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        if not self.validate_token():
            self.access_token = ""
            self.refresh_token = ""
            if self.auth_callback:
                self.auth_callback('', '', 'Authentication failed', True)
            return
        if self.auth_callback:
            self.auth_callback(
                self.access_token, self.refresh_token, 'Authentication succeeded', False)

    def validate_token(self) -> bool:
        r = requests.get('https://id.twitch.tv/oauth2/validate',
                         headers={'Authorization': f'OAuth {self.access_token}'}, timeout=5)
        if r.status_code != 200:
            self.show_error(r.text)
            return False
        self.user_id = r.json()['user_id']
        return True

    def send_message(self, message: str) -> None:
        resp = self.do_twitch_api_post('https://api.twitch.tv/helix/chat/messages', body={
            'broadcaster_id': self.user_id,
            'sender_id': self.user_id,
            'message': message
        })
        if 'error' in resp:
            raise Exception(resp['error'])

    def get_viewers(self) -> int:
        body = {
            'user_id': self.user_id,
            'type': 'live',
            'first': 1,
        }
        resp = self.do_twitch_api_get(
            f'https://api.twitch.tv/helix/streams?{urlencode(body)}')
        if not 'data' in resp:
            return 0
        if len(resp['data']) == 0:
            return 0
        return resp['data'][0]['viewer_count']

    def create_marker(self) -> None:
        resp = self.do_twitch_api_post(
            'https://api.twitch.tv/helix/streams/marker', body={
                'user_id': self.user_id
            })
        if 'error' in resp:
            raise Exception(resp['error'])

    def get_chat_settings(self) -> dict:
        params = {
            'broadcaster_id': self.user_id,
            'moderator_id': self.user_id
        }
        resp = self.do_twitch_api_get(
            f'https://api.twitch.tv/helix/chat/settings?{urlencode(params)}')
        if 'error' in resp:
            raise Exception(resp['error'])
        payload = resp['data'][0]
        return {
            'emote_mode': payload['emote_mode'],
            'follower_mode': payload['follower_mode'],
            'slow_mode': payload['slow_mode'],
            'subscriber_mode': payload['subscriber_mode']
        }

    def toggle_chat_mode(self, mode: str) -> None:
        existing = self.get_chat_settings()
        new = not existing[mode]
        params = {
            'broadcaster_id': self.user_id,
            'moderator_id': self.user_id
        }
        resp = self.do_twitch_api_patch(f'https://api.twitch.tv/helix/chat/settings?{urlencode(params)}', body={
            mode: new
        })
        if 'error' in resp:
            print(resp['error'])
            raise Exception(resp['error'])


backend = Backend()
