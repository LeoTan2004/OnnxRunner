// Define this in only one file to add 'main'
#define CATCH_CONFIG_MAIN
// include the Catch framework
#include <catch.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

TEST_CASE("MainTest", "[test,label]") {
    Mat image = imread("../../../tests/res/img/0005.jpg", IMREAD_COLOR);
    REQUIRE_FALSE(image.empty());

}
