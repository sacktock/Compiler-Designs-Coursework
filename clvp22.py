import sys
import re
from datetime import datetime


def write_error(error):
    print(error)
    f = open('parser.log', 'a')
    f.write('Execution at '+str(datetime.now()) +':\n')
    f.write('error occured - '+error+'\n')
    f.write('\n')
    f.close()
    sys.exit()
    
def read_input_file(F, V, C, P, E, L, Q, file_name):
    reg_expr = re.compile('[a-zA-Z0-9_]')
    FILE = None
    try:
        FILE = open(file_name)
    except:
        print('could not open the specified input file ...')
        sys.exit()
    for line in FILE:
        lst = line.rstrip().split(' ')
        if lst[0] == 'variables:':
            V = lst[1:]
            for v in V:
                if not bool(re.match(reg_expr, v)):
                    write_error('variable name contains illegal characters ...')
        elif lst[0] == 'constants:':
            C = lst[1:]
            for c in C:
                if not bool(re.match(reg_expr, c)):
                    write_error('constant name contains illegal characters ...')
        elif lst[0] == 'predicates:':
            for i in range(1, len(lst)):
                try:
                    P.append((lst[i][:-3], int(lst[i][lst[i].index('[')+1:lst[i].index(']')])))
                except:
                    write_error('error in input file - predicate given a non integer arity ..')
                    
            for p in P:
                if not bool(re.match(reg_expr, p[0])):
                    write_error('predicate name contains illegal characters ..')
        elif lst[0] == 'equality:':
            try:
                E = lst[1]
            except:
                write_error('no equality symbol given ...')
        elif lst[0] == 'connectives:':
            try:
                L = lst[1:6]
            except:
                write_error('some connectives missing in the input file ..')
        elif lst[0] == 'quantifiers:':
            try:
                Q = lst[1:3]
            except:
                write_error('some quantifiers missing in the input file ...')
        elif lst[0] == 'formula:':
            F = ''.join(lst[1:])
        elif F:
            F += ''.join(lst)

    if not E:
        write_error('no equality symbol given ...')

    if len(L) != 5:
        write_error('incorrect number of connectives in the input file ...')

    if len(Q) != 2:
        write_error('incorrect number of quantifiers in the input file ...')

    if set(V).intersection(set(C)):
        write_error('some variables and constants given the same name ...')

    if set(V).intersection(set(L)):
        write_error('some variables and connectives given the same name ...')

    if set(C).intersection(set(L)):
        write_error('some constants and connectives given the same name ...')

    if set(V).intersection(set(Q)):
        write_error('some variables and quantifiers given the same name ...')

    if set(C).intersection(set(Q)):
        write_error('some constants and quantifiers given the same name ...')

    if set(L).intersection(set(Q)):
        write_error('some connectives and quantifiers given the same name ...')

    if len(set(C)) != len(C):
        write_error('duplicated constant names in the input file ... ')

    if len(set(V)) != len(V):
        write_error('duplicated variable names in the input file ... ')

    if len(set([p[0] for p in P])) != len([p[0] for p in P]):
        write_error('duplicated predicate names in the input file ... ')

    if len(set(L)) != len(L):
        write_error('duplicated connective names in the input file ... ')

    if len(set(Q)) != len(L):
        write_error('duplicated quantifier names in the input file ... ')

    if E in V or E in C or E in Q or E in L:
        write_error('equality symbol given the same name somewhere else ...')
        
    for p in P:
        if p[0] in V:
            write_error('some variables and predicates given the same name ...')
        if p[0] in C:
            write_error('some constants and predicates given the same name ...')
        if p[0] in L:
            write_error('some connectives and predicates given the same name ...')
        if p[0] in Q:
            write_error('some quantifiers and predicates given the same name ...')
        if p[0] == E:
            write_error('equality symbol and predicate given the same name ...')
    FILE.close()
    return F, V, C, P, L, Q, E
    
def print_grammar(V, C, P, E, L, Q):
    # get the logical connectives and quantifiers
    eq = E
    land = L[0]
    lor = L[1]
    implies = L[2]
    iff = L[3]
    neg = L[4]

    exists = Q[0]
    forall = Q[1]

    print('S -> Formula')

    # logical formulae rules
    print('Formula -> (Expression) | '+neg+'Formula | QuantifierVariableFormula | Predicate')

    # quantify formulae rule
    print('Quantifier -> '+ exists + ' | '+ forall)

    # equality atoms rule
    print('Expression -> Term'+eq+'Term | FormulaConnectiveFormula')
    print('Term -> Constant | Variable')

    print('Connective -> '+land+' | '+lor+' | '+implies+' | '+iff)
    # assign variables to predicate rule
    predicates = ''
    for p in P:
        predicates += p[0] + '(' + 'Var, '*p[1]
        predicates = predicates[:-2]
        predicates += ') | '
        
    predicates = predicates[:-3]
    print('Predicate -> '+predicates)

    # assign variable rule
    variables = ''
    for v in V:
        variables += v + ' | '

    variables = variables[:-3]
    print('Variable -> '+ variables)

    # assign constants rule
    constants = ''
    for c in C:
        constants += c + ' | '

    constants = constants[:-3]
    print('Constant -> '+ constants)

