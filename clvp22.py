import sys
import re
from datetime import datetime
import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
import math
# pip install python-igraph
# pip install plotly

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
    formula_flag = False
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
            formula_flag = False
        elif lst[0] == 'constants:':
            C = lst[1:]
            for c in C:
                if not bool(re.match(reg_expr, c)):
                    write_error('constant name contains illegal characters ...')
            formula_flag = False
        elif lst[0] == 'predicates:':
            for i in range(1, len(lst)):
                try:
                    P.append((lst[i][:-3], int(lst[i][lst[i].index('[')+1:lst[i].index(']')])))
                except:
                    write_error('error in input file - predicate given a non integer arity ...')
                    
            for p in P:
                if not bool(re.match(reg_expr, p[0])):
                    write_error('predicate name contains illegal characters ..')
            formula_flag = False
        elif lst[0] == 'equality:':
            try:
                E = lst[1]
            except:
                write_error('no equality symbol given ...')
            formula_flag = False
        elif lst[0] == 'connectives:':
            try:
                L = lst[1:6]
            except:
                write_error('some connectives missing in the input file ..')
            formula_flag = False
        elif lst[0] == 'quantifiers:':
            try:
                Q = lst[1:3]
            except:
                write_error('some quantifiers missing in the input file ...')
            formula_flag = False
        elif lst[0] == 'formula:':
            F = ''.join(lst[1:])
            formula_flag = True
        elif formula_flag:
            F += ''.join(lst)
        else:
            write_error('unexcpected line in the input file ... '+line+' ...')

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
        write_error('duplicated constant names in the input file ...')

    if len(set(V)) != len(V):
        write_error('duplicated variable names in the input file ...')

    if len(set([p[0] for p in P])) != len([p[0] for p in P]):
        write_error('duplicated predicate names in the input file ...')

    if len(set(L)) != len(L):
        write_error('duplicated connective names in the input file ...')

    if len(set(Q)) != len(Q):
        write_error('duplicated quantifier names in the input file ...')

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

    print('Start -> Formula')

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
        predicates += p[0] + '(' + 'Variable, '*p[1]
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

if len(sys.argv) == 2:
    file_name = sys.argv[1]
elif len(sys.argv) > 2:
    print('Unexpected number of command line arguments ... using the default filename "example.txt"')
else:
    print('No filename specified in the command line ... using the default filename "example.txt"')


F, V, C, P, L, Q, E = read_input_file(F, V, C, P, E, L, Q, file_name)

print_grammar(V, C, P, E, L, Q)

# lexical analyzer

if F == '':
    print('no formula given')
    sys.exit()
    
token_array = lexical_analyzer(F, V, C, P, E, L, Q)

# syntax analyzer
class Tree(object):
    def __init__(self, data, index):
        self.data = data
        self.index = index
        self.children = []

token_array += [('$', 'EOF')]

I = 0
lookahead = token_array[I]
arity = 0

root = Tree('Start', 0)

def Start(parent):
    global I
    global lookahead
    global arity
    
    I = 1
    lookahead = token_array[I-1]
    arity = 0
    Formula(parent)
    match('EOF')
    
def Formula(parent):
    global lookahead
    if lookahead[0] == '(':
        parent.children.append(Tree('(',I))
        match('OpenBracket')
        Expression(parent)
        parent.children.append(Tree(')',I))
        match('CloseBracket')
    elif lookahead[0] == L[4]: # equal to negation
        parent.children.append(Tree(L[4],I))
        match('Negation')
        Formula(parent)
    elif lookahead[0] in Q:
        node = Quantifier(parent)
        node = Variable(node)
        node = Formula(node)
    elif lookahead[0] in [p[0] for p in P]:
        Predicate(parent)
    else:
        write_error('syntax error ... could not match '+lookahead[0] +' in Formula')
            
def Expression(parent):
    global lookahead
    if lookahead[0] in C or lookahead[0] in V:
        Term(parent)
        parent.children.append(Tree(E,I))
        match('Equality')
        Term(parent)
    else:
        Formula(parent)
        Connective(parent)
        Formula(parent)

