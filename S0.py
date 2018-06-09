
import os,sys

SRC = open(sys.argv[0]+'.src','r').read()

class Qbject:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.value = V
        self.attr = {}
        self.nest = []
        
    def __repr__(self): return self.dump()
    def dump(self,depth=0,prefix=''):
        S = self.pad(depth) + self.head(prefix)
        for i in self.attr:
            S += self.attr[i].dump(depth+1,prefix='%s = ' % i)
        for j in self.nest:
            S += j.dump(depth+1)
        return S
    def head(self,prefix=''): return '%s<%s:%s>' % (prefix, self.type, self.value)
    def pad(self,N): return '\n'+'\t'*N
    
    def __setitem__(self,key,o): self.attr[key] = o ; return self
    def __getitem__(self,key): return self.attr[key]
    def __lshift__(self,o): return self.push(o)
    def push(self,o): self.nest.append(o) ; return self
    def pop(self): return self.nest.pop()
    def top(self): return self.nest[-1]
    
class Primitive(Qbject): pass
class Symbol(Primitive): pass
class String(Primitive): pass
class Number(Primitive):
    def __init__(self,V): Primitive.__init__(self, float(V))
class Integer(Number):
    def __init__(self,V): Primitive.__init__(self, int(V))

class Container(Qbject): pass    
class Stack(Container): pass
class Map(Container):
    def __lshift__(self,o): F = VM(o) ; self.attr[F.value] = F

class Active(Qbject): pass
class Function(Active):
    def __init__(self,F):
        Active.__init__(self, F.__name__)
        self.fn = F
class VM(Function): ' VM command '

D = Stack('DATA')
W = Map('FORTH')

W['STAGE'] = Integer(0)

def q(): print D
W['?'] = VM(q)

def wq(): print W
W['w?'] = VM(wq)

def qq(): q() ; wq() ; BYE()
W['??'] = VM(qq)

def BYE(): sys.exit(0)
# W << BYE

import ply.lex as lex

tokens = ['symbol','number']

t_ignore = ' \t\r\n'
t_ignore_COMMENT = '\#.*\n'

def t_number(t):
    r'[\+\-]?[0-9]+(\.[0-9]*)?([eE][\+\-]?[0-9]+)?'
    return Number(t.value)

def t_symbol(t):
    r'[a-zA-Z0-9_]+'
    return Symbol(t.value)

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()

def WORD():
    token = lexer.token()
    if token: D << token
    return token
W << WORD

def FIND(): return W[D.pop().value]
W << FIND

def INTERPRET(src=SRC):
    lexer.input(src)
    while True:
        WORD()
        if not WORD(): break;
        if D.top().type in ['symbol']: FIND()
        print D
    qq()
W << INTERPRET
INTERPRET(SRC)