def lexical_analyzer(F, V, C, P, E, L, Q):
    max_length = 0 # maximum length of a valid lexeme
    for v in V:
        if len(v) > max_length:
            max_length = len(v)
    for c in C:
        if len(c) > max_length:
            max_length = len(c)
    for p in P:
        if len(p[0]) > max_length:
            max_length = len(p[0])
    if len(E) > max_length:
        max_length = len(E)
    for l in L:
        if len(l) > max_length:
            max_length = len(l)
    for q in Q:
        if len(q) > max_length:
            max_length = len(q)
        
    lex_pointer = 0
    lexeme = ''
    token_array = []
    arity = 0

    i = 0
    j = max_length

    while i < len(F):
        while j > 0:
            lexeme = F[i:i+j]
            if lexeme == '(':
                token_array.append((lexeme, 'OpenBracket'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme == ')':
                if arity > 0:
                    write_error('Predicate given too few variables ...')
                token_array.append((lexeme, 'CloseBracket'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme == ',':
                if arity > 0:
                    arity -= 1
                else:
                    write_error('Unexpected character ","  - Predicate could have been given too many variables ...')
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in V:
                token_array.append((lexeme, 'Variable'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in C:
                token_array.append((lexeme, 'Constant'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            # checking for Predicates
            for p in P:
                if p[0] == lexeme:
                    token_array.append((lexeme, 'Predicate', p[1]))
                    i += len(lexeme)
                    j = max_length
                    lexeme = ''
                    arity = p[1] - 1
                    break
            if lexeme == E:
                token_array.append((lexeme, 'Equality'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in L:
                if lexeme == L[4]:
                    token_array.append((lexeme, 'Negation', L.index(lexeme)))
                else:
                    token_array.append((lexeme, 'Connective', L.index(lexeme)))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in Q:
                token_array.append((lexeme, 'Quantifier', Q.index(lexeme)))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            j -= 1
        if i < len(F):
            write_error('Unexpected character "' + F[i]+ '" at ' + str(i)+'  ...')
        
    return token_array

# read in variables to V
# read in constants to C
# read in predicates to P
# read in equality to eq
# read in connectives to L in order land lor implies iff neg
# read in quantifiers to Q in order exists forall

# read in formula to F

V, C, P, L, Q = [], [], [], [], []
E = ''
F = ''

file_name = 'example.txt'

F, V, C, P, L, Q, E = read_input_file(F, V, C, P, E, L, Q, file_name)

print_grammar(V, C, P, E, L, Q)

# lexical analyzer

if F == '':
    print('no formula given')
    sys.exit()
    
token_array = lexical_analyzer(F, V, C, P, E, L, Q)

# syntax analyzer

token_array += [('EOF', 'EOF')]

I = 0
lookahead = token_array[I]
arity = 0

def Formula():
    global lookahead
    if lookahead[0] == '(':
        match('OpenBracket')
        Expression()
        match('CloseBracket')
    elif lookahead[0] == L[4]: # equal to negation
        match('Negation')
        Formula()
    elif lookahead[0] in Q:
        Quantifier()
        Variable()
        Formula()
    elif [p for p in P if p[0] == lookahead [0]]:
        Predicate()
    elif lookahead[0] == 'EOF':
        return
    else:
        write_error('syntax error ... could not match '+lookahead[0] +' in Formula')
            
def Expression():
    global lookahead
    if lookahead[0] in C or lookahead[0] in V:
        Term()
        match('Equality')
        Term()
    else:
        Formula()
        Connective()
        Formula()

def Term():
    global lookahead
    if lookahead[0] in C:
        Constant()
    elif lookahead[0] in V:
        Variable()
    else:
        write_error('syntax error ... could not match '+lookahead[0] +' in Term')

def Predicate():
    global arity
    match('Predicate')
    match('OpenBracket')
    for _ in range(arity):
        Variable()
    match('CloseBracket')
    
def Quantifier():
    match('Quantifier')

def Connective():
    match('Connective')

def Variable():
    match('Variable')

def Constant():
    match('Constant')

def match(token_type):
    global lookahead
    global arity
    if (lookahead[1] == token_type):
        if token_type == 'Predicate':
            try:
                arity = lookahead[2]
            except:
                write_error('internal parser error ... could not get arity of predicate '+lookahead[0])
        next_token()
    else:
        write_error('syntax error ... could not match '+lookahead[0] +' to '+token_type)
        
def next_token():
    global lookahead
    global I
    try:
        I += 1
        lookahead = token_array[I]
    except:
        write_error('syntax error ... parser expected additional tokens ... ')
    
Formula()
# construct and print the parse tree as we go along ...

if lookahead[0] != 'EOF':
    write_error('syntax error ... parser given additional tokens ... ')
else:
    print('Formula is syntactically correct ... ')
    f = open('parser.log', 'a')
    f.write('Execution at '+str(datetime.now()) +':\n')
    f.write('The formula was syntactically correct\n')
    f.write('\n')
    f.close()
    # save the valid parse tree
    sys.exit()


    
