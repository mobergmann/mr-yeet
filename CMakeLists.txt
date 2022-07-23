cmake_minimum_required(VERSION 3.22)
project(mr_yeet)

# set(CMAKE_CXX_STANDARD 23)

add_subdirectory(dependencies/DPP)
add_subdirectory(dependencies/SQLiteCpp)

#install(FILES yeet-sound.mp3 DESTINATION data) # todo also install/ move yeet-sound to build

add_executable(${PROJECT_NAME}
        include/User.h
        src/Database.cpp include/Database.h
        src/main.cpp
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
