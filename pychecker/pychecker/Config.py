#!/usr/bin/env python

# Copyright (c) 2001-2002, MetaSlash Inc.  All rights reserved.

"""
Configuration information for checker.
"""

import sys
import os
import getopt
import string
import re
import time

_RC_FILE = ".pycheckrc"
CHECKER_VAR = '__pychecker__'
_VERSION = '0.8.11beta'

_DEFAULT_BLACK_LIST = [ "Tkinter", "wxPython", "gtk", "GTK", "GDK", ]
_DEFAULT_VARIABLE_IGNORE_LIST = [ '__version__', '__warningregistry__', 
                                  '__all__', '__credits__',
                                  '__author__', '__email__', ]
_DEFAULT_UNUSED_LIST = [ '_', 'empty', 'unused', 'dummy', ]

_OPTIONS = (
    ('Major Options', [
 ('e', 0, 'errors', None, 'turn off all warnings which are not likely errors'),
 ( '', 0, 'complexity', None, 'turn off all warnings which are related to complexity'),
 ('F', 1, 'config', None, 'specify .pycheckrc file to use'),
     ]),
    ('Error Control', [
 ('i', 0, 'import', 'importUsed', 'unused imports'),
 ('k', 0, 'pkgimport', 'packageImportUsed', 'unused imports from __init__.py'),
 ('M', 0, 'reimportself', 'reimportSelf', 'module imports itself'),
 ('X', 0, 'reimport', 'moduleImportErrors', 'reimporting a module'),
 ('x', 0, 'miximport', 'mixImport', 'module does import and from ... import'),
 ('l', 0, 'local', 'localVariablesUsed', 'unused local variables, except tuples'),
 ('t', 0, 'tuple', 'unusedLocalTuple', 'all unused local variables, including tuples'),
 ('9', 0, 'members', 'membersUsed', 'all unused class data members'),
 ('v', 0, 'var', 'allVariablesUsed', 'all unused module variables'),
 ('p', 0, 'privatevar', 'privateVariableUsed', 'unused private module variables'),
 ('g', 0, 'allglobals', 'reportAllGlobals', 'report each occurrence of global warnings'),
 ('n', 0, 'namedargs', 'namedArgs', 'functions called with named arguments (like keywords)'),
 ('a', 0, 'initattr', 'onlyCheckInitForMembers', 'Attributes (members) must be defined in __init__()'),
 ('I', 0, 'initsubclass', 'initDefinedInSubclass', 'Subclass.__init__() not defined'),
 ('u', 0, 'callinit', 'baseClassInitted', 'Baseclass.__init__() not called'),
 ('0', 0, 'abstract', 'abstractClasses', 'Subclass needs to override methods that only throw exceptions'),
 ('N', 0, 'initreturn', 'returnNoneFromInit', 'Return None from __init__()'),
 ('8', 0, 'unreachable', 'unreachableCode', 'unreachable code'),
 ('2', 0, 'constCond', 'constantConditions', 'a constant is used in a conditional statement'),
 ('1', 0, 'constant1', 'constant1', '1 is used in a conditional statement (if 1: or while 1:)'),
 ( '', 0, 'stringiter', 'stringIteration', 'check if iterating over a string'),
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
 ( '', 0, 'changetypes', 'inconsistentTypes', 'check if variables are set to different types'),
 ( '', 0, 'unpack', 'unpackNonSequence', 'check if unpacking a non-sequence'),
 ( '', 0, 'unpacklen', 'unpackLength', 'check if unpacking sequence with the wrong length'),
     ]),
    ('Possible Errors', [
 ('r', 0, 'returnvalues', 'checkReturnValues', 'check consistent return values'),
 ('C', 0, 'implicitreturns', 'checkImplicitReturns', 'check if using implict and explicit return values'),
 ('O', 0, 'objattrs', 'checkObjectAttrs', 'check that attributes of objects exist'),
 ('7', 0, 'slots', 'slots', 'various warnings about incorrect usage of __slots__'),
 ('3', 0, 'properties', 'classicProperties', 'using properties with classic classes'),
 ( '', 0, 'emptyslots', 'emptySlots', 'check if __slots__ is empty'),
 ('D', 0, 'intdivide', 'intDivide', 'check if using integer division'),
 ('w', 0, 'shadow', 'shadows', 'check if local variable shadows a global'),
     ]),
    ('Security', [
 ( '', 0, 'input', 'usesInput', 'check if input() is used'),
 ('6', 0, 'exec', 'usesExec', 'check if the exec statement is used'),
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
 ('5', 1, 'maxrefs', 'maxReferences', 'maximum # of identifier references (Law of Demeter)'),
 ('m', 0, 'moduledoc', 'noDocModule', 'no module doc strings'),
 ('c', 0, 'classdoc', 'noDocClass', 'no class doc strings'),
 ('f', 0, 'funcdoc', 'noDocFunc', 'no function/method doc strings'),
     ]),
    ('Debug', [
 ( '', 0, 'rcfile', None, 'print a .pycheckrc file generated from command line args'),
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
            if shortArg != '' :
                options['-' + shortArg] = opt
            options['--no-' + longArg] = options['--' + longArg] = opt

    return shortArgs, longArgs, options

_SHORT_ARGS, _LONG_ARGS, _OPTIONS_DICT = init()

def _getRCfiles(filename) :
    """Return a list of .rc filenames, on Windows use the current directory
                                       on UNIX use the user's home directory
    """

    files = []
    home = os.environ.get('HOME')
    if home :
        files.append(home + os.sep + filename)
    files.append(filename)
    return files


_RC_FILE_HEADER = '''#
# .pycheckrc file created by PyChecker v%s @ %s
#
# It should be placed in your home directory (value of $HOME).
# If $HOME is not set, it will look in the current directory.
#

'''

def outputRc(cfg) :
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
        self.membersUsed = 0
        self.importUsed = 1
        self.reimportSelf = 1
        self.moduleImportErrors = 1
        self.mixImport = 1
        self.packageImportUsed = 1
        self.localVariablesUsed = 1
        self.unusedLocalTuple = 0
        self.initDefinedInSubclass = 0
        self.baseClassInitted = 1
        self.abstractClasses = 1
        self.callingAttribute = 0
        self.classAttrExists = 1
        self.namedArgs = 0
        self.returnNoneFromInit = 1
        self.unreachableCode = 0
        self.constantConditions = 1
        self.constant1 = 0
        self.stringIteration = 1
        self.inconsistentTypes = 0
        self.unpackNonSequence = 1
        self.unpackLength = 1

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
        self.maxReferences = 5

        self.slots = 1
        self.emptySlots = 1
        self.classicProperties = 1
        self.checkObjectAttrs = 1
        self.checkReturnValues = 1
        self.checkImplicitReturns = 1
        self.intDivide = 1
        self.shadows = 1
        self.unaryPositive = 1
        self.modifyDefaultValue = 1
        self.usesExec = 0
        self.usesInput = 1

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

    def loadFiles(self, filenames, oldSuppressions = None) :
        if oldSuppressions is None :
            oldSuppressions = ({}, {})
        suppressions = oldSuppressions[0]
        suppressionRegexs = oldSuppressions[1]
        for filename in filenames:
            updates = self.loadFile(filename)
            suppressions.update(updates[0])
            suppressionRegexs.update(updates[1])
        return suppressions, suppressionRegexs

    def processArgs(self, argList, otherConfigFiles = None) :
        try :
            args, files = getopt.getopt(argList, _SHORT_ARGS, _LONG_ARGS)
        except getopt.error, detail :
            raise UsageError, detail

        quiet = self.quiet
        if otherConfigFiles is None:
            otherConfigFiles = []
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
                elif longArg == 'config' :
                    otherConfigFiles.append(value)
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
                elif longArg == 'complexity' :
                    self.__dict__.update(errors_only(2))
            elif value  :
                newValue = value
                memberType = type(getattr(self, member))
                if memberType == type(0) :
                    newValue = int(newValue)
                elif memberType == type([]) :
                    newValue = string.split(newValue, ',')
                setattr(self, member, newValue)
            elif arg[0:2] == '--' :
                setattr(self, member, arg[2:5] != 'no-')
            else :
                # for shortArgs we only toggle
                setattr(self, member, not getattr(self, member))

        self.quiet = quiet
        if self.variablesToIgnore.count(CHECKER_VAR) <= 0 :
            self.variablesToIgnore.append(CHECKER_VAR)

        return files

def errors_only(complexity = 0) :
    "Return {} of Config with all warnings turned off"
    dict = Config().__dict__
    for k, v in dict.items() :
        if type(v) == type(0) and v >= complexity :
            dict[k] = 0
    return dict


def printArg(shortArg, longArg, description, defaultValue, useValue) :
    defStr = ''
    shortArgStr = '   '
    if shortArg:
        shortArgStr = '-%s,' % shortArg

    if defaultValue != None :
        if not useValue :
            if defaultValue :
                defaultValue = 'on'
            else :
                defaultValue = 'off'
        defStr = ' [%s]' % defaultValue
    args = "%s --%s" % (shortArgStr, longArg)
    print "  %-18s %s%s" % (args, description, defStr)

def usage(cfg = None) :
    print "Usage for: checker.py [options] PACKAGE ...\n"
    print "    PACKAGEs can be a python package, module or filename\n"
    print "Long options can be preceded with no- to turn off (e.g., no-namedargs)\n"
    print "Category"
    print "  Options:           Change warning for ... [default value]"
    
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
        suppressions = cfg.loadFiles(_getRCfiles(_RC_FILE))
        otherConfigFiles = []
        files = cfg.processArgs(argList, otherConfigFiles)
        if otherConfigFiles:
            suppressions = cfg.loadFiles(otherConfigFiles, suppressions)
        return cfg, files, suppressions
    except UsageError :
        usage(cfg)
        raise

