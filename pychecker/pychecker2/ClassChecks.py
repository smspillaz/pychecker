
from pychecker2.Check import Check
from pychecker2.Check import Warning
from pychecker2 import symbols
from pychecker2.util import BaseVisitor, parents, type_filter

from compiler.misc import mangle
from compiler import ast, walk

_ignorable = {}
for ignore in ['repr', 'dict', 'class', 'doc', 'str']:
    _ignorable['__%s__' % ignore] = 1

class GetDefs(BaseVisitor):
    "Record definitions of a attribute of self, who's name is provided"
    def __init__(self, name):
        self.selfname = name
        self.result = {}

    def visitAssAttr(self, node):
        if isinstance(node.expr, ast.Name) and \
           node.expr.name == self.selfname and \
           isinstance(node.parent, (ast.Assign, ast.AssTuple)):
            self.result[node.attrname] = node

class GetRefs(BaseVisitor):
    "Record references to a attribute of self, who's name is provided"
    def __init__(self, name):
        self.selfname = name
        self.result = {}

    def visitAssAttr(self, node):
        if isinstance(node.expr, ast.Name) and \
           node.expr.name == self.selfname:
            self.result[node.attrname] = node
        self.visitChildren(node)

    def visitGetattr(self, node):
        if isinstance(node.expr, ast.Name) and \
           node.expr.name == self.selfname:
            self.result[node.attrname] = node
        self.visitChildren(node)


def _get_methods(class_scope):
    return type_filter(class_scope.get_children(), symbols.FunctionScope)

def line(node):
    "find a node with a line number on it"
    for n in parents(node):
        if n.lineno is not None:
            return n
    return None

class NotSimpleName(Exception): pass

# compress Getattr(Getattr(Name(x), y), z) -> "x.y.z"
def get_name(node):
    if isinstance(node, ast.Getattr):
        return get_name(node.expr) + (node.attrname, )
    elif isinstance(node, ast.Name):
        return (node.name,)
    else:
        raise NotSimpleName

def get_base_names(scope):
    names = []
    for b in scope.node.bases:
        try:
            names.append(get_name(b))
        except NotSimpleName:       # FIXME: hiding expressions
            pass
    return names

def find_in_module(package, remotename, names, checker):
    # No other names, must be a remote value from the module
    if not names:
        f = checker.check_module(package)
        if f:
            return find_scope_going_down(f.root_scope, [remotename], checker)
        return None

    # complex name lookup
    #  first, get the real name of the package
    name = package.__name__
    if remotename:
        name += "." + remotename
    #  now import it, and chase down any other modules
    try:
        module = __import__(name, globals(), {}, [''])
        submodule = getattr(module, names[0], None)
        if type(submodule) == type(symbols):
            return find_in_module(submodule, None, names[1:], checker)
    except ImportError:
        return None
    
    #  object in the module is not another module, so chase down the source
    f = checker.check_module(module)
    if f:
        return find_scope_going_down(f.root_scope, names, checker)
    return None
                 
def find_scope_going_down(scope, names, checker):
    "Drill down scopes to find definition of x.y.z"
    root = names[0]
    for c in scope.get_children():
        if getattr(c, 'name', '') == root:
            if len(names) == 1:
                return c
            return find_scope_going_down(c, names[1:], checker)
    # Not defined here, check for import
    return find_imported_class(scope.imports, names, checker)

def find_imported_class(imports, names, checker):
    # may be defined by import
    for i in range(1, len(names) + 1):
        # try x, then x.y, then x.y.z as imported names
        try:
            name = ".".join(names[:i])
            ref = imports[name]
            # now look for the rest of the name
            result = find_in_module(ref.module, ref.remotename, names[i:], checker)
            if result:
                return result
        except KeyError:
            pass
    return None

def find_scope_going_up(scope, parts, checker):
    "Search up to find scope defining x of x.y.z"
    for p in parents(scope):
        if p.defs.has_key(parts[0]):
            return find_scope_going_down(p, parts, checker)
    return None

def get_base_classes(scope, checker):
    result = []
    for name in get_base_names(scope):
        base = find_scope_going_up(scope, name, checker)
        if base:
            result.append(base)
            result.extend(get_base_classes(base, checker))
    return result

def conforms(a, b):
    if len(a.node.argnames) != len(b.node.argnames):
        return None
    return a.node.kwargs == b.node.kwargs and a.node.varargs == b.node.varargs

class AttributeCheck(Check):
    "check `self.attr' expressions for attr"

    hasAttribute = Warning('Report unknown object attributes in methods',
                           'Class %s has no attribute %s')
    missingSelf = Warning('Report methods without "self"',
                          'Method %s is missing self parameter')
    methodRedefined = Warning('Report the redefinition of class methods',
                              'Method %s defined at line %d in '
                              'class %s redefined')
    signatureChanged = Warning('Report methods whose signatures do not '
                               'match base class methods',
                               'Signature does not match method '
                               '%s in base class %s')

    def check(self, file, checker):
        def visit_with_self(Visitor, method):
            # find self
            if not method.node.argnames:
                file.warning(method.node, self.missingSelf, method.node.name)
                return {}
            return walk(method.node, Visitor(method.node.argnames[0])).result

        # for all class scopes
        for scope in type_filter(file.scopes.values(), symbols.ClassScope):
            bases = get_base_classes(scope, checker)
            # get attributes defined on self
            attributes = {}             # "self.foo = " kinda things
            methods = {}                # methods -> scopes
            inherited = {}              # all class defs
            
            for m in _get_methods(scope):
                attributes.update(visit_with_self(GetDefs, m))
                methods[m.name] = m

            for base in [scope] + bases:
                for m in _get_methods(base):
                    attributes.update(visit_with_self(GetDefs, m))
                    if m.name != "__init__" and \
                       methods.has_key(m.name) and \
                       not conforms(m, methods[m.name]):
                        file.warning(methods[m.name].node,
                                     self.signatureChanged,
                                     m.name, base.name)
                    else:
                        methods[m.name] = m
                inherited.update(base.defs)

            # complain about defs with the same name as methods
            for name, node in attributes.items():
                try:
                    orig = methods[mangle(name, scope.name)]
                    file.warning(line(node), self.methodRedefined,
                                 name, orig.lineno, scope.name)
                    break
                except KeyError:
                    pass

            # find refs on self
            refs = []
            for m in _get_methods(scope):
                refs.extend(visit_with_self(GetRefs, m).items())

            # Now complain about refs on self that aren't known
            for name, node in refs:
                if not attributes.has_key(name) and \
                   not _ignorable.get(name, None) and \
                   not scope.defs.has_key(mangle(name, scope.name)) and \
                   not inherited.has_key(name):
                    file.warning(line(node), self.hasAttribute,
                                 scope.name, name)
