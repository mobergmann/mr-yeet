#ifndef USER_H
#define USER_H

#include <cmath>
#include <dpp/dpp.h>


struct User
{
    dpp::snowflake id;
    unsigned long been_yeeted;
    unsigned long has_yeeted;
    bool immunity;

    double score() const
    {
        if (has_yeeted == 0) {
            return 0;
        }
        return (double)been_yeeted / (double)has_yeeted;
    }
};

#endif //USER_H