def Term(parent):
    global lookahead
    if lookahead[0] in C:
        Constant(parent)
    elif lookahead[0] in V:
        Variable(parent)
    else:
        write_error('syntax error ... could not match '+lookahead[0] +' in Term')

def Predicate(parent):
    global arity
    node = Tree(lookahead[0],I)
    parent.children.append(node)
    match('Predicate')
    node.children.append(Tree(lookahead[0],I))
    match('OpenBracket')
    for _ in range(arity):
        Variable(node)
    node.children.append(Tree(lookahead[0],I))
    match('CloseBracket')
    
def Quantifier(parent):
    node = Tree(lookahead[0],I)
    match('Quantifier')
    parent.children.append(node)
    return node

def Connective(parent):
    node = Tree(lookahead[0],I)
    match('Connective')
    parent.children.append(node)
    return node

def Variable(parent):
    node = Tree(lookahead[0],I)
    match('Variable')
    parent.children.append(node)
    return node

def Constant(parent):
    node = Tree(lookahead[0],I)
    match('Constant')
    parent.children.append(node)
    return node

def match(token_type):
    global lookahead
    global arity
    global position_dict
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
    if lookahead[1] != 'EOF':
        try:
            I += 1
            lookahead = token_array[I-1]
        except:
            write_error('syntax error ... parser expected additional tokens ... ')
    
Start(root)
# construct and print the parse tree as we go along ...
current_node = root
lay = []
Edges = []

def assign_position(node, X, Y, H):
    global position
    global Edges
    lay.append([X, Y])
    L = len(node.children)
    for i in range(0, L):
        Edges.append((node.index, node.children[i].index))
        assign_position(node.children[i], X +(i-(L//2))*(1/H), Y+2.0, H*2.1)

def create_tree(lay, E):
    global token_array
    nr_vertices = len(token_array)
    v_label = ['Start']+[t[0] for t in token_array][:-1]
    G = Graph.Tree(nr_vertices, 2)
    position = {k: lay[k] for k in range(nr_vertices)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe+=[position[edge[0]][0], position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1], 2*M-position[edge[1]][1], None]

    labels = v_label

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                             y=Ye,
                             mode='lines',
                             line=dict(color='rgb(210,210,210)', width=1),
                             hoverinfo='none'
                             )) # draws lines using arrays Xe and Ye
    fig.add_trace(go.Scatter(x=Xn,
                             y=Yn,
                             mode='markers',
                             name='bla',
                             marker=dict(symbol='circle-dot',
                                         size=30,
                                         color='#6175c1',
                                         line=dict(color='rgb(50,50,50)',width=1)
                                         ),
                             text=labels,
                             hoverinfo='text',
                             opacity=0.8
                             )) # draws points using arrays Xn and Yn 
    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            ) # removes axes
    fig.update_layout(title='Parse Tree',
                      annotations=make_annotations(position, v_label, labels, M, position),
                      font_size=12,
                      showlegend=False,
                      xaxis=axis,
                      yaxis=axis,
                      margin=dict(l=40,r=40,b=85,t=100),
                      hovermode='closest',
                      plot_bgcolor='rgb(248,248,248)'
                      ) # sets the annotations
    fig.show()
    
def make_annotations(pos, text, labels, M, position, font_size=10, font_color='rgb(250,250,250)'):
    L=len(pos)
    if len(text)!=L:
        raise ValueError('The lists pos and text must have the same len')
    annotations = []
    for k in range(L):
        annotations.append(
            dict(
                text=labels[k], # or replace labels with a different list for the text within the circle
                x=pos[k][0], y=2*M-position[k][1],
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations


if lookahead[1] != 'EOF':
    write_error('syntax error ... parser given additional tokens ... ')
else:
    print('Formula is syntactically correct ... ')
    f = open('parser.log', 'a')
    f.write('Execution at '+str(datetime.now()) +':\n')
    f.write('The formula was syntactically correct\n')
    f.write('\n')
    f.close()
    print('Displaying parse tree ... ')
    assign_position(root, 0.0, -10.0, 0.25)
    create_tree(lay, Edges)
    sys.exit()


    
