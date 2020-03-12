# all import statements
import sys
import re
from datetime import datetime
import igraph
from igraph import Graph
import plotly.graph_objects as go
import math

#################################################################
# Python script information
#################################################################

# -> This python script is written with python version 3.6.3
# -> This python script requires the modules, sys, re, datetime, igraph, plotly, and math
# -> to install igraph and plotly use the following commands:
# pip install python-igraph
# pip install plotly
# refer to these links if you have trouble installing the required packages:
# https://plot.ly/python/getting-started/
# https://plot.ly/python/tree-plots/
# note: You may need jupyter notebook support, intall it using the following commands:  
#pip install "notebook>=5.3" "ipywidgets>=7.2"  
#pip install jupyterlab==1.2 "ipywidgets>=7.5" (for python 3.5+)
# -> If using mira remember to use pip3.
# note: the parse tree will be displayed in your default browser ...
#       make sure python can open your default brower / has permission to do so ...
#       if possible you can open your defualt browser in anticipation, to make the parse tree display quicker.
# -> to run this script from the command line use the following commands:
# python parser.py <input_file> (on windows)
# python3 parser.py <input_file> (on linux / mira)
# -> if <input_file> is not specified in the command line then this script will try to open a default file: example.txt

#################################################################
# Function definitions
#################################################################

def write_error(error): # print error and write to the log file
    print()
    print(error)
    f = open('parser.log', 'a+')
    f.write(error+'\n')
    f.write('\n')
    f.close()
    sys.exit()
    
