import sys
import os

from .CodeObject import CodeObject
from .InstructionList import InstructionList
from .instructions import *
from ..compiler import *
from ..ast import *
from ..ast.visitor.AbstractASTVisitor import AbstractASTVisitor

class CodeGenerator(AbstractASTVisitor):

  def __init__(self):
    self.intRegCount = 1 # Changed from 0 so t0 is never used, this way maybe we could use t0 for the constant 0 register
    self.floatRegCount = 1 
    self.intTempPrefix = 't'
    self.floatTempPrefix = 'f'
    self.numCtrlStructs = 1
    self.elselabel = ''
    self._ctrlLabelStack = []

    # Put code here for label counting



  def getIntRegCount(self):
    return self.intRegCount

  def getFloatRegCount(self):
    return self.floatRegCount

  # Generate code for Variables
  #
  # Create a code object that just holds a variable
  # Important: add a pointer from the code object to the symbol table entry so
  # we know how to generate code for it later (we'll need it to find the
  # address)
  #
  # Mark the code object as holding a variable, and also as an lval

  def postprocessVarNode(self, node: VarNode) -> CodeObject:
    sym = node.getSymbol()

    co = CodeObject(sym)
    co.lval = True
    co.type = node.getType()

    return co



  
  def postprocessIntLitNode(self, node: IntLitNode) -> CodeObject:

    co = CodeObject()

    temp = self.generateTemp(Scope.Type.INT)
    val = node.getVal()
    #LI t2, 5 ; call the LI function in instruction, this will be a common theme
    co.code.append(Li(temp, val))
    co.temp = temp
    co.lval = False
    co.type = node.getType()


    return co


  def postprocessFloatLitNode(self, node: FloatLitNode) -> CodeObject:

    co = CodeObject()

    temp = self.generateTemp(Scope.Type.FLOAT)
    val = node.getVal()
    #LI t2, 5 ; call the LI function in instruction, this will be a common theme
    co.code.append(FImm(temp, val))
    co.temp = temp
    co.lval = False
    co.type = node.getType()
    return co

  def postprocessBinaryOpNode(self, node: BinaryOpNode, left: CodeObject, right: CodeObject) -> CodeObject:
    ''' 
    Copy from PA8
    '''
    co = CodeObject()
    newcode = CodeObject()

    #print("Left: ", left, "Left Type: ", left.type)
    #print("Right: ", right, "Right Type: ", right.type)
    #print("Optype: ", str(node.op))

    optype = str(node.op) # Get string corresponding to the operation (+, -, *, /)
    #Step 1: add code from left child
    
    #Step 1a: check if left child is an lval or rval; if lval, rvalify
    if left.lval == True:
      left = self.rvalify(left) # create new code object, fix this, this is bad?
      #print("Left type after rvalify:", left.type)
    co.code.extend(left.code)

    #Step 2: add code from right child

    if right.lval == True:
      right = self.rvalify(right)
    
    co.code.extend(right.code)
  
    #Step 2a: check if left child is an lval or rval; if lval, rvalify

    #Step 3: generate correct binop.  8 cases for 4 ops, float vs. int. for 4 arithmetic ops.

    if left.type != right.type:
      print("Incompatible types in binary operation!\n")
    
    # Get appropriate new temporary for result of operation
    if left.type == Scope.Type.INT:
      #print("Processing binop with INTs")
      newtemp = self.generateTemp(Scope.Type.INT)
      if optype == "OpType.ADD":
        newcode = Add(left.temp, right.temp, newtemp)
      elif optype == "OpType.SUB":
        newcode = Sub(left.temp, right.temp, newtemp)
      elif optype == "OpType.MUL":
        newcode = Mul(left.temp, right.temp, newtemp)
      elif optype == "OpType.DIV":
        newcode = Div(left.temp, right.temp, newtemp)
      else:
        print("Bad operation in binop!\n")


    elif left.type == Scope.Type.FLOAT:
      newtemp = self.generateTemp(Scope.Type.FLOAT)
      if optype == "OpType.ADD":
        newcode = FAdd(left.temp, right.temp, newtemp)
      elif optype == "OpType.SUB":
        newcode = FSub(left.temp, right.temp, newtemp)
      elif optype == "OpType.MUL":
        newcode = FMul(left.temp, right.temp, newtemp)
      elif optype == "OpType.DIV":
        newcode = FDiv(left.temp, right.temp, newtemp)
      else:
        print("Bad operation in binop!\n")

    else:
      print("Bad type in binary op!\n")


    #Step 4: update temp, lval etc., return code object


    co.code.append(newcode)
    co.lval = False
    co.temp = newtemp
    co.type = left.type
    #print(newcode)
    return co
	 



  def postprocessUnaryOpNode(self, node: UnaryOpNode, expr: CodeObject) -> CodeObject:
    
    #Unary Op Node would be telling us to do -(expr)
    
    co = CodeObject()  # Step 0

    exprcode = expr.code # Add in all the code required to get the expr

    if expr.lval:
      expr = self.rvalify(expr)

    co.code.extend(expr.code)

    if expr.type == Scope.Type.INT:
      temp = self.generateTemp(Scope.Type.INT)
      co.code.append(Neg(src=expr.temp, dest=temp))

    elif expr.type == Scope.Type.FLOAT:
      temp = self.generateTemp(Scope.Type.FLOAT)
      co.code.append(FNeg(src=expr.temp, dest=temp))
      
    else:
      raise Exception("Non int/float in unary op!")
    co.lval = False
    co.temp = temp
    co.type = expr.type
    return co
  
  def postprocessAssignNode(self, node: AssignNode, left: CodeObject, right: CodeObject) -> CodeObject:
    
    co = CodeObject()

    address = self.generateAddrFromVariable(left)
    temp2 = self.generateTemp(Scope.Type.INT)
    co.code.append(La(temp2, str(address)))

    if right.lval:
      right = self.rvalify(right)
    
    co.code.extend(right.code)
    temp = right.temp
    if right.type == Scope.Type.INT:
      co.code.append(Sw(temp, temp2, '0'))
    elif right.type == Scope.Type.FLOAT:
      co.code.append(Fsw(temp, temp2, '0'))
    return co

  def postprocessStatementListNode(self, node: StatementListNode, statements: list) -> CodeObject:
    co = CodeObject()

    for subcode in statements:
      co.code.extend(subcode.code)

    co.type = None
    return co

	 # Generate code for read
	 # 
	 # Step 0: create new code object
	 # Step 1: add code from VarNode (make sure it's an lval)
	 # Step 2: generate GetI instruction, storing into temp
	 # Step 3: generate store, to store temp in variable
	
  def postprocessReadNode(self, node: ReadNode, var: CodeObject) -> CodeObject:
    #only varrefs are the readnode
    assert(var.isVar())
    co = CodeObject()

    if var.type is Scope.Type.INT:
      temp = self.generateTemp(Scope.Type.INT)  #read the example.asm's to see the patterns
      co.code.append(GetI(temp))
      address = self.generateAddrFromVariable(var)
      temp2 = self.generateTemp(Scope.Type.INT)
      co.code.append(La(temp2, str(address)))
      co.code.append(Sw(temp, temp2, '0'))
    
    
    elif var.type is Scope.Type.FLOAT:
      temp = self.generateTemp(Scope.Type.FLOAT)  #read the example.asm's to see the patterns
      co.code.append(GetF(temp))
      address = self.generateAddrFromVariable(var)
      temp2 = self.generateTemp(Scope.Type.INT) # this is an address, these are always INTs
      co.code.append(La(temp2, str(address)))
      co.code.append(Fsw(temp, temp2, '0'))
    
    else:
      raise Exception("Bad Type in read node!")



    return co
	 

  def postprocessWriteNode(self, node: WriteNode, expr: CodeObject) -> CodeObject:
    #get this to work first
    co = CodeObject()


    if expr.type == Scope.Type.STRING:
      temp = self.generateTemp(Scope.Type.INT)
      address = expr.getSTE().getAddress()  
      co.code.append(La(temp, str(address)))
      co.code.append(PutS(temp))


    elif expr.type == Scope.Type.INT:
      if expr.isVar() is True:
        expr = self.rvalify(expr)
      co.code.extend(expr.code)
      co.code.append(PutI(expr.temp))
      
    elif expr.type == Scope.Type.FLOAT: 
      if expr.isVar() is True:
        expr = self.rvalify(expr)
      co.code.extend(expr.code)
      co.code.append(PutF(expr.temp))
  
    else:
      raise Exception("Bad type in write node!")
    
    return co





  def postprocessCondNode(self, node: CondNode, left: CodeObject, right: CodeObject) -> CodeObject:
    '''
    NEW:
    '''
    co = CodeObject()

    
    if left.type != right.type:
      raise Exception("Bad cmp types in CondNode!")
    
    node.setOp(node.getReversedOp(node.getOp())) # Reverse comparison type
      
    if right.lval:
      right = self.rvalify(right)
    co.code.extend(right.code)
    if left.lval:
      left = self.rvalify(left)
    co.code.extend(left.code)
    

    labelnum = self._getnumCtrlStruct() + 1
    self._ctrlLabelStack.append(labelnum)
    elselabel = self._generateElseLabel(labelnum)
    optype = str(node.getOp())

    if left.type == Scope.Type.INT:
      if optype == 'OpType.EQ':
        co.code.append(Beq(left.temp, right.temp, elselabel))
      elif optype == 'OpType.NE':
        co.code.append(Bne(left.temp, right.temp, elselabel))
      elif optype == 'OpType.LT':
        co.code.append(Blt(left.temp, right.temp, elselabel))      
      elif optype == 'OpType.LE':
        co.code.append(Ble(left.temp, right.temp, elselabel))
      elif optype == 'OpType.GT':
        co.code.append(Bgt(left.temp, right.temp, elselabel))
      elif optype == 'OpType.GE':
        co.code.append(Bge(left.temp, right.temp, elselabel))    
      else:
        raise Exception("Bad Cond in CondNode!")
      
    elif left.type == Scope.Type.FLOAT:
      fcmptemp = self.generateTemp(Scope.Type.INT)
      if optype == 'OpType.EQ':
        co.code.append(Feq(left.temp, right.temp, fcmptemp))
        co.code.append(Beq(fcmptemp, 'x0', elselabel))
      elif optype == 'OpType.NE':
        co.code.append(Feq(left.temp, right.temp, fcmptemp))
        co.code.append(Bne(fcmptemp, 'x0', elselabel))
      elif optype == 'OpType.LT':
        co.code.append(Flt(left.temp, right.temp, fcmptemp))
        co.code.append(Bne(fcmptemp, 'x0', elselabel))
      elif optype == 'OpType.LE':
        co.code.append(Fle(left.temp, right.temp, fcmptemp))
        co.code.append(Bne(fcmptemp, 'x0', elselabel))
      elif optype == 'OpType.GT':
        co.code.append(Fle(left.temp, right.temp, fcmptemp))
        co.code.append(Beq(fcmptemp, 'x0', elselabel))
      elif optype == 'OpType.GE':
        co.code.append(Flt(left.temp, right.temp, fcmptemp))
        co.code.append(Beq(fcmptemp, 'x0', elselabel))
      else:
        raise Exception("Bad Cond in CondNode")
      

    return co




  def postprocessIfStatementNode(self, node: IfStatementNode, cond: CodeObject, tlist: CodeObject, elist: CodeObject) -> CodeObject:
    '''
    NEW
    '''
    co = CodeObject()
    


    self._incrnumCtrlStruct()
    labelnum = self._ctrlLabelStack.pop()


    donelabel = self._generateDoneLabel(labelnum)
    donecolon = donelabel + ':'

    #co.code.extend(cond.code)

    elselabel = self._generateElseLabel(labelnum)
    elsecolon = elselabel + ':'
    #self._incrnumCtrlStruct()

    
    co.code.extend(cond.code)


    co.code.extend(tlist.code)
    co.code.append(J(donelabel))
    co.code.append(elsecolon)
    if elist is not None:
      co.code.extend(elist.code)
    co.code.append(donecolon)
    
    #self._incrnumCtrlStruct()

    return co



  def postprocessWhileNode(self, node: WhileNode, cond: CodeObject, wlist:CodeObject) -> CodeObject:
    ''' 
    NEW
    '''
    co = CodeObject()

    self._incrnumCtrlStruct()
    labelnum = self._ctrlLabelStack.pop()

    elselabel = self._generateElseLabel(labelnum)
    looplabel = self._generateLoopLabel(labelnum)
    colonelse = elselabel + ':'
    colonloop = looplabel + ':'



    co.code.append(colonloop)
    co.code.extend(cond.code)
    co.code.extend(wlist.code)
    co.code.append(J(looplabel))
    co.code.append(colonelse)
    #self._incrnumCtrlStruct()

    return co
  


  
  def postprocessReturnNode(self, node: ReturnNode, retExpr: CodeObject) -> CodeObject:

    co = CodeObject()


    if retExpr.lval is True:
      retExpr = self.rvalify(retExpr)

    co.code.extend(retExpr.code)
    co.code.append(Halt())
    co.type = None


    return co
  
  def generateTemp(self, t: Scope.Type) -> str:
    if t == Scope.Type.INT:
      s = self.intTempPrefix + str(self.intRegCount)
      self.intRegCount += 1
      return s
    elif t == Scope.Type.FLOAT:
      s = self.floatTempPrefix + str(self.floatRegCount)
      self.floatRegCount += 1
      return s
    else:
      raise Exception("Generating temp for bad type")

  
  




  def rvalify(self, lco : CodeObject) -> CodeObject:
    assert (lco.lval is True)
    assert(lco.isVar() is True)

    co = CodeObject()
 
    address = self.generateAddrFromVariable(lco)
    temp1 = self.generateTemp(Scope.Type.INT)
    co.code.append(La(temp1, str(address)))

    if lco.type is Scope.Type.INT:
      temp2 = self.generateTemp(Scope.Type.INT)
      co.code.append(Lw(temp2, temp1, '0'))
    elif lco.type is Scope.Type.FLOAT: 
      temp2 = self.generateTemp(Scope.Type.FLOAT)
      co.code.append(Flw(temp2, temp1, '0'))

    else:
      raise Exception("Bad type in rvalify!")
    
    co.type = lco.type
    co.lval = False
    co.temp = temp2

    return co
  
  def generateAddrFromVariable(self, lco: CodeObject) -> str:
    assert (lco.isVar() is True)
  
    symbol = lco.getSTE()
    address = symbol.addressToString()

  
    return address
  


  # Here we should define functions that generate labels for conditionals and loops

  def _incrnumCtrlStruct(self):
    self.numCtrlStructs += 1

  def _getnumCtrlStruct(self) -> int:
    return self.numCtrlStructs
  
  def _generateThenLabel(self, num: int) -> str: 
    return "then_"+str(num) 
  
  def _generateElseLabel(self, num: int) -> str:
    return "else_"+str(num) 

  def _generateLoopLabel(self, num: int) -> str:
    return "loop_"+str(num) 

  def _generateDoneLabel(self, num: int) -> str:
    return "done_"+str(num) 
  
