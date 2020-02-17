import sys

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

    print('S -> F')

    # logical formulae rules
    print('F -> (F'+land+'F) | (F'+lor+'F) | (F'+implies+'F) | (F'+iff+'F) | '+neg+'F | QVF | E | P')

    # quantify formulae rule
    print('Q -> '+ exists + ' | '+ forall)

    # formulae rule
    print('F -> E | P')

    # equality atoms rule
    print('E -> (T'+eq+'T)')
    print('T -> C | V')

    # assign variables to predicate rule
    predicates = ''
    for p in P:
        predicates += p[0] + '(' + 'V, '*p[1]
        predicates = predicates[:-2]
        predicates += ') | '
        
    predicates = predicates[:-3]
    print('P -> '+predicates)

    # assign variable rule
    variables = ''
    for v in V:
        variables += v + ' | '

    variables = variables[:-3]
    print('V -> '+ variables)

    # assign constants rule
    constants = ''
    for c in C:
        constants += c + ' | '

    constants = constants[:-3]
    print('C -> '+ constants)

def lexical_analyzer(F, V, C, P, E, L, Q):
    max_length = 7 # maximum length of a valid lexeme
    lex_pointer = 0
    lexeme = ''
    token_array = []
    arity = 0

    for c in F:
        lexeme += c
        if lexeme == '(':
            token_array.append((lexeme, 'OB'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme == ')':
            token_array.append((lexeme, 'CB'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme == ',':
            if arity > 0:
                arity -= 1
            else:
                print('Lexical Analyzer throws error')
                sys.exit()
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme in V:
            token_array.append((lexeme, 'V'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme in C:
            token_array.append((lexeme, 'C'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        # checking for Predicates
        for p in P:
            if p[0] == lexeme:
                token_array.append((lexeme, 'P'))
                lex_pointer += len(lexeme)
                lexeme = ''
                arity = p[1]
                break
        if lexeme == '':
            continue
        
        if lexeme == E:
            token_array.append((lexeme, 'Eq'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme in L:
            token_array.append((lexeme, 'L'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if lexeme in Q:
            token_array.append((lexeme, 'Q'))
            lex_pointer += len(lexeme)
            lexeme = ''
            continue
        if len(lexeme) >= max_length:
            # invalid formula
            print('Lexical Analyzer throws error')
            sys.exit()
    return token_array

# read in varoables to V
# read in constants to C
# read in predicates to P
# read in equality to eq
# read in connectives to L in order land lor implies iff neg
# read in quantifiers to Q in order exists forall

V = ['x', 'y', 'z'] # variables are lower case
C = ['C', 'D'] # constants are upper case
P = [('P',2), ('Q',1)] # predicates are upper case
E = '='
L = ['land', 'lor', 'implies', 'iff', 'neg']
Q = ['exists', 'forall']

print_grammar(V, C, P, E, L, Q)

# read in formula to F

F = 'forall x ( exists y ( P(x,y) implies neg Q(x) ) lor exists z ( ( (C = z) land Q(z) ) land P(x,z) ) )'

# lexical analyzer

token_array = lexical_analyzer(''.join(F.split(' ')), V, C, P, E, L, Q)

print(token_array)

# syntax analyzer


