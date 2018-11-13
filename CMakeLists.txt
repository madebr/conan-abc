cmake_minimum_required(VERSION 3.3.0)
project(conan_abc)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_definitions(${CONAN_DEFINES})
include_directories(${CONAN_INCLUDE_DIRS})
link_libraries(${CONAN_LIBS})

add_subdirectory("sources")
