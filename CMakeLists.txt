cmake_minimum_required(VERSION 3.28)
project(Drone
        VERSION 0.1
        LANGUAGES C CXX
)

set(CMAKE_CXX_STANDARD 17)
find_package(OpenCV REQUIRED)
add_subdirectory(src)

option(BUILD_TEST "Whether or not to build the tests" OFF)
if (${BUILD_TEST})
    message(STATUS "Building tests")
    enable_testing()
    add_subdirectory(tests)
endif ()
