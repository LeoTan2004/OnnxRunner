cmake_minimum_required(VERSION 3.28)
project(Drone)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)

if(DEFINED OPENVX_INCLUDES)
    message(STATUS "OPENVX_INCLUDES: \t${OPENVX_INCLUDES}")
    include_directories(${OPENVX_INCLUDES})
else()
    message(STATUS "OPENVX_INCLUDES: \t<empty>")
endif()

if(DEFINED OPENVX_LIBRARIES)
    message(STATUS "OPENVX_LIBRARIES: \t${OPENVX_LIBRARIES}")
else()
    message(STATUS "OPENVX_LIBRARIES: \t<empty>")
endif()

add_executable(Drone src/main.cpp)

target_link_libraries(${PROJECT_NAME} ${OPENVX_LIBRARIES} ${OpenCV_LIBRARIES})
