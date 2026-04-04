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
    self.intRegCount = 0
    self.floatRegCount = 0
    self.intTempPrefix = 't'
    self.floatTempPrefix = 'f'

  def getIntRegCount(self):
    return self.intRegCount

  def getFloatRegCount(self):
    return self.floatRegCount




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
      #check type right and left, (int v float), get code, rvalify them if nesscary 
    co = CodeObject()
    if left.lval is True:
      left = self.rvalify(left)
    if right.lval is True:
      right = self.rvalify(right) 
    co.code.extend(left.code)
    co.code.extend(right.code)
    
    if node.getOp() == BinaryOpNode.OpType.ADD:
      if left.type == Scope.Type.INT and right.type == Scope.Type.INT:
        temp = self.generateTemp(Scope.Type.INT)
        co.code.append(Add(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.INT
        co.temp = temp
        co.lval = False

      elif left.type == Scope.Type.FLOAT and right.type == Scope.Type.FLOAT:
        temp = self.generateTemp(Scope.Type.FLOAT)
        co.code.append(FAdd(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.FLOAT
        co.temp = temp
        co.lval = False



    elif node.getOp() == BinaryOpNode.OpType.SUB:
      if left.type == Scope.Type.INT and right.type == Scope.Type.INT:
        temp = self.generateTemp(Scope.Type.INT)
        co.code.append(Sub(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.INT
        co.temp = temp
        co.lval = False

      elif left.type == Scope.Type.FLOAT and right.type == Scope.Type.FLOAT:
        temp = self.generateTemp(Scope.Type.FLOAT)
        co.code.append(FSub(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.FLOAT
        co.temp = temp
        co.lval = False



    elif node.getOp() == BinaryOpNode.OpType.MUL:
      if left.type == Scope.Type.INT and right.type == Scope.Type.INT:
        temp = self.generateTemp(Scope.Type.INT)
        co.code.append(Mul(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.INT
        co.temp = temp
        co.lval = False

      elif left.type == Scope.Type.FLOAT and right.type == Scope.Type.FLOAT:
        temp = self.generateTemp(Scope.Type.FLOAT)
        co.code.append(FMul(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.FLOAT
        co.temp = temp
        co.lval = False


      
    elif node.getOp() == BinaryOpNode.OpType.DIV:
      if left.type == Scope.Type.INT and right.type == Scope.Type.INT:
        temp = self.generateTemp(Scope.Type.INT)
        co.code.append(Div(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.INT
        co.temp = temp
        co.lval = False

      elif left.type == Scope.Type.FLOAT and right.type == Scope.Type.FLOAT:
        temp = self.generateTemp(Scope.Type.FLOAT)
        co.code.append(FDiv(src1=left.temp, src2=right.temp, dest=temp))
        co.type = Scope.Type.FLOAT
        co.temp = temp
        co.lval = False

    else:
      raise Exception("Bad types in binary op node!")

    return co



  def postprocessUnaryOpNode(self, node: UnaryOpNode, expr: CodeObject) -> CodeObject:
    '''
    Unary Op Node would be telling us to do -(expr)
    '''  
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

    return co
  






  def postprocessAssignNode(self, node: AssignNode, left: CodeObject, right: CodeObject) -> CodeObject:
    co = CodeObject()
    #set varable from left, get code from right, rvalify right if nesscary, generate address from left, then sw or fsw depending on type.
    if left.lval is False:
      raise Exception("Left side of assign node isn't an lval!")
    if right.lval is True:
      right = self.rvalify(right)
    co.code.extend(right.code)  
    address = self.generateAddrFromVariable(left)
    if right.type == Scope.Type.INT:
      co.code.append(Sw(right.temp, address, offset='0'))
    elif right.type == Scope.Type.FLOAT:
      co.code.append(Fsw(right.temp, address, offset='0'))
    else:
      raise Exception("Bad type in assign node!")

    return co



  def postprocessStatementListNode(self, node: StatementListNode, statements: list) -> CodeObject:
    co = CodeObject()

    for subcode in statements:
      co.code.extend(subcode.code)

    co.type = None
    return co


	
  def postprocessReadNode(self, node: ReadNode, var: CodeObject) -> CodeObject:
    #only varrefs are the readnode
    assert(var.isVar())
    co = CodeObject()

    if var.type is Scope.Type.INT:
      temp = self.generateTemp(Scope.Type.INT)  #read the example.asm's to see the patterns
      co.code.append(GetI(temp))
      address = self.generateAddrFromVariable(var)
      temp2 = self.generateTemp(Scope.Type.INT)
      co.code.append(La(temp2, address))
      co.code.append(Sw(temp, temp2, '0'))
    
    
    elif var.type is Scope.Type.FLOAT:
      temp = self.generateTemp(Scope.Type.FLOAT)  #read the example.asm's to see the patterns
      co.code.append(GetF(temp))
      address = self.generateAddrFromVariable(var)
      temp2 = self.generateTemp(Scope.Type.INT) # this is an address, these are always INTs
      co.code.append(La(temp2, address))
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
      co.code.append(La(temp, address))
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
    co.code.append(La(temp1, address))

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






  def generateAddrFromVariable(self, lco: CodeObject) -> CodeObject:

    assert (lco.isVar() is True)

    #co = CodeObject()

    #il = InstructionList()

    symbol = lco.getSTE()
    address = str(symbol.getAddress())

    

    return address
  
