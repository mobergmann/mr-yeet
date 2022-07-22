#ifndef USER_H
#define USER_H

#include <dpp/dpp.h>


struct User
{
    dpp::snowflake id;
    unsigned long been_yeeted;
    unsigned long has_yeeted;
    bool immunity;

    unsigned long score() const
    {
        if (has_yeeted == 0) {
            return 0;
        }
        return been_yeeted / has_yeeted;
    }
};

#endif //USER_H
