from charstream import CharStream
from tokenizer import Tokenizer
from tokenstream import TokenStream
from tokens import *

import sys

# Expectation of program: 
# input filename will be sys.argv[1]
# output filename will be sys.argv[2]
if len(sys.argv) != 3:
    print("Usage: python acdc.py <inputfile> <outputfile>")
    sys.exit(1)

# Get input from file
with open(sys.argv[1], 'r') as inputfile:
    inputcontents = inputfile.read()

cs = CharStream(inputcontents)

try:
    ts = Tokenizer(cs).tokenize()

    with open(sys.argv[2], 'w') as outputfile:
        for token in ts:
            outputfile.write(str(token) + "\n")    


except Exception as e:
    with open(sys.argv[2], 'w') as outputfile:
        outputfile.write(f"ERROR: {type(e).__name__}: {e}\n")
        exit(1)