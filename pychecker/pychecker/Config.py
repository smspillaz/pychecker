#!/usr/bin/env python

# Copyright (c) 2001, MetaSlash Inc.  All rights reserved.

"""
Configuration information for checker.
"""

import sys
import os
import getopt
import string
import re

_RC_FILE = ".pycheckrc"
CHECKER_VAR = '__pychecker__'
_VERSION = '0.8.5'

_DEFAULT_BLACK_LIST = [ "Tkinter", "wxPython", "gtk", "GTK", "GDK", ]
_DEFAULT_VARIABLE_IGNORE_LIST = [ '__version__', '__warningregistry__', 
                                  '__all__', ]
_DEFAULT_UNUSED_LIST = [ '_', 'empty', 'unused', 'dummy', ]

_OPTIONS = (
    ('Major Options', [
 ('e', 0, 'errors', None, 'turn off all warnings which are not likely errors'),
 ('s', 0, 'doc', None, 'turn off all warnings for no doc strings'),
 ('m', 0, 'moduledoc', 'noDocModule', 'no module doc strings'),
 ('c', 0, 'classdoc', 'noDocClass', 'no class doc strings'),
 ('f', 0, 'funcdoc', 'noDocFunc', 'no function/method doc strings'),
     ]),
    ('Error Control', [
 ('i', 0, 'import', 'importUsed', 'unused imports'),
 ('k', 0, 'pkgimport', 'packageImportUsed', 'unused imports from __init__.py'),
 ('M', 0, 'reimportself', 'reimportSelf', 'module imports itself'),
 ('X', 0, 'reimport', 'moduleImportErrors', 'reimporting a module'),
 ('x', 0, 'miximport', 'mixImport', 'module does import and from ... import'),
 ('l', 0, 'local', 'localVariablesUsed', 'unused local variables, except tuples'),
 ('t', 0, 'tuple', 'unusedLocalTuple', 'all unused local variables, including tuples'),
 ('v', 0, 'var', 'allVariablesUsed', 'all unused module variables'),
 ('p', 0, 'privatevar', 'privateVariableUsed', 'unused private module variables'),
 ('g', 0, 'allglobals', 'reportAllGlobals', 'report each occurrence of global warnings'),
 ('n', 0, 'namedargs', 'namedArgs', 'functions called with named arguments (like keywords)'),
 ('a', 0, 'initattr', 'onlyCheckInitForMembers', 'Attributes (members) must be defined in __init__()'),
 ('I', 0, 'initsubclass', 'initDefinedInSubclass', 'Subclass.__init__() not defined'),
 ('u', 0, 'callinit', 'baseClassInitted', 'Subclass.__init__() not called'),
 ('N', 0, 'initreturn', 'returnNoneFromInit', 'Return None from __init__()'),
 ('A', 0, 'callattr', 'callingAttribute', 'Calling data members as functions'),
 ('y', 0, 'classattr', 'classAttrExists', 'class attribute does not exist'),
 ('S', 1, 'self', 'methodArgName', 'First argument to methods'),
 ('T', 0, 'argsused', 'argumentsUsed', 'unused method/function arguments'),
 ('z', 0, 'varargsused', 'varArgumentsUsed', 'unused method/function variable arguments'),
 ('G', 0, 'selfused', 'ignoreSelfUnused', 'ignore if self is unused in methods'),
 ('o', 0, 'override', 'checkOverridenMethods', 'check if overridden methods have the same signature'),
 ('U', 0, 'reuseattr', 'redefiningFunction', 'check if function/class/method names are reused'),
 ('Y', 0, 'positive', 'unaryPositive', 'check if using unary positive (+) which is usually meaningless'),
 ('j', 0, 'moddefvalue', 'modifyDefaultValue', 'check if modify (call method) on a parameter that has a default value'),
     ]),
    ('Possible Errors', [
 ('r', 0, 'returnvalues', 'checkReturnValues', 'check consistent return values'),
 ('C', 0, 'implicitreturns', 'checkImplicitReturns', 'check if using implict and explicit return values'),
 ('O', 0, 'objattrs', 'checkObjectAttrs', 'check that attributes of objects exist'),
 ('D', 0, 'intdivide', 'intDivide', 'check if using integer division'),
     ]),
    ('Suppressions', [
 ('q', 0, 'stdlib', 'ignoreStandardLibrary', 'ignore warnings from files under standard library'),
 ('b', 1, 'blacklist', 'blacklist', 'ignore warnings from the list of modules\n\t\t\t'),
 ('Z', 1, 'varlist', 'variablesToIgnore', 'ignore global variables not used if name is one of these values\n\t\t\t'),
 ('E', 1, 'unusednames', 'unusedNames', 'ignore unused locals/arguments if name is one of these values\n\t\t\t'),
     ]),
    ('Complexity', [
 ('L', 1, 'maxlines', 'maxLines', 'maximum lines in a function'),
 ('B', 1, 'maxbranches', 'maxBranches', 'maximum branches in a function'),
 ('R', 1, 'maxreturns', 'maxReturns', 'maximum returns in a function'),
 ('J', 1, 'maxargs', 'maxArgs', 'maximum # of arguments to a function'),
 ('K', 1, 'maxlocals', 'maxLocals', 'maximum # of locals in a function'),
     ]),
    ('Debug', [
 ('F', 0, 'rcfile', None, 'print a .pycheckrc file generated from command line args'),
 ('P', 0, 'printparse', 'printParse', 'print internal checker parse structures'),
 ('d', 0, 'debug', 'debug', 'turn on debugging for checker'),
 ('Q', 0, 'quiet', None, 'turn off all output except warnings'),
 ('V', 0, 'version', None, 'print the version of PyChecker and exit'),
     ])
)