def read_input_file(F, V, C, P, E, L, Q, file_name): # read the input file
    name_re = re.compile('[a-zA-Z0-9_]') # regular expression for checking variable, predicate and constants
    other_re = re.compile('[a-zA-Z0-9_\\\\]') # regular expression for conenctives and quantifiers
    equality_re = re.compile('[a-zA-Z0-9_\\\\=]') # regular expression for the equality symbol
    FILE = None
    formula_flag = False # flag indictating if we are expecting part of the formula no the next line
    try:
        FILE = open(file_name)
    except:
        write_error('Execution error - could not open the specified input file ...') # throw error and exit if the file doesn't exist
    for line in FILE: 
        lst = line.rstrip().split(' ')
        if lst[0] == 'variables:':
            if V:
                write_error('Input file error - the set of variables has been specified multiple times ...')
            V = lst[1:]
            for v in V:
                if not bool(re.match(name_re, v)): # check variable names against regular expression
                    write_error('Input file error - the name of a variable contains illegal characters ...')
        elif lst[0] == 'constants:':
            if C:
                write_error('Input file error - the set of constants has been specified multiple times ...')
            C = lst[1:]
            for c in C:
                if not bool(re.match(name_re, c)): # check constant names against regular expression
                    write_error('Input file error - the name of a constant contains illegal characters ...')
        elif lst[0] == 'predicates:':
            if P:
                write_error('Input file error - the set of predicates has been specified multiple times ...')
            for i in range(1, len(lst)):
                try: # append tuple (<predicate_name>, <arity>) to P
                    local_arity = int(lst[i][lst[i].index('[')+1:lst[i].index(']')])
                    if local_arity < 1:
                        write_error('Input file error - a predicate has been given an arity less than 1 ...')
                    P.append((lst[i][:-3], local_arity))
                except IndexError:
                    write_error('Input file error - a predicate has been given a non integer arity ...')
                except ValueError:
                    write_error('Input file error - a predicate has not been given an arity ...')
            for p in P:
                if not bool(re.match(name_re, p[0])): # check predicate names against regular expression
                    write_error('Input file error - the name of a predicate name contains illegal characters ...')
        elif lst[0] == 'equality:':
            if E:
                write_error('Input file error - the equality symbol has been specified multiple times ...')
            try:
                E = lst[1]
                if not bool(re.match(equality_re, E)): # check equality symbol against regular expression
                    write_error('Input file error - the name of the equality symbol contains illegal characters ...')
            except IndexError: # check equality symbol given
                write_error('Input file error - there is no equality symbol ...')
        elif lst[0] == 'connectives:':
            if L:
                write_error('Input file error - the set of logical connectives has been specified multiple times ...')
            try:
                L = lst[1:6]
                for l in L:
                    if not bool(re.match(other_re, l)): # check connectives against regular expression
                        write_error('Input file error - one of the logical connectives contains illegal characters ...')
            except IndexError: # check all logical connectives are given
                write_error('Input file error - some logical connectives have not been specified ..')
        elif lst[0] == 'quantifiers:':
            if Q:
                write_error('Input file error - the set of quantifiers has been specified multiple times ...')
            try:
                Q = lst[1:3]
                for q in Q:
                    if not bool(re.match(other_re, q)): # check quantifiers against regular expression
                        write_error('Input file error - one of the quantifiers contains illegal characters ...')
            except IndexError: # check all quantifiers are given
                write_error('Input file error - some of the quantifiers have not been specified ...')
        elif lst[0] == 'formula:':
            if F:
                write_error('Input file error - the formula has been specified multiple times ...')
            F = ''.join(lst[1:])
            formula_flag = True
            continue
        elif formula_flag:
            F += ''.join(lst)
            continue
        else: # if no formula flag throw error - we are not expecting this line ...
            write_error('Input file error - there is an unexpected line in the input file: '+line+' ...')
            
        formula_flag = False
            
    FILE.close()
    
    # Handle various input file errors
    if not E:
        write_error('Input file error - there is no equality symbol ...')

    if len(L) != 5:
        write_error('Input file error - there is an incorrect number of connectives specified ...')

    if len(Q) != 2:
        write_error('Input file error - there is an incorrect number of quantifiers specified ...')

    if set(V).intersection(set(C)):
        write_error('Input file error - some of the variables and constants have been given the same name ...')

    if set(V).intersection(set(L)):
        write_error('Input file error - some of the variables and logical connectives have been given the same name ...')

    if set(C).intersection(set(L)):
        write_error('Input file error - some of the constants and logical connectives have been given the same name ...')

    if set(V).intersection(set(Q)):
        write_error('Input file error - some of the variables and quantifiers have been given the same name ...')

    if set(C).intersection(set(Q)):
        write_error('Input file error - some of the constants and quantifiers have been given the same name ...')

    if set(L).intersection(set(Q)):
        write_error('Input file error - some of the quantifiers and logical connectives have been given the same name ...')

    if len(set(C)) != len(C):
        write_error('Input file error - there are duplicated constant names in the input file ...')

    if len(set(V)) != len(V):
        write_error('Input file error - there are variable constant names in the input file ...')

    if len(set([p[0] for p in P])) != len([p[0] for p in P]):
        write_error('Input file error - there are duplicated predicate names in the input file ...')

    if len(set(L)) != len(L):
        write_error('Input file error - there are duplicated logical connectives identifiers in the input file ...')

    if len(set(Q)) != len(Q):
        write_error('Input file error - there are duplicated quantifier indentifiers in the input file ...')

    if E in V or E in C or E in Q or E in L or E in [p[0] for p in P]:
        write_error('Input file error - the equality symbol identifier appears elsewhere in the input file ...')
        
    for p in P:
        if p[0] in V:
            write_error('Input file error - some of the variables and predicates have been given the same name ...')
        if p[0] in C:
            write_error('Input file error - some of the constants and predicates have been given the same name ...')
        if p[0] in L:
            write_error('Input file error - some of the logical connectives and predicates have been given the same name ...')
        if p[0] in Q:
            write_error('Input file error - some of the quantifiers and predicates have been given the same name ...')

    return F, V, C, P, L, Q, E
    
