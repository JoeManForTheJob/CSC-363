# Paste tokenizer here
from charstream import CharStream
from tokens import Token, TokenType
from tokenstream import TokenStream
from acdcast import *
import string

RESERVED = {'i', 'f', 'o', 'n', 'p', 'l', 's'}
VALID_VARS = set(string.ascii_lowercase) - RESERVED

class Tokenizer:

    def __init__(self, cs: CharStream):
        self.cs = cs

    def tokenize(self) -> TokenStream:
        ts = TokenStream()
        while True:
            tok = self.nexttoken()
            ts.append(tok)
            if tok.tokentype == TokenType.EOF:
                break

        return ts
    

    def nexttoken(self) -> Token:

        char = self.cs.read()

        while char in {' ', '\n', '\r', '\t'}:
            char = self.cs.read() # Consume chars for space, newline, etc.
        
        
        if char == '':
            return Token(TokenType.EOF, lexeme = f"{char}")



        match char:

            case '=':
                return Token(TokenType.ASSIGN, lexeme = f"{char}")
            
            case '(':
                 return Token(TokenType.LPAREN, lexeme = f"{char}")
                
            case ')': 
                 return Token(TokenType.RPAREN, lexeme = f"{char}")
            
            case '+':
                 return Token(TokenType.PLUS, lexeme = f"{char}")

            case '-':
                 return Token(TokenType.MINUS, lexeme = f"{char}")
            
            case '*':
                 return Token(TokenType.TIMES, lexeme = f"{char}")
            
            case '/':
                 return Token(TokenType.DIVIDE, lexeme = f"{char}")
            
            case '^':
                 return Token(TokenType.EXPONENT, lexeme = f"{char}")
            
            case 'i':
                var = self.cs.read() 
                while var == ' ' or var == '\t':
                    var = self.cs.read()
                if var not in VALID_VARS:
                    raise ValueError("Invalid variable character: '"+ var+"'")
                return Token(TokenType.INTDEC, lexeme = f"{char}" + f"{var}", name=var)

            case 'p':
                var = self.cs.read() 
                while var == ' ' or var == '\t':
                    var = self.cs.read()
                if var not in VALID_VARS:
                    raise ValueError("Invalid variable character: '"+ var+"'")
                return Token(TokenType.PRINT, lexeme = f"{char}" + f"{var}", name=var)
            
            case _:
                pass # Move on to secondary inspection to handle digits, vars, error case

        if char.isdigit():
            lexeme, intvalue = self.readintliteral(char)
            return Token(TokenType.INTLIT, lexeme = lexeme, intvalue = intvalue)


        if char.isalpha():
            if char in RESERVED:
                raise ValueError(f"Invalid variable character: {char}")
            else:
                return Token(TokenType.VARREF, lexeme = f"{char}", name = f"{char}")
           
        raise ValueError(f"Unexpected character: {char!r}")
        
    

    def readintliteral(self, firstchar: str) -> tuple[str, int]:
        
        digits: list[str] = []
        digits.append(firstchar)
        #if CONDITION:
        #    raise ValueError("Integer literal cannot have a leading zero")

        #while not self.cs.eof() and SOMETHING:
        #    digits.append(SOMETHING)
        intstr = '0123456789'
        if  firstchar == '0' and self.cs.peek() == '0':
            raise ValueError("Integer literal cannot have a leading zero")
        
        while not self.cs.eof() and self.cs.peek() in intstr :
            digits.append(self.cs.read())
        lexeme = ''.join(digits)

        return lexeme, int(lexeme)