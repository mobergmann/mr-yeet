# mr-yeet
Mr-Yeet is a fun discord Bot. 
You can yeet a random user, who is connected to the same voice channel as you into the AFK channel for 2 seconds.

To add the bot to your server click [here](https://discord.com/api/oauth2/authorize?client_id=753719268021108796&permissions=2167406592&scope=bot).

## Commands

| Command                   | Description                                                                                                                                                                                                |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/yeet`                   | Moves a random user, which is connected to the same voice channel as you, into the servers AFK channel for 2 seconds. If no AFK channel is present, then the user will be disconnected.                    |
| `/score`                  | Displays an embed with the users yeet statistics. These are how ofthen the user has been yeeted, how often the user has yeeted and based on these metrics a score and a rank, associated with that score.  |
| `/forget`                 | Deletes/ Removes your data from the database, so you can enjoy your DSGVO right for deletion.                                                                                                              |
| `/immunity [True, False]` | Grants yeet immunity. When you set immunity to `True`, then you can no longer be yeeted, but also cannot yeet anymore.                                                                                     |

## Future
Plans for the future:
- [ ] Sound/ Voice: Let the Bot join a channel and play a yeet sound (see the `ressources/yeet-sound.wav` file)
- [ ] Yeet Coins: currency, used for other/ future commands
- [ ] Yeet snipe: yeet a specific user
