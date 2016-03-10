from ply import lex
from ply.lex import TOKEN
from ply import yacc

from pif_ir.bir.utils.exceptions import BIRParsingError

class BIRLexer(object):
    def __init__(self):
        self.last_token = None
        self.lexer = lex.lex(module=self, debug=False)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def input(self, data):
        self.lexer.input(data)

    keywords = ('DONE', 'OFFSET')

    tokens = ( 
        # identifier tokens
        'ID', 'INT_CONST_HEX', 'INT_CONST_DEC',
        'PERIOD', 'LPAREN', 'RPAREN',

        # arithmetic operators
        'PLUS', 'MINUS', 'MULT', 'DIVIDE', 'MOD', 'INC', 'DEC',

        # relational operators
        'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',

        # logical operators
        'LAND', 'LOR', 'LNOT',
        
        # bitwise operators
        'AND', 'OR', 'XOR', 'NOT', 'LSHIFT', 'RSHIFT'
    ) + keywords

    identifier  = r'[a-zA-Z_][0-9a-zA-Z_]*'
    hex_const   = r'0[xX][0-9a-fA-F]+'
    dec_const   = r'0|([1-9][0-9]*)'

    t_PERIOD    = r'\.'
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'

    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_MULT      = r'\*'
    t_DIVIDE    = r'/'
    t_MOD       = r'%'
    t_INC       = r'\+\+'
    t_DEC       = r'\-\-'

    t_EQ        = r'=='
    t_NEQ       = r'!='
    t_GT        = r'>'
    t_LT        = r'<'
    t_GTE       = r'>='
    t_LTE       = r'<='

    t_LAND      = r'&&'
    t_LOR       = r'\|\|'
    t_LNOT      = r'!'
    
    t_AND       = r'&'
    t_OR        = r'\|'
    t_XOR       = r'\^'
    t_NOT       = r'~'
    t_LSHIFT    = r'<<'
    t_RSHIFT    = r'>>'

    t_DONE      = r'\$done\$'
    t_OFFSET    = r'\$offset\$'
    t_ignore    = ' \t\n'

    @TOKEN(identifier) 
    def t_ID(self, t):
        t.type = 'ID'
        return t

    @TOKEN(hex_const)
    def t_INT_CONST_HEX(self, t):
        t.value = int(t.value, 16)
        return t

    @TOKEN(dec_const)
    def t_INT_CONST_DEC(self, t):
        t.value = int(t.value)
        return t

    def t_error(self, t):
        print "Illegal BIR character '{0}'".format(t.value[0])
        t.lexer.skip(1)

