#!/usr/bin/env python

# Copyright (c) 2001, MetaSlash Inc.  All rights reserved.

"""
Object to hold information about functions.
Also contain a pseudo Python function object
"""

import string

_ARGS_ARGS_FLAG = 4
_KW_ARGS_FLAG = 8


class FakeFunction :
    "This is a holder class for turning code at module level into a function"

    def __init__(self, name, code, func_globals = {}) :
        self.func_name = self.__name__ = name
        self.func_doc  = self.__doc__  = "ignore"

        self.func_code = code
        self.func_defaults = None
        self.func_globals = func_globals


class Function :
    "Class to hold all information about a function"

    def __init__(self, function, isMethod = None) :
        self.function = function
        self.maxArgs = function.func_code.co_argcount
        if isMethod :
            self.maxArgs = self.maxArgs - 1
        self.minArgs = self.maxArgs
        if function.func_defaults != None :
            self.minArgs = self.minArgs - len(function.func_defaults)
        # if function uses *args, there is no max # args
        if function.func_code.co_flags & _ARGS_ARGS_FLAG != 0 :
            self.maxArgs = None
        self.supportsKW = function.func_code.co_flags & _KW_ARGS_FLAG

    def isParam(self, name) :
        numArgs = self.function.func_code.co_argcount
        if self.maxArgs is None :
            numArgs = numArgs + 1
        if self.supportsKW :
            numArgs = numArgs + 1
        return name in self.function.func_code.co_varnames[:numArgs]

def create_fake(name, code, func_globals = {}) :
    return Function(FakeFunction(name, code, func_globals))

def create_from_file(file, filename, module) :
    # Make sure the file is at the beginning
    #   if python compiled the file, it will be at the end
    file.seek(0)

    # Read in the source file, see py_compile.compile() for games w/src str
    codestr = file.read()
    codestr = string.replace(codestr, "\r\n", "\n")
    codestr = string.replace(codestr, "\r", "\n")
    if codestr and codestr[-1] != '\n' :
        codestr = codestr + '\n'
    code = compile(codestr, filename, 'exec')
    return Function(FakeFunction('__main__', code, module.__dict__))


