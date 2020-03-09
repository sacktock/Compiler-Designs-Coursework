# parser.py
- This python script is written with python version 3.6.3.
- This python script requires the modules, sys, re, datetime, igraph, plotly, and math.
- To install igraph and plotly use the following commands:  
**pip install python-igraph**,  
**pip install plotly**.  
- **note:** the parse tree will be displayed in your default browser, make sure python can open your default brower / has permission to do so, if possible you can open your defualt browser in anticipation, to make the parse tree display quicker.  
- to run this script from the command line use the following commands:  
**python parser.py <input_file>** (on windows),  
**python3 parser.py <input_file>** (on linux / mira).  
- If **<input_file>** is not specified in the command line then this script will try to open the default file: **example.txt**.
- If you give more than one command line argument the script will report an error and terminate.
- Similarly if the file you specify in the command line does not exist then the script will report an error and terminate.

# the grammar
- The grammar will be printed to your screen if the input file passes all the validation checks.
- In the case that a validation check is not passed, an error will be printed to the command line indicating which check failed (this will also be written to parser.log).
- You need not specify a valid formula (or any formula) for the grammar to be displayed, but if there are duplicated or unexpected lines in the input file an error will be reported.
- **note:** all non-terminals are enclosed by * characters like so: *non-terminal*, to provide clarity when differentiating between non-terminals and terminals.

# the parse tree
- The parse tree will be displayed in your default browser.
- The parse tree that will be shown is an abstract syntax tree (not a full parse tree).
- What to expect from the parse tree?
- Quantifiers will have only one child - the variable that is being quantified.
- Variables could have many children - '(', ')', some quantifier, some logical connective, or an equality symbol. Or they could have no children if they are part of some predicate.
- Logical connectives could have many children again - '(', ')', some quantifier, some logical connective, some predicate, or an equality symbol. But they must be internal nodes, because their children make up some sub formula(e).
- Brackets '(' or ')' have no children and are always leaves in the parse tree.
- Constants are also always leaves.
- Predicates always have the children '(', followed by 'a' variables (where 'a' is the arity of the predicate), and a ')'.
- The equality symbol will always have exactly two children - both either a constant or a variable.

# additional info
- Any errors will be printed to the command line and written to the log file parser.log.
- In the case of a success 'Success - the formula is syntactically correct ... ' will be printed to the command line and written in the parser.log file.
- In the parser.log file each execution of the python script will have a timestamp and an outcome (error or success) associated with it (from oldest to newest).
- In the case of complex or large FO formula, the tree may be hard to read, but there is a zoom function provided by plotly so you can zoom in on some of the nodes to check they are indeed correct.
- In the case of particularly long names for variables, constants, predicates etc. hover over the node to read the full name of terminal it represents.
- In the case that plotly times out or fails to display the parse tree, run the script again on the same input and it should work (it has happened quite a lot of times where it randomly fails to display the parse tree).