class BIRParser(object):
    def __init__(self):
        self.lexer = BIRLexer()
        self.tokens = self.lexer.tokens
        self.inst_parser = yacc.yacc(module=self, write_tables=0, 
                                     debug=False, start='arith_exp',
                                    errorlog=yacc.NullLogger())
        self.cond_parser = yacc.yacc(module=self, write_tables=0, 
                                     debug=False, start='bool_exp')

    def eval_inst(self, expression, header, packet, bit_offset=0):
        self.header = header
        self.packet = packet
        self.bit_offset = bit_offset
        self.exp = str(expression)
        return self.inst_parser.parse(self.exp, lexer=self.lexer)

    def eval_cond(self, expression, header, packet, bit_offset=0):
        self.header = header
        self.packet = packet
        self.bit_offset = bit_offset
        self.exp = str(expression)
        return self.cond_parser.parse(self.exp, lexer=self.lexer)

    precedence = (
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'LT', 'LTE', 'GT', 'GTE'),
        ('left', 'LSHIFT', 'RSHIFT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIVIDE', 'MOD'),
        ('right', 'NOT', 'LNOT'),
        ('left', 'LPAREN', 'RPAREN', 'INC', 'DEC')
    )

    def p_bool_exp_0(self, p):
        """ bool_exp : LPAREN bool_exp RPAREN
        """
        p[0] = p[2]

    def p_bool_exp_1(self, p):
        """ bool_exp : arith_exp EQ arith_exp
                     | arith_exp NEQ arith_exp
                     | arith_exp LT arith_exp
                     | arith_exp GT arith_exp
                     | arith_exp LTE arith_exp
                     | arith_exp GTE arith_exp
        """
        if p[2] == "==":    p[0] = p[1] == p[3]
        elif p[2] == "!=":  p[0] = p[1] != p[3]
        elif p[2] == "<":   p[0] = p[1] < p[3]
        elif p[2] == ">":   p[0] = p[1] > p[3]
        elif p[2] == "<=":  p[0] = p[1] <= p[3]
        else:               p[0] = p[1] >= p[3]

    def p_bool_exp_2(self, p):
        """ bool_exp : bool_exp LAND bool_exp
                     | bool_exp LOR bool_exp
        """
        if p[2] == "&&":    p[0] = p[1] and p[3]
        else:               p[0] = p[1] or p[3]

    def p_bool_exp_3(self, p):
        """ bool_exp : LNOT bool_exp
        """
        p[0] = not p[2]

    def p_arith_exp_0(self, p):
        """ arith_exp : literal
        """
        p[0] = p[1]

    def p_arith_exp_1(self, p):
        """ arith_exp : LPAREN arith_exp RPAREN
        """
        p[0] = p[2]


    def p_arith_exp_2(self, p):
        """ arith_exp : arith_exp PLUS arith_exp
                      | arith_exp MINUS arith_exp
                      | arith_exp MULT arith_exp
                      | arith_exp DIVIDE arith_exp
                      | arith_exp MOD arith_exp
                      | arith_exp AND arith_exp
                      | arith_exp XOR arith_exp
                      | arith_exp OR arith_exp
                      | arith_exp LSHIFT arith_exp
                      | arith_exp RSHIFT arith_exp
        """
        if p[2] == '+':     p[0] = p[1] + p[3]
        elif p[2] == '-':   p[0] = p[1] - p[3]
        elif p[2] == '*':   p[0] = p[1] * p[3]
        elif p[2] == '/':   p[0] = p[1] / p[3]
        elif p[2] == '%':   p[0] = p[1] % p[3]
        elif p[2] == '&':   p[0] = p[1] & p[3]
        elif p[2] == '^':   p[0] = p[1] ^ p[3]
        elif p[2] == '|':   p[0] = p[1] | p[3]
        elif p[2] == '<<':  p[0] = p[1] << p[3]
        else:               p[0] = p[1] >> p[3]

    def p_arith_exp_3(self, p):
        """ arith_exp : NOT arith_exp
        """
        p[0] = ~p[2]

    def p_arith_exp_4(self, p):
        """ arith_exp : arith_exp INC
                      | arith_exp DEC
        """
        if p[2] == "++":    p[0] = p[1] + 1
        else:               p[0] = p[1] - 1

    def p_literal(self, p):
        """ literal : field_ref
                    | int_const
        """
        p[0] = p[1]

    # field_ref: BIR keywords
    def p_field_ref_0(self, p):
        """ field_ref : OFFSET
                      | DONE
        """
        p[0] = self.bit_offset if p[1] == "$offset$" else None

    # field_ref: header field value in the packet
    def p_field_ref_1(self, p):
        """ field_ref : ID
        """
        size = self.header.field_size(p[1])
        offset = self.bit_offset + self.header.field_offset(p[1])
        p[0] = self.packet.get_bits(size, offset)

    # field_ref: metadata value
    def p_field_ref_2(self, p):
        """ field_ref : ID PERIOD ID
        """
        p[0] = int(self.packet.metadata[p[1]].get_value(p[3]))

    def p_int_const(self, p):
        """ int_const : INT_CONST_HEX
                      | INT_CONST_DEC
        """
        p[0] = p[1]

    def p_error(self, p):
        if p is None:
            msg = "Incomplete expression: {}".format(self.exp)
            raise BIRParsingError(msg)
        else:
            msg = "Syntax error while parsing token {}".format(p.value)
            raise BIRParsingError(msg)