def init() :
    GET_OPT_VALUE = (('', ''), (':', '='),)
    shortArgs, longArgs = "", []
    for _, group in _OPTIONS :
        for opt in group:
            optStr = GET_OPT_VALUE[opt[1]]
            shortArgs = shortArgs + opt[0] + optStr[0]
            longArgs.append(opt[2] + optStr[1])
            longArgs.append('no-' + opt[2] + optStr[1])

    options = {}
    for _, group in _OPTIONS :
        for opt in group:
            shortArg, useValue, longArg, member, description = opt
            options['-' + shortArg] = opt
            options['--no-' + longArg] = options['--' + longArg] = opt

    return shortArgs, longArgs, options

_SHORT_ARGS, _LONG_ARGS, _OPTIONS_DICT = init()

def _getRCfile(filename) :
    """Return the .rc filename, on Windows use the current directory
                                on UNIX use the user's home directory"""

    # FIXME: this is really cheating, but should work for now
    home = os.environ.get('HOME')
    if home :
        filename = home + os.sep + filename
    return filename


_RC_FILE_HEADER = '''#
# .pycheckrc file created by PyChecker v%s @ %s
#
# It should be placed in your home directory (value of $HOME).
# If $HOME is not set, it will look in the current directory.
#

'''

def outputRc(cfg) :
    import time
    output = _RC_FILE_HEADER % (_VERSION, time.ctime(time.time()))
    for name, group in _OPTIONS :
        for opt in group:
            shortArg, useValue, longArg, member, description = opt
            if member is None :
                continue
            description = string.strip(description)
            value = getattr(cfg, member)
            optStr = '# %s\n%s = %s\n\n' % (description, member, `value`)
            output = output + optStr

    return output
        

class UsageError(Exception) :
    """Exception to indicate that the application should exit due to
       command line usage error."""

_SUPPRESSIONS_ERR = \
'''\nWarning, error processing defaults file: %s
\%s must be a dictionary ({}) -- ignoring suppressions\n'''

def _getSuppressions(name, dict, filename) :
    suppressions = dict.get(name, {})
    if type(suppressions) != type({}) :
        print _SUPPRESSIONS_ERR % (filename, name)
        suppressions = {}
    return suppressions


