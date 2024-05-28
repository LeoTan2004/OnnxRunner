cmake_minimum_required(VERSION 3.28)
project(Drone-Target)

set(CMAKE_CXX_STANDARD 17)

add_executable(${PROJECT_NAME} main.cpp)

target_link_libraries(${PROJECT_NAME} ${OPENVX_LIBRARIES} ${OpenCV_LIBRARIES})

