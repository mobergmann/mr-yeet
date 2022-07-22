cmake_minimum_required(VERSION 3.22)
project(mr_yeet)

# set(CMAKE_CXX_STANDARD 23)

add_subdirectory(dependencies/DPP)
add_subdirectory(dependencies/SQLiteCpp)

add_executable(${PROJECT_NAME}
        User.h
        Database.cpp Database.h
        main.cpp
        )

target_link_libraries(${PROJECT_NAME}
        dpp
        SQLiteCpp
        sqlite3
        pthread
        dl
        )

target_include_directories(${PROJECT_NAME} PRIVATE
        dependencies/DPP/include
        )

# Set C++ version
set_target_properties(${PROJECT_NAME} PROPERTIES
        CXX_STANDARD 23
        CXX_STANDARD_REQUIRED ON
        )
