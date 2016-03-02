from ply import lex
from ply.lex import TOKEN
from ply import yacc

class InstructionParser(object):
    def __init__(self):
        self.lexer = lex.lex(module=self, debug=False)
        self.parser = yacc.yacc(module=self, write_tables=0, debug=False, 
                                start='exp')

    def evaluate(self, expression, header, packet, bit_offset=0):
        self.header = header
        self.packet = packet
        self.bit_offset = bit_offset

        return self.parser.parse(expression, lexer=self.lexer)

    # Lexer Tokens
    # ----- ----- ----- ----- ----- ----- ----- ----- -----
    tokens = ( 
        'ID', 'PERIOD',
        'INT_CONST_DEC', 'INT_CONST_HEX',
        'LPAREN', 'RPAREN',
        'PLUS', 'MINUS',
        'AND', 'OR', 'XOR'
    )
    t_PERIOD    = r'\.'
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_AND       = r'&'
    t_OR        = r'\|'
    t_ignore    = ' \t\n'

    identifier  = r'[a-zA-Z][0-9a-zA-Z_]*'
    dec_const   = '[1-9][0-9]*'
    hex_const   = '0[xX][0-9a-fA-F]+'

    @TOKEN(identifier) 
    def t_ID(self, t):
        t.type = 'ID'
        return t

    @TOKEN(dec_const)
    def t_INT_CONST_DEC(self, t):
        t.value = int(t.value)
        return t
    
    @TOKEN(hex_const)
    def t_INT_CONST_HEX(self, t):
        t.value = int(t.value, 16)
        return t

    def t_error(self, t):
        print "Illegal instruction character '{0}'".format(t.value[0])
        t.lexer.skip(1)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    # Parser States
    # ----- ----- ----- ----- ----- ----- ----- ----- -----
    precedence = (
        ('left', 'RPAREN'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'LPAREN')
    )

    def p_exp_0(self, p):
        """ exp : literal
        """
        p[0] = p[1]

    def p_exp_1(self, p):
        """ exp : RPAREN exp LPAREN
        """
        p[0] = p[2]

    def p_exp_2(self, p):
        """ exp : exp PLUS exp
                | exp MINUS exp
                | exp OR exp
                | exp XOR exp
                | exp AND exp
        """
        if   p[2] == 'PLUS':    p[0] = p[1] + p[3]
        elif p[2] == 'MINUS':   p[0] = p[1] - p[3]
        elif p[2] == 'OR':      p[0] = p[1] | p[3]
        elif p[2] == 'XOR':     p[0] = p[1] ^ p[3]
        else:                   p[0] = p[1] & p[3]

    def p_literal_0(self, p):
        """ literal : INT_CONST_DEC
                    | INT_CONST_HEX
                    | header_field
                    | metadata_field
        """
        p[0] = p[1]

    def p_header_field_0(self, p):
        """ header_field : ID
        """
        size = self.header.field_size(p[1])
        offset = self.bit_offset + self.header.field_offset(p[1])
        p[0] = self.packet.get_bits(size, offset)

    def p_metadata_field_0(self, p):
        """ metadata_field : ID PERIOD ID
        """
        p[0] = int(self.packet.metadata[p[1]].get_value(p[3]))

    def p_error(self, p):
        # FIXME: output a useful message
        pass
