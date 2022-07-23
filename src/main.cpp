#include <iostream>
#include <iomanip>
#include <random>
#include <cmath>

#include <dpp/dpp.h>

#include "../include/User.h"
#include "../include/Database.h"


/// Global random device, used for generating unique random numbers
std::random_device device;
/// Global random number generator, used for generating unique random numbers
std::mt19937 random_number_generator(device());

/// Stores the actual yeet sound file
uint8_t* robot = nullptr;
/// Size of the yeet sound file
size_t robot_size = 0;

/// The time interval in seconds, how long the user should remain in the afk channel
const int yeet_waiting_time = 2;


void yeet(const dpp::slashcommand_t &event, dpp::cluster& cluster)
{
    Database db;

    auto author = event.command.member;
    User db_author{};
    try
    {
        db_author = db.get_user(author.user_id);
    }
    catch (std::exception &e)
    {
        event.reply("Error communicating with the database. Please contact the maintainer.");
        return;
    }

    // check if author has immunity activated and skip if so
    if (db_author.immunity)
    {
        event.reply("You have **immunity enabled** and therefore cannot yeet. **Disable** immunity first.");
        return;
    }

    // try to retrieve guild from cache
    auto guild = dpp::find_guild(event.command.guild_id);
    if (not guild)
    {
        event.reply("Could not find this guild...");
        return;
    }

    // get voice channel where the user is also connected to
    std::vector<dpp::user> users;
    dpp::snowflake origin_channel;
    // filter only the members, connected to our channel
    {
        auto unfiltered_users = guild->voice_members;

        // search current channel
        for (const auto &user: unfiltered_users)
        {
            if (user.second.user_id == author.user_id)
            {
                origin_channel = user.second.channel_id;
                break;
            }
        }

        // filter only the users connected to the current channel
        for (const auto &user: unfiltered_users)
        {
            if (user.second.channel_id == origin_channel)
            {
                try
                {
                    // don't add user, which are immune to yeet
                    if (db.get_user(user.second.user_id).immunity)
                    {
                        continue;
                    }
                }
                catch (std::exception &e)
                {
                    event.reply("Error communicating with the database. Please contact the maintainer.");
                    return;
                }

                auto _user = dpp::find_user(user.second.user_id);
                // skip users which cannot be retrieved, so we can dereference
                if (not _user)
                {
                    continue;
                }

                users.push_back(*_user);
            }
        }
    }

    // ensure that yeeting only possible with more than 1 user
    if (users.size() <= 1)
    {
        event.reply("You have to be at **least two people** in a voice channel, which have **immunity turned off**.");
        return;
    }

    // get a random user from users, which should be yeeted
    std::uniform_int_distribution<std::mt19937::result_type> distribution(0, users.size());
    auto random_yeet_user = users[distribution(random_number_generator)];

    // increase yeet scores
    try
    {
        db.increase_been_yeeted(random_yeet_user.id);
        db.increase_has_yeeted(author.user_id);
    }
    catch (std::exception &e)
    {
        event.reply("Error communicating with the database. Please contact the maintainer.");
        return;
    }

    // move user into akf
    auto afk_channel = guild->afk_channel_id;
    // no need to move user back, so don't bother
    if (not afk_channel)
    {
        cluster.guild_member_move(afk_channel, guild->id, random_yeet_user.id, [event](auto callback){
            if (callback.is_error())
            {
                event.reply("An error occurred. Please contact the maintainer.");
                return;
            }
        });
    }
    else
    {
        cluster.guild_member_move(afk_channel, guild->id, random_yeet_user.id,
            [&cluster, event, author, random_yeet_user, origin_channel, guild](auto callback)
        {
            // catch callback errors
            if (callback.is_error())
            {
                event.reply("An error occurred. Please contact the maintainer.");
                return;
            }

#pragma region play sound file
                if (!guild->connect_member_voice(author.user_id))
                {
                    event.reply("An error occurred connecting to your voice channel. Please contact the maintainer.");
                    return;
                }

                dpp::voiceconn* v = event.from->get_voice(guild->id);
                if (v && v->voiceclient && v->voiceclient->is_ready())
                {
                    v->voiceclient->send_audio_raw((uint16_t*)robot, robot_size);
                    // todo disconnect
                    event.from->disconnect_voice(guild->id);
                }
#pragma endregion

            // send yeet message and special message when author yeeted itself
            if (author.user_id == random_yeet_user.id)
            {
                event.reply(author.get_mention() + std::string(" has yeeted itself."));
            }
            else
            {
                event.reply(author.get_mention() + std::string(" yeeted ") + random_yeet_user.get_mention());
            }

            // todo
            //  // dont need to move, when user has already moved
            //  if () {}

            // wait the afk time penalty
            new dpp::oneshot_timer(&cluster, yeet_waiting_time,
                [&cluster, event, origin_channel, guild, random_yeet_user](auto callback)
            {
                // move user back to original channel
                cluster.guild_member_move(origin_channel, guild->id, random_yeet_user.id,
                    [event](auto callback)
                {
                    // catch callback errors
                    if (callback.is_error())
                    {
                        event.reply("An error occurred. Could not move the user back.");
                        return;
                    }
                });
            });
        });
    }
}

