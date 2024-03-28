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

Make sure you have version 3.13 or later of CMake installed.  (I
currently have version 3.28, so 3.13 or later should be easy to
satisfy.)    You can find CMake distributions at
https://cmake.org/download/

You will also need the Unix utility Make, which should be installed
by default in any Linux, MacOS, or other Unixoid system. 

### Steps

From the tiny_vm directory, execute these commands at the command line: 

```cli
cmake -Bcmake-build-debug -S.
make -f cmake-build-debug/Makefile
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

Here's a little explanation of how CMake and Make build the tiny vm. 

_CMake_ and _make_ are tools for building software in a Unix environment.
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
wanted more. 

After _make_ established the usefulness of project build tools, dozens
of alternatives and extensions were devised.  Some, like _Ant_, are
basically language-specific replacements for _make_.   Others, like
_Maven_ and _Gradle_, try to be more complete project management
tools, typically with lots of plug-in extensions.   Some replace
_make_, others use build _Makefile_ scripts and then use _make_ for
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

There is one other very important reason for choosing _CMake_:
I knew that many graduate
students in our department are already familiar with _CMake_.  I will
never be more than minimally competent with any sophisticated build
tool.  When one cannot build deep expertise, it is important to have
access to experts.


