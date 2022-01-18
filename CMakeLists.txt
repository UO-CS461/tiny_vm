cmake_minimum_required(VERSION 3.19)
project(tiny_vm C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)  # No apparent effect

# Very simple JSON library for loader
find_package(cJSON CONFIG REQUIRED)

add_custom_command(
        OUTPUT  ${CMAKE_SOURCE_DIR}/vm_code_table.c
        COMMAND python3 ${CMAKE_SOURCE_DIR}/build_bytecode_table.py
            ${CMAKE_SOURCE_DIR}/opdefs.txt
            ${CMAKE_SOURCE_DIR}/vm_code_table.c
        MAIN_DEPENDENCY ${CMAKE_SOURCE_DIR}/opdefs.txt
        DEPENDS ${CMAKE_SOURCE_DIR}/build_bytecode_table.py
        DEPENDS ${CMAKE_SOURCE_DIR}/vm_code_table.h
)

add_executable(tiny_vm
        main.c
        vm_state.c vm_state.h
        vm_ops.c vm_ops.h
        vm_code_table.h
        vm_code_table.c  # Generated
        builtins.c builtins.h
        vm_core.h vm_core.c
        vm_loader.c vm_loader.h
        logger.c logger.h)

target_include_directories(tiny_vm PRIVATE ${CJSON_INCLUDE_DIRS})
target_link_libraries(tiny_vm PRIVATE cjson)

# Unit tests as C code
add_executable(test_roll
        unit_tests/test_roll.c
        vm_core.c vm_core.h
        vm_state.c vm_state.h
        builtins.c builtins.h
        vm_ops.c vm_ops.h
        logger.c logger.h
        vm_code_table.c vm_code_table.h
        )

target_include_directories(test_roll
        PRIVATE ${CJSON_INCLUDE_DIRS},
        ${CMAKE_SOURCE_DIR}
        )
target_link_libraries(test_roll PRIVATE cjson)
