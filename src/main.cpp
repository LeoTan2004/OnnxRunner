#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

int main(int argc, char **argv) {
    // 读取图像
    Mat image = imread("../res/test-set/img/0005.jpg", IMREAD_COLOR);

    // 判断是否读取成功
    if (image.empty()) {
        cout << "Could not open or find the image" << endl;
        return -1;
    }

    // 显示图像
    imshow("Image", image);

    // 等待按键
    waitKey(0);

    return 0;
}