class Config :
    "Hold configuration information"

    def __init__(self) :
        "Initialize configuration with default values."

        self.debug = 0
        self.quiet = 0
        self.onlyCheckInitForMembers = 0
        self.printParse = 0

        self.noDocModule = 0
        self.noDocClass = 0
        self.noDocFunc = 0

        self.reportAllGlobals = 0
        self.allVariablesUsed = 0
        self.privateVariableUsed = 1
        self.importUsed = 1
        self.reimportSelf = 1
        self.moduleImportErrors = 1
        self.mixImport = 1
        self.packageImportUsed = 1
        self.localVariablesUsed = 1
        self.unusedLocalTuple = 0
        self.initDefinedInSubclass = 0
        self.baseClassInitted = 1
        self.callingAttribute = 0
        self.classAttrExists = 1
        self.namedArgs = 1
        self.returnNoneFromInit = 1

        self.unusedNames = _DEFAULT_UNUSED_LIST
        self.variablesToIgnore = _DEFAULT_VARIABLE_IGNORE_LIST
        self.blacklist = _DEFAULT_BLACK_LIST
        self.ignoreStandardLibrary = 0
        self.methodArgName = 'self'
        self.checkOverridenMethods = 1

        self.argumentsUsed = 1
        self.varArgumentsUsed = 1
        self.ignoreSelfUnused = 0
        self.redefiningFunction = 1

        self.maxLines = 200
        self.maxBranches = 50
        self.maxReturns = 10
        self.maxArgs = 10
        self.maxLocals = 40

        self.checkObjectAttrs = 1
        self.checkReturnValues = 1
        self.checkImplicitReturns = 0
        self.intDivide = 1
        self.unaryPositive = 1
        self.modifyDefaultValue = 1

    def loadFile(self, filename) :
        suppressions = {}
        suppressionRegexs = {}
        try :
            tmpGlobal, dict = {}, {}
            execfile(filename, tmpGlobal, dict)
            for key, value in dict.items() :
                if self.__dict__.has_key(key) :
                    self.__dict__[key] = value
                elif key not in ('suppressions', 'suppressionRegexs') :
                    print "Warning, option (%s) doesn't exist, ignoring" % key

            suppressions = _getSuppressions('suppressions', dict, filename)
            regexs = _getSuppressions('suppressionRegexs', dict, filename)
            for regex_str in regexs.keys() :
                regex = re.compile(regex_str)
                suppressionRegexs[regex] = regexs[regex_str]
        except IOError :
            pass       # ignore if no file
        except Exception, detail:
            print "Warning, error loading defaults file:", filename, detail
        return suppressions, suppressionRegexs

    def processArgs(self, argList) :
        try :
            args, files = getopt.getopt(argList, _SHORT_ARGS, _LONG_ARGS)
        except getopt.error, detail :
            raise UsageError, detail

        quiet = self.quiet
        for arg, value in args :
            shortArg, useValue, longArg, member, description = _OPTIONS_DICT[arg]
            if member == None :
                # FIXME: this whole block is a hack
                if longArg == 'rcfile' :
                    sys.stdout.write(outputRc(self))
                    continue
                elif longArg == 'quiet' :
                    quiet = 1
                    continue
                elif longArg == 'version' :
                    # FIXME: it would be nice to define this in only one place
                    print _VERSION
                    sys.exit(0)

                self.noDocModule = 0
                self.noDocClass = 0
                self.noDocFunc = 0
                if longArg == 'errors' :
                    self.__dict__.update(errors_only())
            elif value  :
                newValue = value
                memberType = type(getattr(self, member))
                if memberType == type(0) :
                    newValue = int(newValue)
                elif memberType == type([]) :
                    newValue = string.split(newValue, ',')
                setattr(self, member, newValue)
            elif arg[0:5] == '--no-' :
                setattr(self, member, 0)
            elif arg[0:2] == '--' :
                setattr(self, member, 1)
            else :
                # for shortArgs we only toggle
                setattr(self, member, not getattr(self, member))

        self.quiet = quiet
        if self.variablesToIgnore.count(CHECKER_VAR) <= 0 :
            self.variablesToIgnore.append(CHECKER_VAR)

        return files

def errors_only() :
    "Return {} of Config with all warnings turned off"
    dict = Config().__dict__
    for k, v in dict.items() :
        if type(v) == type(0) :
            dict[k] = 0
    return dict


def printArg(shortArg, longArg, description, defaultValue, useValue) :
    defStr = ''
    if defaultValue != None :
        if not useValue :
            if defaultValue :
                defaultValue = 'on'
            else :
                defaultValue = 'off'
        defStr = ' [%s]' % defaultValue
    args = "-%s, --%s" % (shortArg, longArg)
    print "  %-18s %s%s" % (args, description, defStr)

def usage(cfg = None) :
    print "Usage for: checker.py [options] PACKAGE ...\n"
    print "    PACKAGEs can be a python package, module or filename\n"
    print "Long options can be preceded with no- to turn off (e.g., no-namedargs)\n"
    print "Category and"
    print "Options:               Change warning for ... [default value]"
    
    if cfg is None :
        cfg = Config()
    for name, group in _OPTIONS :
        print
        print name + ":"
        for opt in group:  
            shortArg, useValue, longArg, member, description = opt
            defValue = None
            if member != None :
                defValue = cfg.__dict__[member]

            printArg(shortArg, longArg, description, defValue, useValue)


def setupFromArgs(argList) :
    "Returns (Config, [ file1, file2, ... ]) from argList"

    cfg = Config()
    try :
        suppressions = cfg.loadFile(_getRCfile(_RC_FILE))
        return cfg, cfg.processArgs(argList), suppressions
    except UsageError :
        usage(cfg)
        raise

