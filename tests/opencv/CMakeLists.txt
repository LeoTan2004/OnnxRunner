add_executable(MainTest main-test.cpp)
target_link_libraries(MainTest ${OpenCV_LIBRARIES})
add_test(Maintest MainTest)
