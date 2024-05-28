project(Drone-Test)

# 使得测试文件夹下的所有源码均可以向使用库函数一样引入catch.hpp
include_directories(CATCH2 PRIVATE /home/leo/Project/Project/Python/drone/tests/include)

add_subdirectory(opencv)

