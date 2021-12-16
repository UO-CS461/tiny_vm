cmake_minimum_required(VERSION 3.19)
project(tiny_vm C)
set(CMAKE_C_STANDARD 11)

add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/vm_code_table.c
        COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/opdefs.txt ${CMAKE_CURRENT_BINARY_DIR}/vm_code_table.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/opdefs.txt
)

add_executable(tiny_vm
        main.c
        vm_state.c
        vm_ops.c vm_ops.h
        vm_code_table.h
        vm_bytecodes.c vm_bytecodes.h
        builtins.c builtins.h
        vm_core.h)

add_executable(array_ptrs
        experiments/array_ptr_refs.c
        )