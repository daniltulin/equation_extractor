# blif_parser

I use pyparsing library to parse blif files. I constructed a context-free grammar, that is intialized in Parser.parse method.
For every component, that is used by the grammar, there is a factory method, that is invocated when parser meet that component in a file.
Every component in component folder has Factory method, it get a raw string or other component as an argument
Model's link_with method links all models with each other(if some of them has .subckt or .gate commands), then it build dependencies for every output variable
Parser's parse method return array of models

Then we build equatation. 
Equation is basically is:
1) Variable
2) Equation && Equation ...
3) Equation || Equation ...

It is not a challenge to evaluate equation using recursion
