import discord
import datetime
import random
import time
import json
from discord.ext import commands
from database import Database


config_file = open("config.json", "r").read()
config = json.loads(config_file)
token = config["token"]

bot = commands.Bot(command_prefix="/")

# Ranks
yeet_ranks = [
    ("Unfortunate Yeeter", 0),
    ("Yeet Beginner", 1),
    ("Yeet Trainee", 3),
    ("Yeet Approved", 5),
    ("Yeet Adept", 7),
    ("Big Yeeter", 9),
    ("Yeet Schmied", 11),
    ("Yeetlead", 13),
    ("Boss Yeeter", 15),
    ("Grand Yeeter", 17),
    ("Yeet King", 18),
    ("Yeet Emperor", 19),
    ("Grand Yeet Emperor", 20)
]


#region yeet specific

def get_yeet_rank(yeet_score):
    # make secrets
    if 0 < yeet_score <= 0.01:
        return "Shitty Yeeter"
    if yeet_score >= 35:
        return "The Yeeter of all Yeeters"

    # calculate the yeat rank of the user
    for i in range(len(yeet_ranks)-1):
        if yeet_ranks[i][1] <= yeet_score < yeet_ranks[i+1][1]:
            return yeet_ranks[i][0]
    return yeet_ranks[len(yeet_ranks)-1][0] # prevent an out of bounds