def print_grammar(V, C, P, E, L, Q):
    f = open('grammar.txt', 'w+')
    # get the logical connectives and quantifiers
    eq = E
    land = L[0]
    lor = L[1]
    implies = L[2]
    iff = L[3]
    neg = L[4]

    exists = Q[0]
    forall = Q[1]

    print('note: all non-terminals are enclosed by * characters like so: *<non-terminal>* ')
    f.write('note: all non-terminals are enclosed by * characters like so: *<non-terminal>* \n')
    print()
    f.write('\n')
    # start rule
    print('*Start* -> *Formula*')
    f.write('*Start* -> *Formula*\n')

    # logical formulae rules
    print('*Formula* -> (*Expression*) | '+neg+'*Formula* | *Quantifier* *Variable* *Formula* | *Predicate*')
    f.write('*Formula* -> (*Expression*) | '+neg+'*Formula* | *Quantifier* *Variable* *Formula* | *Predicate*\n')

    # quantifiers
    print('*Quantifier* -> '+ exists + ' | '+ forall)
    f.write('*Quantifier* -> '+ exists + ' | '+ forall+'\n')

    # expression rules
    print('*Expression* -> *Term*'+eq+'*Term* | *Formula**Connective**Formula*')
    f.write('*Expression* -> *Term*'+eq+'*Term* | *Formula**Connective**Formula*\n')
    
    # term rules
    print('*Term* -> *Constant* | *Variable*')
    f.write('*Term* -> *Constant* | *Variable*\n')

    # connectives rule
    print('*Connective* -> '+land+' | '+lor+' | '+implies+' | '+iff)
    f.write('*Connective* -> '+land+' | '+lor+' | '+implies+' | '+iff+'\n')
    
    # assign variables to predicate rule
    predicates = ''
    for p in P:
        predicates += p[0] + '(' + '*Variable*, '*p[1]
        predicates = predicates[:-2]
        predicates += ') | '
        
    predicates = predicates[:-3]
    print('*Predicate* -> '+predicates)
    f.write('*Predicate* -> '+predicates+'\n')

    # assign variable rule
    variables = ''
    for v in V:
        variables += v + ' | '

    variables = variables[:-3]
    print('*Variable* -> '+ variables)
    f.write('*Variable* -> '+ variables+'\n')

    # assign constants rule
    constants = ''
    for c in C:
        constants += c + ' | '

    constants = constants[:-3]
    print('*Constant* -> '+ constants)
    f.write('*Constant* -> '+ constants+'\n')
    f.close()

