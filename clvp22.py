import sys
import re

def read_input_file(F, V, C, P, E, L, Q, file_name):
    reg_expr = re.compile('[a-zA-Z0-9_]')
    FILE = None
    try:
        FILE = open(file_name)
    except:
        print('could not open the specified input file')
        sys.exit()
    for line in FILE:
        lst = line.rstrip().split(' ')
        if lst[0] == 'variables:':
            V = lst[1:]
            for v in V:
                if not bool(re.match(reg_expr, v)):
                    print('variable name contains illegal characters')
                    sys.exit()
        elif lst[0] == 'constants:':
            C = lst[1:]
            for c in C:
                if not bool(re.match(reg_expr, c)):
                    print('constant name contains illegal characters')
                    sys.exit()
        elif lst[0] == 'predicates:':
            for i in range(1, len(lst)):
                try:
                    P.append((lst[i][:-3], int(lst[i][lst[i].index('[')+1:lst[i].index(']')])))
                except:
                    print('error in input file - predicate given a non integer arity')
                    sys.exit()
                    
            for p in P:
                if not bool(re.match(reg_expr, p[0])):
                    print('predicate name contains illegal characters')
                    sys.exit()
        elif lst[0] == 'equality:':
            try:
                E = lst[1]
            except:
                print('no equality symbol given')
                sys.exit()
        elif lst[0] == 'connectives:':
            try:
                L = lst[1:6]
            except:
                print('some connectives misisng in the input file')
                sys.exit()
        elif lst[0] == 'quantifiers:':
            try:
                Q = lst[1:3]
            except:
                print('some quantifiers missing in the input file')
                sys.exit()
        elif lst[0] == 'formula:':
            F = ''.join(lst[1:])
        elif F:
            F += ''.join(lst)

    if E == []:
        print('no equality symbol given')
        sys.exit()

    if L == []:
        print('some connectives misisng in the input file')
        sys.exit()

    if Q == []:
        print('some quantifiers missing in the input file')
        sys.exit()

    if set(V).intersection(set(C)):
        print('some variables and constants given the same name')
        sys.exit()

    if set(V).intersection(set(L)):
        print('some variables and connectives given the same name')
        sys.exit()

    if set(C).intersection(set(L)):
        print('some constants and connectives given the same name')
        sys.exit()

    if set(V).intersection(set(Q)):
        print('some variables and quantifiers given the same name')
        sys.exit()

    if set(C).intersection(set(Q)):
        print('some constants and quantifiers given the same name')
        sys.exit()

    if set(L).intersection(set(Q)):
        print('some connectives and quantifiers given the same name')
        sys.exit()

    if E in V or E in C or E in Q or E in L:
        print('equality symbol given the same name somewhere else')
        sys.exit()
        
    for p in P:
        if p[0] in V:
            print('some variables and predicates given the same name')
            sys.exit()
        if p[0] in C:
            print('some constants and predicates given the same name')
            sys.exit()
        if p[0] in L:
            print('some connectives and predicates given the same name')
            sys.exit()
        if p[0] in Q:
            print('some quantifiers and predicates given the same name')
            sys.exit()
        if p[0] == E:
            print('equality symbol and predicate given the same name')
            sys.exit()
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

    print('S -> Form')

    # logical formulae rules
    print('Form -> (Form'+land+'Form) | (Form'+lor+'Form) | (Form'+implies+'Form) | (Form'+iff+'Form) | '+neg+'Form | QuanVarForm | Expr | Pred')

    # quantify formulae rule
    print('Quan -> '+ exists + ' | '+ forall)

    # equality atoms rule
    print('Expr -> (Term'+eq+'Term)')
    print('Term -> Const | Var')

    # assign variables to predicate rule
    predicates = ''
    for p in P:
        predicates += p[0] + '(' + 'Var, '*p[1]
        predicates = predicates[:-2]
        predicates += ') | '
        
    predicates = predicates[:-3]
    print('Pred -> '+predicates)

    # assign variable rule
    variables = ''
    for v in V:
        variables += v + ' | '

    variables = variables[:-3]
    print('Var -> '+ variables)

    # assign constants rule
    constants = ''
    for c in C:
        constants += c + ' | '

    constants = constants[:-3]
    print('Const -> '+ constants)

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
                token_array.append((lexeme, 'OpenBr'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme == ')':
                if arity > 0:
                    print('Predicate given too few variables')
                    sys.exit()
                token_array.append((lexeme, 'CloseBr'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme == ',':
                if arity > 0:
                    arity -= 1
                else:
                    print('Unexpected character ","  - Predicate could have been given too many variables')
                    sys.exit()
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in V:
                token_array.append((lexeme, 'Var'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in C:
                token_array.append((lexeme, 'Const'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            # checking for Predicates
            for p in P:
                if p[0] == lexeme:
                    token_array.append((lexeme, 'Pred', p[1]))
                    i += len(lexeme)
                    j = max_length
                    lexeme = ''
                    arity = p[1] - 1
                    break
            if lexeme == E:
                token_array.append((lexeme, 'Equal'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in L:
                token_array.append((lexeme, 'Log', L.index(lexeme)))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in Q:
                token_array.append((lexeme, 'Quan', Q.index(lexeme)))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            j -= 1
        if i < len(F):
            print('Unexpected character "' + F[i]+ '" at ' + str(i))
            sys.exit()
        
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
print()
print(token_array)

# syntax analyzer

i = 0
j = 0

prod_rules = ['S', 'Form']
next_prod = 'Form'

def recursive_parsing(prod_rules, token_array, i):

    curr_prod = prod_rules[-1]
    n_term = ''
    for i in range(0, len(curr_prod)):
        if 'Form' in curr_prod[:i]:
            n_term = 'Form'
            break
        if 'Quan' in curr_prod[:i]:
            n_term = 'Quan'
            break
        if 'Expr' in curr_prod[:i]:
            n_term = 'Expr'
            break
        if 'Pred' in curr_prod[:i]:
            n_term = 'Pred'
            break
        if 'Var' in curr_prod[:i]:
            n_term = 'Var'
            break
        if 'Term' in curr_prod[:i]:
            n_term = 'Term'
            break
        if 'Const' in curr_prod[:i]:
            n_term = 'Const'
            break
        
    if n_term == '':
        return prod_rules
    
    token = token_array[i][0]
    token_type = token_array[i][1]

    if n_term == 'Form':
        return recursive_parsing(prod_rules+[curr_prod.replace('Form', 'Var', 1)], token_array, i+1)
        

        

'''while i < len(token_array):
    curr_prod = prod_rules[-1]
    print(curr_prod)
    
    token = token_array[i][0]
    token_type = token_array[i][1]
    
    if token_type == 'Var':
        if 'Var' == next_prod:
            prod_rules.append(curr_prod.replace('Var', token, 1))
            i += 1
            continue
        elif 'Form' == next_prod:
            prod_rules.append(curr_prod.replace('Form', 'Var', 1))
            curr_prod = prod_rules[-1]
            prod_rules.append(curr_prod.replace('Var', token, 1))
            i += 1
            continue
        else:
            print('parsing error at token number '+ str(i))
            break
    if token_type == 'Const':
        if 'Const' == next_prod:
            prod_rules.append(curr_prod.replace('Const', token, 1))
            i += 1
            continue
        elif 'Form' == next_prod:
            prod_rules.append(curr_prod.replace('Form', 'Const', 1))
            curr_prod = prod_rules[-1]
            prod_rules.append(curr_prod.replace('Const', token, 1))
            i += 1
            continue
        else:
            print('parsing error at token number '+ str(i))
            break
    if token_type == 'Pred':
        var = '(' + 'Var,'*(token_array[i][2]-1)+'Var' +')'
        if 'Pred' == next_prod:
            prod_rules.append(curr_prod.replace('Pred', token+var, 1))
            i += 1
            continue
        elif 'Form' == next_prod:
            prod_rules.append(curr_prod.replace('Form', 'Pred', 1))
            curr_prod = prod_rules[-1]
            prod_rules.append(curr_prod.replace('Pred', token+var, 1))
            i += 1
            continue
        else:
            print('parsing error at '+ str(i))
            break
    if token_type == 'Log':
        print('parsing error at token number '+ str(i))
        break
    if token_type == 'Quan':
        if 'Form' == next_prod:
            prod_rules.append(curr_prod.replace('Form', 'QuanVarForm', 1))
            curr_prod = prod_rules[-1]
            prod_rules.append(curr_prod.replace('Quan', token, 1))
            i += 1
            next_prod = 'Var'
            continue
        else:
            print('parsing error at '+ str(i))
            break
    if token_type == 'OpenBr':
        if 'OpenBr' == next_prod:
            i += 1
            continue
        if 'Form' == next_prod:
            break
        else:  
            print('parsing error at token number '+ str(i))
            break
    if token_type == 'CloseBr':
        if 'OpenBr' == next_prod:
            i += 1
            continue
        if 'Form' == next_prod:
            break
        else:
            print('parsing error at token number '+ str(i))
            break'''

print(prod_rules)

