set(MODULE_NAME "core")
set(LIBRARY_NAME "${PROJECT_NAME}-${MODULE_NAME}")
 
project(${LIBRARY_NAME})

add_library(${LIBRARY_NAME} STATIC)
target_sources(${LIBRARY_NAME}
    PRIVATE
        src/greeter.c
)

target_include_directories(${LIBRARY_NAME}
    PUBLIC
        include
)

target_compile_options(${LIBRARY_NAME}
    PRIVATE 
        -Wall -Wextra  -Wno-c++98-compat
)


