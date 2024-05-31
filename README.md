# StreamController Twitch Integration
This plugin adds the ability to interact with your Twitch stream in a variety of ways. Currently supported functions:

* Create stream marker
* Send a message to your stream
* See number of viewers on your stream

## Setup
This plugin does require you to create a Twitch app in your account. This can be done at https://dev.twitch.tv/console/apps/create. Name
the app whatever you want, set the OAuth redirect URL to `http://localhost:3000/auth` and choose any category. Make sure to also select
"Confidential" for the client type.
After creating the app, you will be shown a Client ID and Client Secret. You can paste these values into any of the actions that you setup,
and the values will be shared between all of them. Make sure to click the Validate button to store the credentials.
