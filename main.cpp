#include <iostream>
#include <random>
#include <dpp/dpp.h>

#include "User.h"
#include "Database.h"


std::random_device device;
std::mt19937 random_number_generator(device());

void yeet(const dpp::slashcommand_t &event)
{
    Database db;

    auto author = event.command.member;

    // try to retrieve guild from cache
    auto guild = dpp::find_guild(event.command.guild_id);
    if (not guild)
    {
        event.reply("Could not find the requested guild.");
        return;
    }

    // get voice channel where the user is also connected to
    std::vector<dpp::user> users;
    // filter only the members, connected to our channel
    {
        auto _users = guild->voice_members;

        // search current channel
        dpp::snowflake channel_id;
        for (const auto &user: _users)
        {
            if (user.second.user_id == author.user_id)
            {
                channel_id = user.second.channel_id;
                break;
            }
        }

        // filter only the users connected to the current channel
        for (const auto &user: _users)
        {
            if (user.second.channel_id == channel_id)
            {
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

    if (users.size() <= 1)
    {
        event.reply("You need friends to summon me, go find some!");
        return;
    }

    // get a random user from users, which should be yeeted
    std::uniform_int_distribution<std::mt19937::result_type> distribution(0, users.size());
    auto random_yeet_user = users[distribution(random_number_generator)];

    // increase yeet scores
    db.increase_been_yeeted(random_yeet_user.id);
    db.increase_has_yeeted(author.user_id);

    // move user into akf
    auto afk_channel = dpp::find_channel(guild->afk_channel_id);
    if (afk_channel)
    {
        // todo
        // random_yeet_user.move_voice(afk_channel);
    }
    else
    {
        // todo
        // random_yeet_user.disconnect();
    }

    // special message, if author yeeted itself
    if (author.user_id == random_yeet_user.id)
    {
        event.reply(author.get_mention() + std::string(" has yeeted itself."));
    }
    else
    {
        event.reply(author.get_mention() + std::string(" yeeted ") + random_yeet_user.get_mention());
    }
}

void score(const dpp::slashcommand_t &event)
{
    Database db;
    auto user = db.get_user(event.command.member.user_id);
    auto rank = std::to_string(user.score());

    auto embed = dpp::embed()
        .set_title("Yeet Profile")
        .set_description("Your Score is **" + std::to_string(user.score()) + "** therefore is your Rank *" + rank + "*!")
        .add_field("Has Yeeted", std::to_string(user.has_yeeted), false)
        .add_field("Been Yeeted", std::to_string(user.been_yeeted), false);

    auto msg = dpp::message(event.command.msg.channel_id, embed).set_reference(event.command.msg.id);
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
    dpp::cluster bot("MTAwMDA0MDUxMjM4NTk3ODM5OQ.G0tNrg.F4IVqGj6kbsKOufLjt99jCP9zxN2w0ikAphH5k");

    bot.on_log(dpp::utility::cout_logger());

    bot.on_slashcommand([&bot](const dpp::slashcommand_t &event)
    {
        auto command = event.command.get_command_name();

        if (command == "yeet")
        {
            yeet(event);
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
