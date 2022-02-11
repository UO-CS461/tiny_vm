
calc_grammar = """
    ?start: program -> end

    ?program: statement*

    statement: rexpr ";"
      | assignment ";"

    assignment: lexpr ":" type "=" rexpr -> assign

    ?type: NAME

    ?lexpr: NAME

    ?rexpr: sum
      | methodcall
    
    methodcall: rexpr "." methodname "(" methodargs ")" -> methodcall
    
    ?methodname : NAME
    ?methodargs: (rexpr ("," rexpr)* )? -> methodargs

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> const_number
         | "-" atom         -> neg
         | lexpr            -> var
         | "(" sum ")"
         | "true" -> const_true
         | "false" -> const_false
         | "nothing" -> const_nothing
         | string -> const_string

    ?string: ESCAPED_STRING

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.WS_INLINE
    %import common.WS

    %ignore WS_INLINE
    %ignore WS
"""
