cmake_minimum_required(VERSION 3.28)

project(log4cxx)

set(CMAKE_CXX_STANDARD 17)

add_library(Log log.h Log4Cxx.h Log4Cxx.cpp)
