from tokens import *

class TokenStream:
    
    def __init__(self):
        self.tokens: list[Token] = []

    def append(self, token: Token) -> None:
        self.tokens.append(token)

    def __iter__(self):
        return iter(self.tokens)
    
    def __len__(self):
        return len(self.tokens)