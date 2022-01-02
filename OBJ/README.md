# OBJect code files

We need a systematic approach to making translated object code
available for linking and running.  

## Examples of "real-world" approaches

Some examples from "real" 
systems: 

- C/Unix has a hotch-potch of schemes for finding object (.o) files
  and static and dynamic libraries (.a, lib, .dylib).  40+ years of 
  development, in which new approaches are added while old approaches
  are kept, will do that. 
- Windows has its own library search scheme, supported by Windows development
  tools; I have not studied it.
- Java has ".class" files and a `CLASSPATH` environment variable to
  tell tools where to look for the translated ".class" files.
  There are also conventions for organizing a directory hierarchy that
  echos the package structure, e.g., a class `org.uoregon.cis461.Example`
  should be found in `org/uoregon/cis461/Example.class` relative to a
  directory on the `CLASSPATH`. 
- Python stashes translated bytecode (.pyc) files in `__pycache__`.  It also
  has its own search scheme for finding imported modules.  It is apparently
  standard practice, and maybe even required, to modify the `PYTHONPATH` 
  variable from Python code, which to me looks like a failure to work out 
  a good general scheme. 

## A simple approach for the Tiny VM

For the tiny vm, I want to keep things as simple as possible, even if it does
not scale up well for large projects.  So, we will rely on one environment
variable, `TVMLIB`, indicating a path to one directory in which we will look
for `.json` files containing object code.  We will use the same `.json` files
whether we are looking for the information we need about imported modules for
translation, or whether we are looking for code to load into the virtual machine
for execution.  (In using the same object files for both, our approach is 
similar to Java and Python.)

By default we will use a directory called `OBJ`, and we will look for it 
within the current working directory. 

## Contents of the object directory

We will keep one `.obj` file for each class that may be loaded into the tiny
vm or imported during translation of another module. Each of the built-in
classes will also be represented by a `.obj` file, but these stub `.obj` files'
will not contain instructions for the built-in methods.  


