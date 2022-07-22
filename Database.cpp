#include "Database.h"

SQLite::Database Database::database = SQLite::Database("database.sqlite3", SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE);


Database::Database()
{
    auto statement =
        "CREATE TABLE IF NOT EXISTS 'users' ( "
        "   'id'            INTEGER NOT NULL UNIQUE, "
        "   'has_yeeted'    INTEGER NOT NULL DEFAULT 0, "
        "   'been_yeeted'   INTEGER NOT NULL DEFAULT 0, "
        "   'immunity'      INTEGER NOT NULL DEFAULT 0, "
        "   PRIMARY KEY('id') "
        ")";
    SQLite::Statement query(Database::database, statement);

    query.exec();
}

User Database::get_user(dpp::snowflake user_id)
{
    SQLite::Statement query(Database::database, "SELECT id, has_yeeted, been_yeeted, immunity FROM users WHERE id == :user_id");
    query.bind(":user_id", std::to_string(user_id));

    User user{};
    // Loop to execute the query step by step, to get one a row of results at a time
    while (query.executeStep())
    {
        user.id = query.getColumn(0).getUInt();
        user.has_yeeted = query.getColumn(1).getUInt();
        user.been_yeeted = query.getColumn(2).getUInt();
        user.immunity = query.getColumn(3).getUInt();
    }

    return user;
}

void Database::increase_has_yeeted(dpp::snowflake user_id)
{
    // todo transaction
    auto statement1 = "INSERT OR IGNORE INTO users (id) VALUES (:user_id)";
    auto statement2 = "UPDATE users SET has_yeeted = has_yeeted + 1 WHERE id = :user_id";

    SQLite::Statement query1(Database::database, statement1);
    query1.bind(":user_id", std::to_string(user_id));

    SQLite::Statement query2(Database::database, statement2);
    query2.bind(":user_id", std::to_string(user_id));

    query1.exec();
    query2.exec();
}

void Database::increase_been_yeeted(dpp::snowflake user_id)
{
    // todo transaction
    auto statement1 = "INSERT OR IGNORE INTO users (id) VALUES (:user_id)";
    auto statement2 = "UPDATE users SET been_yeeted = been_yeeted + 1 WHERE id = :user_id";

    SQLite::Statement query1(Database::database, statement1);
    query1.bind(":user_id", std::to_string(user_id));

    SQLite::Statement query2(Database::database, statement2);
    query2.bind(":user_id", std::to_string(user_id));

    query1.exec();
    query2.exec();
}

void Database::forget(dpp::snowflake user_id)
{
    auto statement = "DELETE FROM users WHERE id = :user_id";
    SQLite::Statement query(Database::database, statement);
    query.bind(":user_id", std::to_string(user_id));

    query.exec();
}

void Database::set_immunity(dpp::snowflake user_id)
{
    // todo transaction
    auto statement1 = "INSERT OR IGNORE INTO users (id) VALUES (:user_id)";
    auto statement2 = "UPDATE users SET immunity = 1 WHERE id = :user_id";

    SQLite::Statement query1(Database::database, statement1);
    query1.bind(":user_id", std::to_string(user_id));

    SQLite::Statement query2(Database::database, statement2);
    query2.bind(":user_id", std::to_string(user_id));

    query1.exec();
    query2.exec();
}

void Database::remove_immunity(dpp::snowflake user_id)
{
    // todo transaction
    auto statement1 = "INSERT OR IGNORE INTO users (id) VALUES (:user_id)";
    auto statement2 = "UPDATE users SET immunity = 0 WHERE id = :user_id";

    SQLite::Statement query1(Database::database, statement1);
    query1.bind(":user_id", std::to_string(user_id));

    SQLite::Statement query2(Database::database, statement2);
    query2.bind(":user_id", std::to_string(user_id));

    query1.exec();
    query2.exec();
}
