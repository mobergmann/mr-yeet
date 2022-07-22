#ifndef DATABASE_H
#define DATABASE_H

#include <dpp/dpp.h>
#include <SQLiteCpp/SQLiteCpp.h>
#include <SQLiteCpp/VariadicBind.h>

#include "User.h"

class Database
{
    static SQLite::Database database;

public:
    Database();

    User get_user(dpp::snowflake user_id);

    void increase_has_yeeted(dpp::snowflake user_id);
    void increase_been_yeeted(dpp::snowflake user_id);

    void forget(dpp::snowflake user_id);

    void set_immunity(dpp::snowflake user_id);
    void remove_immunity(dpp::snowflake user_id);
};


#endif //DATABASE_H
