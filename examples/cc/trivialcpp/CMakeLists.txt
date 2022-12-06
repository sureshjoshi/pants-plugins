set(MODULE_NAME "trivialcpp")
set(EXECUTABLE_NAME "${PROJECT_NAME}-${MODULE_NAME}")
 
project(${EXECUTABLE_NAME})

add_executable(${EXECUTABLE_NAME})
target_sources(${EXECUTABLE_NAME}
    PRIVATE
        src/main.cpp
)

target_compile_options(${EXECUTABLE_NAME}
    PRIVATE 
        -Wall -Wextra  -Wno-c++98-compat
)
