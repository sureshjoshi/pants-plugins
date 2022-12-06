cmake_minimum_required(VERSION 3.19)

project(pantscc
    LANGUAGES
        C CXX
    VERSION
        0.0.1
)

set(CMAKE_VERBOSE_MAKEFILE TRUE)
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib) 
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON) # Don't fallback if CXX_STANDARD not found
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(app)
add_subdirectory(core)
add_subdirectory(trivialc)
add_subdirectory(trivialcpp)
