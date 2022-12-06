set(MODULE_NAME "app")
set(EXECUTABLE_NAME "${PROJECT_NAME}-${MODULE_NAME}")
 
project(${EXECUTABLE_NAME})

add_executable(${EXECUTABLE_NAME})
target_sources(${EXECUTABLE_NAME}
    PRIVATE
        src/foo.c
        src/main.cpp
)

target_compile_options(${EXECUTABLE_NAME}
    PRIVATE 
        -Wall -Wextra  -Wno-c++98-compat
)

target_link_libraries(${EXECUTABLE_NAME}
    PRIVATE
        pantscc-core
)