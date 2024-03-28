# tiny_vm
A tiny virtual machine interpreter for Quack programs

## Work in progress

Originally the core of an interpreter for the Winter 2022
offering of CIS 461/561 compiler construction course at University of Oregon. 

Continuing development and revisions for Spring 2024 offering. 

## Building with CMake

These instructions should work in Linux and have been tested with
MacOS 13.5 (Ventura).  They should also work in the Linux subsystem
for Windows, although I have not tested there. 

### Dependencies

Make sure you have version 3.13 or later of _CMake_ installed.  (I
currently have version 3.28, so 3.13 or later should be easy to
satisfy.)    You can find _CMake_ distributions at
https://cmake.org/download/

You will also need the Unix utility _make_, which should be installed
by default in any Linux, MacOS, or other Unixoid system. 

### Steps

From the tiny_vm directory, execute these commands at the command line: 

```cli
cmake -Bcmake-build-debug -S.
cd cmake-build-debug
make
```

The first command (cmake) should produce output that looks something like this (with appropriate substitutions for your platform): 

```
volo:tiny_vm michal$ cmake -Bcmake-build-debug -S.
-- The C compiler identification is AppleClang 13.0.0.13000029
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Configuring done (0.5s)
-- Generating done (0.0s)
-- Build files have been written to: /Users/michal/Dropbox/24S-461-compilers/dev/tiny_vm/cmake-build-debug
```

The last command (make) should produce output that looks like this: 

```
volo:cmake-build-debug michal$ make
[  4%] Generating /Users/michal/Dropbox/24S-461-compilers/dev/tiny_vm/vm_code_table.c
INFO:__main__:Bytecode table generation
INFO:__main__:Finished bytecode table generation
[  9%] Building C object CMakeFiles/tiny_vm.dir/cjson/cJSON.c.o
[ 14%] Building C object CMakeFiles/tiny_vm.dir/main.c.o
[ 19%] Building C object CMakeFiles/tiny_vm.dir/vm_state.c.o
[ 23%] Building C object CMakeFiles/tiny_vm.dir/vm_ops.c.o
[ 28%] Building C object CMakeFiles/tiny_vm.dir/vm_code_table.c.o
[ 33%] Building C object CMakeFiles/tiny_vm.dir/builtins.c.o
[ 38%] Building C object CMakeFiles/tiny_vm.dir/vm_core.c.o
[ 42%] Building C object CMakeFiles/tiny_vm.dir/vm_loader.c.o
[ 47%] Building C object CMakeFiles/tiny_vm.dir/logger.c.o
[ 52%] Linking C executable /Users/michal/Dropbox/24S-461-compilers/dev/tiny_vm/bin/tiny_vm
[ 52%] Built target tiny_vm
[ 57%] Building C object CMakeFiles/test_roll.dir/cjson/cJSON.c.o
[ 61%] Building C object CMakeFiles/test_roll.dir/unit_tests/test_roll.c.o
[ 66%] Building C object CMakeFiles/test_roll.dir/vm_core.c.o
[ 71%] Building C object CMakeFiles/test_roll.dir/vm_state.c.o
[ 76%] Building C object CMakeFiles/test_roll.dir/builtins.c.o
[ 80%] Building C object CMakeFiles/test_roll.dir/vm_ops.c.o
[ 85%] Building C object CMakeFiles/test_roll.dir/logger.c.o
[ 90%] Building C object CMakeFiles/test_roll.dir/vm_code_table.c.o
[ 95%] Linking C executable /Users/michal/Dropbox/24S-461-compilers/dev/tiny_vm/bin/test_roll
[100%] Built target test_roll

```


Test the constructed  `test_roll` executable: 

```cli
bin/test_roll
```

You should get output that looks something like this: 

```
Testing the 'roll' operation
*DEBUG* : ===
*DEBUG* : -fp-> 0 : (int) 0
*DEBUG* :       1 : (int) 44
*DEBUG* :       2 : (int) 43
*DEBUG* :       3 : (int) 42
*DEBUG* :       4 : (int) 41
*DEBUG* :       5 : (int) 40
*DEBUG* : ===
Expected:  44 43 42 41 40
*DEBUG* : ===
*DEBUG* : -fp-> 0 : (int) 0
*DEBUG* :       1 : (int) 44
*DEBUG* :       2 : (int) 42
*DEBUG* :       3 : (int) 41
*DEBUG* :       4 : (int) 40
*DEBUG* :       5 : (int) 43
*DEBUG* : ===
Expected: 43 40 41 42 44
Finished testing the 'roll' operation.
```

###  Huh? What did we just do? 

Here's a little explanation of how _CMake_ and _make_ build the tiny vm. 

_CMake_ and _make_ are tools for building software in a Unix
or Unix-like environment.
_Make_ is the grandparent of all such tools.  _make_ reads a script
called a _Makefile_ which describes dependencies among program
artifacts  (source files, .o files, executables, etc).  It constructs
a tree of the dependencies, then executes commands in an order that
satisfies them, starting at the leaves and working up toward the
"target" of the build.    Incidentally, the _Makefile_ is an example
of a "little language" which is parsed and then interpreted by
_make_. 

_make_ was a great advance over manually invoking compiler commands
in the right order, or writing inflexible shell scripts, partly
because it inspected file modification dates to determine which
files really needed to be recompiled.  Before long,
though, _Makefile_ scripts became complicated enough that developers
wanted more. Dozens
of alternatives and extensions have been devised.  Some, like _Ant_, are
basically language-specific replacements for _make_.   Others, like
_Maven_ and _Gradle_, try to be more complete project management
tools, typically with lots of plug-in extensions.   Some replace
_make_, others build _Makefile_ scripts and then use _make_ for
the compilation step.  _CMake_ is an example of the latter, a more
sophisticated build tool that is designed particularly for C++
applications (but capable of building C applications as well),
which builds a _Makefile_.

_CMake_ is particularly useful for "out of source" builds, that is,
for keeping generated files separate from files that are under source
control (that is, stored and versioned in the git repository).
_CMake_ is also good at dealing with some common portability issues,
such as important library files being located in different places
depending on which version of an operating system one is working
with.  These are reasons I selected _CMake_ for the tiny vm. 

Another very important reason I chose _CMake_:
I knew that many graduate
students in our department are already familiar with _CMake_.  I will
never be more than minimally competent with any sophisticated build
tool.  When one cannot build deep expertise, it is important to have
access to experts.

### The executable binaries

The `tiny_vm/bin` directory should now contain two executable programs. 

- `test_roll` is a tiny test program, a "smoke test" that does not thoroughly test the tiny virtual machine, but is likely to fail if the build went horribly wrong. 
- `tiny_vm` is the tiny virtual machine that will execute instructions that we generate, first for a calculator and later for Quack programs. 




