
from pychecker2.Check import Check
from pychecker2.util import BaseVisitor

from compiler import walk, symbols, parseFile

import sys, os

class ImportCheck(Check):
    "Get 'from module import *' names hauled into the file and modules"

    def check(self, unused_modules, file, unused_options):

        class FromImportVisitor(BaseVisitor):

            # return default for any name that isn't "visitFrom"
            def __getattr__(self, name):
                if name == 'visitFrom':
                    return self.visitFrom
                return self.default

            # Add a scope, if the node corresponds to a new scope
            def default(self, node, *scopes):
                try:
                    scopes = scopes + (file.scopes[node],)
                except KeyError:
                    pass
                for c in node.getChildNodes():
                    self.visit(c, *scopes)

            def visitFrom(self, node, *scopes):
                if node.names[0][0] != '*':
                    return self.visitChildren(node)
                m = __import__(node.modname, globals(), {}, [None])
                scopes[-1].importStar[node.modname] = m

        if file.root_scope:
            walk(file.root_scope.node, FromImportVisitor())