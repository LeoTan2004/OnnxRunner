add_executable(MainTest OpenCVTest.cpp)
target_link_libraries(MainTest ${OpenCV_LIBRARIES})
add_test(Maintest MainTest)