def lexical_analyzer(F, V, C, P, E, L, Q):
    max_length = 0 # maximum length of a valid lexeme
    # calculate the maximum length of any possible lexeme
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
    #####################################################
            
    lexeme = '' # init lexeme variable
    token_array = [] # construct the token_array
    arity = 0 # init arity variable

    i = 0 # set our pointer i to the start
    j = max_length # set the lookahead pointer to max length

    while i < len(F): # while we still have characters to evaluate
        while j > 0: # while we still have a string to evaluate
            lexeme = F[i:i+j] # set lexeme
            # evaluate lexeme
            if lexeme == '(':
                token_array.append((lexeme, 'OpenBracket')) # append tuple (<lexeme>, <token_type>) to our token array
                i += len(lexeme) # move the pointer along the input
                j = max_length # set the lookahead pointer to max length again
                lexeme = ''
                continue
            if lexeme == ')':
                if arity > 0:
                    write_error('Syntax error - a predicate has been given too few variables ...')
                token_array.append((lexeme, 'CloseBracket'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme == ',':
                if arity > 0: # if we see a comma make sure it is part of a predicate
                    arity -= 1
                else:
                    write_error('Syntax error - there is an unexpected character "," at position '+str(i)+' in the formula\n- perhaps a predicate has been given too many variables ...')
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
                    token_array.append((lexeme, 'Predicate', p[1])) # append the tuple (<lexeme>, <token_type>, <arity>) to our token array
                    i += len(lexeme)
                    j = max_length
                    lexeme = ''
                    arity = p[1] - 1 # set the arity variable to <arity> - 1, this is how many commas (,) we expect
                    break
            if lexeme == E:
                token_array.append((lexeme, 'Equality'))
                i += len(lexeme)
                j = max_length
                lexeme = ''
                continue
            if lexeme in L:
                if lexeme == L[4]:
                    token_array.append((lexeme, 'Negation', L.index(lexeme))) # specify the special negation case
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
            j -= 1 # decrement j and look at a smaller lexeme
        if i < len(F): # if we get to j = 0 then i < len(F) which means we have an unexpected character
            write_error('Syntax error - there is an unexpected character "' + F[i]+ '" at position ' + str(i)+'  in the formula ...')
        
    return token_array

#################################################################
# Main code
#################################################################

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

# parse command line args
if len(sys.argv) == 2:
    file_name = sys.argv[1]
elif len(sys.argv) > 2:
    write_error('Execution error - there are an unexpected number of command line arguments ... ')
else:
    print('WARNING - there was no <filename> specified in the command line ...')
    print('using the default <filename> "example.txt" ...')
    print()

# write the execution timestamp header to the log file    
f = open('parser.log', 'a+')
f.write('Execution at '+str(datetime.now()) +':\n')
f.close()
    
# try to read input file
F, V, C, P, L, Q, E = read_input_file(F, V, C, P, E, L, Q, file_name)

# write that the input file passed the validation checks
print('Success - the input file has the correct format ...')
print()
f = open('parser.log', 'a+')
f.write('Success - the input file given had the correct format ...\n')
f.close()

# print the grammar
print_grammar(V, C, P, E, L, Q)

#################################################################
# Lexical analysis
#################################################################

# if we dont' have a formula print error and exit
if F == '':
    write_error('Execution error - there was no formula specified in the input file ...')
else: # remove all white space that includes tabs \t and newlines \n and character returns \r
    F = F.replace('\t', '')
    F = F.replace(' ', '')
    F = F.replace('\n', '')
    F = F.replace('\r', '')

# get the token stream from our lexical analyzer 
token_array = lexical_analyzer(F, V, C, P, E, L, Q)

#################################################################
# Syntax analysis
#################################################################

#################################################################
# Parse tree data structure
#################################################################
class Tree(object):
    def __init__(self, data, index):
        self.data = data # data represents the token
        self.index = index # index represents the index of the token in the token array / stream
        self.children = [] # list of child nodes

#################################################################
# Non terminal function definitions
#################################################################
    
def Start():
    node = Formula()[0] # set the child nodes of the 'Start' node to any nodes returned by formula
    match('EOF') # match EOF to make sure we reached the end when parsing
    return node
    
def Formula(): # non terminal *Formula*
    global lookahead
    nodes = [] # list of nodes returned by Formula()
    if lookahead[0] == '(': # if we see a '(' we know to use the production rule: *Formula* -> (*Expression*)
        nodes.append(Tree('(',I)) # append tree node to our list of nodes
        match('OpenBracket') # match open bracket
        nodes.append(Expression()) # call Expression() and append any nodes returned to our list of nodes
        nodes.append(Tree(')',I)) # append tree node to our list of nodes
        match('CloseBracket') # match close brackets
        return nodes # return our list of nodes
    elif lookahead[0] == L[4]: # if we see a negation  we know to use the production rule: *Formula* -> <negation>*Formula*
        node = Tree(L[4],I) # init negation tree node
        match('Negation')
        node.children = (Formula()) # call Formula() and set any nodes returned to the children of our negation node
        return [node] # return singleton list containing our negation tree node
    elif lookahead[0] in Q: # if we see a quantifier we know to use the production rule: *Formula* -> *Quantifier* *Variable* *Formula*
        temp_node1 = Quantifier() # create temp node returned by Quantfiier()
        temp_node2 = Variable() # create temp node returned by Variable()
        temp_nodes3 = Formula() # create list of temp nodes return by Formula()
        temp_node2.children=(temp_nodes3) # set the children of the variable node to the list returned by Formula()
        temp_node1.children.append(temp_node2) # set the child of the quantifier node to the variable node
        return [temp_node1] # return a singleton list containing out quantfier node
    elif lookahead[0] in [p[0] for p in P]: # if we see a predicate we know to use the production rule: *Formula* -> *Predicate*
        return [Predicate()] # return a singleton list containing the node returned by Predicate()
    else: # if we see something else for example, a variable or a constant return an error
        error = 'Syntax error - the syntax parser expected either a "(", a negation, a quantifier or a predicate but was given a '+lookahead[1] +' '+lookahead[0]+' instead'
        # construct a meaningful error message
        if lookahead[1] == 'Equality':
            error += '\n- perhaps an equality symbol appeared before a variable or constant'
        if lookahead[1] == 'Connective':
            error += '\n- perhaps a logical connective appeared before a valid formula'
        write_error(error+' ...')
        
def Expression(): # non terminal *Expression*
    global lookahead
    if lookahead[0] in C or lookahead[0] in V: # if we see a constant or variable we know to use the prodcution rule *Expression* -> *Term*<equality>*Term*
        node = Tree(E, None) # init a tree node for the equality symbol
        node.children.append(Term()) # append the node returned by Term() to the equality node's children
        node.index = I # set the node index of the equality node
        match('Equality') # match the equality symbol
        node.children.append(Term()) # append the node returned by Term() to the equality node's children
        return node # return the equality node
    else: # if we see anything else we can assume we should try the production rule: *Expression* -> *Formula**Connective**Formula*
        node = Tree('temp', None) # init a temporary node, that will become the logical connective node
        node.children+=Formula() # add the nodes returned by Formula() to the children of our temporary node
        temp = Connective() # set another temporary node to the node returned by Connective()
        node.data = temp.data # set the node data (which connective?)
        node.index = temp.index # set the node index
        node.children+=Formula() # add the nodes returned by Formula() to the children of our connective node
        return node # return our connective node

def Term(): # non terminal *Term*
    global lookahead
    if lookahead[0] in C: # if we see a constant we know to use the production rule: *Term* -> *Constant*
        return Constant() # return the node returned by Constant()
    elif lookahead[0] in V: # if we see a variable we know to use the production rule: *Term* -> *Variable*
        return Variable() # return the node returned by Variable()
    else: # if we see something else for example a predicate, then error
        write_error('Syntax error - the syntax parser expected a constant or variable after an equality symbol but got a '+lookahead[1] +' '+ lookahead[0]+' instead ...')

def Predicate(): # non terminal *Predicate*
    global arity
    node = Tree(lookahead[0],I) # create a Predicate node
    match('Predicate') # match a predicate token
    node.children.append(Tree(lookahead[0],I)) # append a '(' node to the children of our predicate node
    match('OpenBracket') # match open bracket
    for _ in range(arity): # for the arity of our predicate
        node.children.append(Variable()) # append a variable node returned by Variable() to the chidlren of our predicate node
    node.children.append(Tree(lookahead[0],I)) # append a ')' node to the children of our predicate node
    match('CloseBracket') # match close bracket
    return node # return our predicate node
    
def Quantifier(): # non terminal *Quantifier*
    node = Tree(lookahead[0],I) # create a quantfiier node
    match('Quantifier') # match the quantifier
    return node # return our quantifier node

def Connective(): # non terminal *Connective*
    node = Tree(lookahead[0],I) # create a logical connective node
    match('Connective') # match the logical connective
    return node # return our connective node

def Variable(): # non terminal *Variable*
    node = Tree(lookahead[0],I) # create a variable node
    match('Variable') # match the variable
    return node # return our variable node

def Constant(): # non terminal *Constant*
    node = Tree(lookahead[0],I) # create a constant node
    match('Constant') # match the variable
    return node # return our constant node

def match(token_type): # function that matches the current lookahead token with some token type
    global lookahead
    global arity
    global position_dict
    if (lookahead[1] == token_type): # lookahead[1] specifies the token type of the current token
        # if the token type of the current lookahead is the one expected specified in token_type then continue
        if token_type == 'Predicate': # if the token_type expected is Predicate then set the global arity variable 
            try:
                arity = lookahead[2] # lookahead[2] specifies the arity of a predicate if the current lookahead token is a predicate, we have a tuple: (<predicate_name>, <token_type>, <arity>)
            except IndexError: # if we can't get the arity something has gone wrong print error and exit
                write_error('Internal error - the syntax parser could not get the arity of the predicate '+lookahead[0]+' ...')
        next_token() # move the lookahead along to the next token
    else: # if the expected token_type does not macth the token type of the current lookahead then we have a syntax error
        error = 'Syntax error - the syntax parser expected a '+token_type +' but was given a '+lookahead[1]+' '+lookahead[0]+' instead'
        # construct a meaningful error message
        if token_type == 'OpenBracket':
            error += '\n- perhaps you are missing brackets when expressing a predicate'
        if token_type == 'CloseBracket':
            error += '\n- perhaps you are missing brackets somewhere'
        if token_type == 'Variable':
            error += '\n- perhaps a quantifier was not given a variable ; perhaps a predicate was given something other than a variable as an input'
        if token_type == 'Equality':
            error += '\n- perhaps a variable or constant was not followed by an equality symbol'
        if token_type == 'Connective':
            error += '\n- perhaps you have unnessecary brackets'
        if token_type == 'EOF':
            error += '\n- perhaps you are missing brackets'
        write_error(error+' ...' )
        
def next_token(): # function that sets the global lookahead variable to the next token in our token array / stream
    global lookahead
    global I
    if lookahead[1] != 'EOF': # check our lookahead is not EOF
        try:
            I += 1 # increment I to get the next token
            lookahead = token_array[I] # try to get the Ith token at postion I-1 in our array
        except IndexError:
            # if we get an index out of range error then we must report an error, our parser was expecting more tokens but it reached EOF
            write_error('Syntax error - the syntax parser \n- perhaps there are missing brackets somewhere ... ')

#################################################################
# Main code
#################################################################

token_array += [('$', 'EOF')] # append EOF / $ to the end of our token stream 

# init the global variabes for syntax analysis
I = 0 # set I to 0
lookahead = token_array[I] # set the lookahead to the first character at position I
arity = 0 # global arity variable for any predictes we come accross

# call the Start() function on the root node and begin parsing
root = Start()

#################################################################
# Constructing and displaying the parse tree
#################################################################

# set the global variable current_node to our root 'Start' node
current_node = root
# init the layout array lay which specifies the relative positions of the parse tree nodes
lay = [0]*len(token_array)
# init the Edges array which specifies the edges between the parse tree nodes
Edges = []

#################################################################
# Function definitions
#################################################################

def traverse_tree(node, X, Y, H): # traverse tree function
    global position
    global Edges

    lay[node.index] = [X, Y] # X an Y specify the relative position of this node
    L = len(node.children) # L is the number of children of this node
    for i in range(0, L): # for each of the child nodes
        Edges.append((node.index, node.children[i].index)) # create an edge between this node and its children
        traverse_tree(node.children[i], X + (i+1-((L+1)/2))*(1/((math.log(L) + 1)*H)), Y+2.0, H*(math.log(L) + 1)) # call traverse_tree on each of the child nodes and specify their relative position

def display_tree(lay, E): # display tree function - display the tree with plotly and igraph using the layout array lay and the edges array E
    global token_array
    nr_vertices = len(token_array) - 1 # set nr_vertices to the number of vertices
    v_label = [t[0] for t in token_array][:-1] # append Start to our node labels and remove the EOF character from our labels
    G = Graph.Tree(nr_vertices, 2) # create a tree G
    position = {k: lay[k] for k in range(nr_vertices)} # create the position dict
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y) # M is the max Y position

    L = len(position) # L is the number of nodes again
    Xn = [position[k][0] for k in range(L)] # create the actual X position from the relative positions in the dict position
    Yn = [2*M-position[k][1] for k in range(L)] # create the actual Y position from the relative positions in the dict position
    Xe = []
    Ye = []
    for edge in E: # create the edges using the relative positions
        Xe+=[position[edge[0]][0], position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1], 2*M-position[edge[1]][1], None]

    labels = v_label # set the labels of the nodes

    fig = go.Figure() # init a figure
    fig.add_trace(go.Scatter(x=Xe, # draws lines / edges using arrays Xe and Ye
                             y=Ye,
                             mode='lines',
                             line=dict(color='rgb(210,210,210)', width=1),
                             hoverinfo='none'
                             )) 
    fig.add_trace(go.Scatter(x=Xn, # draws points using arrays Xn and Yn 
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
                             )) 
    axis = dict(showline=False, # hide axis line, grid, ticklabels and title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            )
    fig.update_layout(title='Parse Tree', # update the layout with a title and annotations on the nodes
                      annotations=make_annotations(position, v_label, labels, M, position),
                      font_size=12,
                      showlegend=False,
                      xaxis=axis,
                      yaxis=axis,
                      margin=dict(l=40,r=40,b=85,t=100),
                      hovermode='closest',
                      plot_bgcolor='rgb(248,248,248)'
                      ) 
    fig.show() # show the figure
    
def make_annotations(pos, text, labels, M, position, font_size=10, font_color='rgb(250,250,250)'):
    L=len(pos) # function to assign the text / labels to the nodes of the parse tree
    if len(text)!=L:
        write_error('Internal error - while constructing the parse tree the lists pos and text must have the same len ...')
    annotations = []
    for k in range(L): # for each node
        annotations.append(
            dict( # specify the node characteristics
                text=labels[k], 
                x=pos[k][0], y=2*M-position[k][1],
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations

#################################################################
# Main code
#################################################################

if lookahead[1] != 'EOF': # if we have not reached EOF then we have a syntax error ... we have been given too many tokens .. perhaps additional brackets
    write_error('Syntax error - the syntax parser was given additional unexpected tokens \n-perhaps there are unnecessary brackets ... ')
else:
    print()
    print('Success - the formula is syntactically correct ... ') # otherwise our formula is correct
    f = open('parser.log', 'a+')
    f.write('Success - the formula was syntactically correct ... \n')
    f.write('\n')
    f.close()
    print('Displaying the parse tree ... ')
    traverse_tree(root, 0.0, -10.0, 1.0) # traverse the tree starting from the root
    display_tree(lay, Edges) # display the tree
    sys.exit()


    