void score(const dpp::slashcommand_t &event)
{
    Database db;

    User user{};
    try
    {
        user = db.get_user(event.command.member.user_id);
    }
    catch (std::exception &e)
    {
        event.reply("Error communicating with the database. Please contact the maintainer.");
        return;
    }

    std::string rank = std::to_string(user.score());
    std::ostringstream oss;
    oss << std::setprecision(2) << std::noshowpoint << user.score();
    std::string score = oss.str();

    auto embed = dpp::embed()
        .set_title("Yeet Profile")
        .set_description("Your Score is **" + score + "** therefore is your Rank *" + rank + "*!")
        .add_field("Has Yeeted", std::to_string(user.has_yeeted), false)
        .add_field("Been Yeeted", std::to_string(user.been_yeeted), false)
        .add_field("Currently immune", user.immunity ? "True" : "False", false);

    auto msg = dpp::message(event.command.msg.channel_id, embed);
    event.reply(msg);
}

void forget(const dpp::slashcommand_t &event)
{
    Database db;
    try
    {
        db.forget(event.command.member.user_id);
    }
    catch (std::exception &e)
    {
        event.reply("Error communicating with the database. Please contact the maintainer.");
        return;
    }

    event.reply("All your Data has been removed.");
}

void immunity(const dpp::slashcommand_t &event)
{
    Database db;
    bool choice = std::get<bool>(event.get_parameter("value"));
    try
    {
        if (choice)
        {
            db.set_immunity(event.command.member.user_id);
            event.reply("You are now **immune** to yeets, but **cannot yeet** anymore.");
        }
        else
        {
            db.remove_immunity(event.command.member.user_id);
            event.reply("You are **no longer immune** to yeets, but **can yeet** again.");
        }
    }
    catch (std::exception &e)
    {
        event.reply("Error communicating with the database. Please contact the maintainer.");
        return;
    }
}

int main()
{
#pragma region load yeet sound
    // according to: https://dpp.dev/soundboard.html
    std::ifstream input("../resources/yeet-sound.wav", std::ios::in|std::ios::binary|std::ios::ate);
    if (input.is_open())
    {
        robot_size = input.tellg();
        robot = new uint8_t[robot_size];
        input.seekg(0, std::ios::beg);
        input.read((char*)robot, robot_size);
        input.close();
    }
    else
    {
        std::cerr << "Could not open yeet soundfile." << std::endl;
        return EXIT_FAILURE;
    }
#pragma endregion

    dpp::cluster bot("MTAwMDA0MDUxMjM4NTk3ODM5OQ.G0tNrg.F4IVqGj6kbsKOufLjt99jCP9zxN2w0ikAphH5k");

    bot.on_log(dpp::utility::cout_logger());

    bot.on_slashcommand([&bot](const dpp::slashcommand_t &event)
    {
        auto command = event.command.get_command_name();

        if (command == "yeet")
        {
            yeet(event, bot);
        }
        else if (command == "score")
        {
            score(event);
        }
        else if (command == "forget")
        {
            forget(event);
        }
        else if (command == "immunity")
        {
            immunity(event);
        }
    });

    bot.on_ready([&bot](const dpp::ready_t &event)
    {
        if (dpp::run_once<struct register_bot_commands>())
        {
            dpp::slashcommand yeet_command(
                "yeet",
                "Moves a random user, who is connected to the same voice channel as you, to the AFK channel "
                "(or disconnects them from voice, if no channel exists)",
                bot.me.id);

            dpp::slashcommand score_command(
                "score",
                "Displays your personal yeet score",
                bot.me.id);

            dpp::slashcommand forget_command(
                "forget",
                "Deletes all your data from the database (WARNING: this will also remove your score)",
                bot.me.id);

            dpp::slashcommand immunity_command(
                "immunity",
                "Grants immunity to you, so you cannot be yeeted, but you also CANNO'T yeet anymore",
                bot.me.id);
            immunity_command.add_option(
                dpp::command_option(
                    dpp::co_boolean, "value", "Weather the immunity should be toggled on or off.", true));

            // Register the command
            bot.guild_command_create(yeet_command, 502183046594691072);
            // bot.global_command_create(yeet_command);
            bot.guild_command_create(score_command, 502183046594691072);
            // bot.global_command_create(score_command);
            bot.guild_command_create(forget_command, 502183046594691072);
            // bot.global_command_create(forget_command);
            bot.guild_command_create(immunity_command, 502183046594691072);
            // bot.global_command_create(immunity_command);
        }
    });

    bot.start(dpp::st_wait);

    return 0;
}
