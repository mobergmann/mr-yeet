# mr-yeet
A Bot, which can be summoned with the command `/yeet`, or `/yeetkick`.
When the Bot has been summoned, he moves a random user, which is on the same channel as the summoner, into a channel called "YEET-LAUNCH", or if not exist into the guilds AFK channel.
With `/yeetkick` a random user is disconnected from the server.
With `/yeetscore` you receive your yeet score.

# Adding the Bot
https://discord.com/oauth2/authorize?client_id=753719268021108796&scope=bot&permissions=16777216

# Using the Bot
`/yeet` yeets a random person in a channel challed `YEET-LAUNCH`
`/yeetkick` yeets a random person from the server

# config.json
Create a file called `config.json` and a token attribute and a `command_prefix` attribute.

For Example:
```json
{
    "token": "123abc...",
    "command_prefix": "/"
}```
