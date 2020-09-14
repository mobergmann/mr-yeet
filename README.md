# mr-yeet
A Bot, which can be summoned with the command `/yeet`, or `/yeetkick`.

When the Bot has been summoned, he moves (or disconnects) a random user, which is on the same channel as the summoner, into a channel called "YEET-LAUNCH", or if not exist into the guilds AFK channel.

To get your personal Yeet Score you can use `/yeetscore`.

## Disclaymer
The Bot needs to store some Data of the users to provide the `/yeetscore` functionality. He stores the id of a discord user, who uses the bot, or has been yeetet by the bot, and he stores the times a user has been yeeted or yeeted someone.
He also stores who and when a command has been used (logging) to make the process of an issue finding and fixing more easily.


# How-To
## Adding the Bot
You can add the Bot by pressing [here](https://discord.com/oauth2/authorize?client_id=753719268021108796&scope=bot&permissions=19975168).

### The Bots needs at least the following permissions:
- view channels
- connect
- move members
- speak

- read messages
- send messages
- embed links
- attach files

## Usage
- `/yeethelp`: Prints a help page (this page, in case you didn't notice).
- `/yeet` Moves a random user into a channel called **YEET-LAUNCH** or if not exist into the guilds **AFK** channel.
- `/yeetsoft`: Like `/yeet` but moves the user back into the origin channel after 2 seconds.
- `/yeetkick`: Like `/yeet` but doesn't move the user into the yeet channel, instead disconnects the user from the server.
- `/yeetscore` Shows the yeet score of the caller.

## Yeet Score FAQ
- How is the yeet score calculated?
  - (*times you yeetet anyone* / *times you have been yeetet*) + (*times you yeetet anyone* / 50)
- Is there a difference between the commands in yeet score gain?
  - No! Every command increases your yeet score according to the function.


# Source Code
## config.json
For the bot to function you need to add values to the `config.json`. Add the token of your Bot to the `token` attribute and a prefix for the `command_prefix` attribute.

For Example:
```json
{
    "token": "your token here",
    "command_prefix": "/"
}
```
