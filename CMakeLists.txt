cmake_minimum_required(VERSION 3.3.0)
project(conan_abc)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if(MSVC)
    set(READLINE_FOUND FALSE)
else()
    set(READLINE_FOUND TRUE)
    set(ABC_READLINE_INCLUDE "${CONAN_INCLUDE_DIRS}")
    set(READLINE_LIBRARIES "${CONAN_LIBS}")
endif()

add_subdirectory("sources")