async def _yeet(ctx, should_kick=False, move_back=False):
    #region Error Check
    yeet_voice = ctx.author.voice

    # if user is not in a voice channel, then inform the user
    if yeet_voice == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return

    yeet_voice_channel = yeet_voice.channel

    # if user is not connected to a voice channel
    if yeet_voice_channel == None:
        log("{} is not connected to a voice channel".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me when you are connected to a chanel on a guild")
        return

    # if message guild is different from user voice channel inform the user
    if ctx.guild != yeet_voice_channel.guild:
        log("{} used yeet on a guild to which he wasn't connected".format(ctx.author))
        await send_dm(ctx.author, "Please only summmon me on a guild, when you are also connected to a voicechanel on that guild.")
        return


    # get yeet channel from server
    # can either be a channel called YEET-LAUNCH, or if the channel doesn't exist the afk channel
    yeet_channel = discord.utils.find(lambda x: x.name == "YEET-LAUNCH", ctx.guild.channels)
    if yeet_channel == None:
        yeet_channel = ctx.guild.afk_channel
        if yeet_channel == None:
            try:
                await ctx.channel.send("I cannot use my yeet powers, because I need a channel with the name YEET-LAUNCH, or a AFK channel. Please create one.")
                return
            except Exception as e:
                log(str(e))
                return

    # if user already connected to yeet channel
    if yeet_voice_channel == yeet_channel:
        log("{} used yeet in the yeet channel".format(ctx.author))
        await send_dm(ctx.author, "Please don't summmon me when you are alreay connected to the yeet_cannel.")
        return
    #endregion

    # the origin channel in which mr yeet has been summond 
    origin_channel = ctx.author.voice.channel

    # get users which can be yeetet
    users_to_yeet = origin_channel.members

    # get user to yeet
    user_to_yeet = random.choice(users_to_yeet)

    # connect bot to voice
    voice = None
    try:
        voice = await yeet_voice_channel.connect()
    except Exception as e:
        log(str(e))
        return

    # play yeet sound
    player = voice.play(discord.FFmpegPCMAudio("sounds/yeet.mp3"))
    time.sleep(1) # wait for the sound to be finished playing

    # yeet user form voice channel
    for user in users_to_yeet:
        if user_to_yeet == user:
            if should_kick:
                try:
                    await user_to_yeet.move_to(None) # disconnect from voice
                except Exception as e:
                    log(str(e))
                    return
                break
            else:
                try:
                    await user_to_yeet.move_to(yeet_channel) # move into yeet channel
                except Exception as e:
                    log(str(e))
                    return
                break

    # disconnect bot from voice channnel (so early, to prevent errors)
    try:
        await voice.disconnect()
    except:
        log("Fatal Error could not disconnect from voice channel")
        return


    # log yeet action
    if should_kick:
        log("{} yeetkicked {}".format(ctx.author, user_to_yeet))
    else:
        log("{} yeeted {}".format(ctx.author, user_to_yeet))

    # inform, that bot has yeetet a user
    await ctx.channel.send("Yeeted {}".format(user_to_yeet))

    #region add informatoin to database
    try:
        db_inc_has_yeet(ctx.author.id)
    except Exception as e:
        log("Could not save yeet of {} to database, bechause of: ".format(ctx.author.id) + str(e))

    try:
        db_inc_been_yeet(user_to_yeet.id)
    except Exception as e:
        log("Could not save yeet of {} to database, bechause of: ".format(user_to_yeet.id) + str(e))
    #endregion

    # soft yeet
    if move_back:
        time.sleep(2) # wait for the soft time to finish
        try:
            await user_to_yeet.move_to(origin_channel) # move back to origin channel
        except Exception as e:
            log("Could not move {} back to origin, because of: {}".format(user_to_yeet, str(e)))
#endregion


def log(message):
    print("{}: {}".format(datetime.datetime.now(), message))

    
async def send_dm(user, message):
    try:
        dm_channel = user.dm_channel
        if dm_channel == None:
            dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except Exception as e:
        log("could not send dm to {}. See: {}".format(user, str(e)))
        return False
    
#endregion


#region bot & command


@bot.command()
async def yeethelp(ctx):
    embed=discord.Embed(title="Yeet Manual", url="https://github.com/mobergmann/mr-yeet#usage", description="This is a manual to improve your yeet skills.", color=0xff65c4)
    embed.add_field(name="/yeethelp", value="Prints a help page (in case you didn't notice, this page).", inline=False)
    embed.add_field(name="/yeet", value="Moves a random user into a channel called **YEET-LAUNCH** or if not exist into the guilds **AFK** channel.", inline=False)
    embed.add_field(name="/yeetsoft", value=" Like `/yeet` but moves the user back into the origin channel after 2 seconds.", inline=False)
    embed.add_field(name="/yeetkick", value=" Like `/yeet` but doesn't move the user into the yeet channel, instead disconnects the user from the server.", inline=False)
    embed.add_field(name="/yeetscore", value="Shows the yeet score of the caller.", inline=False)
    embed.set_footer(text="Good luck yeeting!")

    log("{} called yeethelp")
    
    try:
        await ctx.channel.send(embed=embed)
    except:
        log("yeethelp couldn't be send, because of: {}".format(str(e)))

        
@bot.command()
async def yeet(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx)

    
@bot.command()
async def yeetkick(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, should_kick=True)

    
@bot.command()
async def yeetsoft(ctx):
    if ctx.author.bot:
        return

    await _yeet(ctx, move_back=True)

    
@bot.command()
async def yeetscore(ctx):
    yeet_score = 0
    has_yeet = 0
    been_yeet = 0

    # get data from database an handle errors or no database entry
    data = None
    try:
        data = db_get_data(ctx.author.id)
    except Exception as e:
        log("Could no retrive database information of {}, because of {}".format(ctx.author, str(e)))
    if data == None:
        data = [ctx.author.id, 0, 0]

    # fill data into variables
    has_yeet = data[1]
    been_yeet = data[2]

    # when been_yeet == 0, then yeet_score := has_yeet / 1
    # otherwise yeet_score := has_yeet / (been_yeet * 0.3)
    if been_yeet == 0:
        yeet_score = has_yeet
    else:
        yeet_score = (has_yeet / been_yeet) + (has_yeet / 50)


    # get the yeet rank of the user
    yeet_rank = get_yeet_rank(yeet_score=yeet_score)

    # creating the yeat_score embed
    embed = discord.Embed(title = "Yeet Score: {}".format(round(yeet_score, 2)), color = 0xd97355)
    embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
    embed.add_field(name = "Times Yeetet", value = str(has_yeet), inline = False)
    embed.add_field(name = "Times been Yeetet", value = str(been_yeet), inline = False)
    embed.set_footer(text = "Your Yeet Rank is: \"{}\"".format(yeet_rank))

    # semding the score and logging
    try:
        await ctx.channel.send(embed=embed)
    except Exception as e:
        log("Could no send score of {}, because of {}".format(ctx.author, str(e)))

    log("{} retrieved its Yeets Score".format(ctx.author))

    
@bot.event
async def on_ready():
    log("Bot is running...")
    connect_db()
# endregion    
    
    
def main():
    log("Bot is starting...")
    bot.run(token)
    
   
if __name__ == "__main__":
    main()
