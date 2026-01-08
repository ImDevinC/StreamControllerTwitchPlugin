# StreamController Twitch Integration
This plugin adds the ability to interact with your Twitch stream in a variety of ways.

## Available Actions

- **Marker** - Create a stream marker to highlight important moments during your broadcast
- **SendMessage** - Send a chat message to a specified Twitch channel
- **ShowViewers** - Display the current number of viewers watching your stream
- **ChatMode** - Toggle chat restrictions including Follower Only, Subscriber Only, Emote Only, and Slow Mode
- **Clip** - Create a clip of the current moment in your stream
- **PlayAd** - Run an ad break with configurable duration (30, 60, 90, or 120 seconds)
- **AdSchedule** - Display countdown to next scheduled ad with color-coded alerts and snooze capability

## Setup
This plugin does require you to create a Twitch app in your account. This can be done at https://dev.twitch.tv/console/apps/create. Name
the app whatever you want, set the OAuth redirect URL to `http://localhost:3000/auth` and choose any category. Make sure to also select
"Confidential" for the client type.
After creating the app, you will be shown a Client ID and Client Secret. You can paste these values into any of the actions that you setup,
and the values will be shared between all of them. Make sure to click the Validate button to store the credentials.
