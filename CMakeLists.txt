cmake_minimum_required(VERSION 3.6)
project(codevs_st)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")

set(SOURCE_FILES main.cpp)
add_executable(codevs_st ${SOURCE_FILES})