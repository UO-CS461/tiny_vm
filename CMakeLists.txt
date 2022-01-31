cmake_minimum_required(VERSION 3.13)
project(tiny_vm C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)  # No apparent effect

add_custom_command(
        OUTPUT  ${CMAKE_SOURCE_DIR}/vm_code_table.c
        COMMAND python3 ${CMAKE_SOURCE_DIR}/build_bytecode_table.py
            ${CMAKE_SOURCE_DIR}/opdefs.txt
            ${CMAKE_SOURCE_DIR}/vm_code_table.c
        MAIN_DEPENDENCY ${CMAKE_SOURCE_DIR}/opdefs.txt
        DEPENDS ${CMAKE_SOURCE_DIR}/build_bytecode_table.py
        DEPENDS ${CMAKE_SOURCE_DIR}/vm_code_table.h
)

include_directories(PRIVATE ${CMAKE_SOURCE_DIR} ${PROJECT_SOURCE_DIR} "cjson")

add_executable(tiny_vm
        cjson/cJSON.c cjson/cJSON.h
        main.c
        vm_state.c vm_state.h
        vm_ops.c vm_ops.h
        vm_code_table.h
        vm_code_table.c  # Generated
        builtins.c builtins.h
        vm_core.h vm_core.c
        vm_loader.c vm_loader.h
        logger.c logger.h)

# Unit tests as C code
add_executable(test_roll
        cjson/cJSON.c cjson/cJSON.h
        unit_tests/test_roll.c
        vm_core.c vm_core.h
        vm_state.c vm_state.h
        builtins.c builtins.h
        vm_ops.c vm_ops.h
        logger.c logger.h
        vm_code_table.c vm_code_table.h
        )

