from acdcast import *

class FoldingError(Exception):
    pass


def constant_folding(program: list[ASTNode]) -> list[ASTNode]:
    #take a AST and rewrite it into an constantfolded rendition
    new_program = []
    for statement in enumerate(program, start=1):
        if type(statement[1]) == AssignNode: # we only need to fold when an assignnode/expression is here
            try:
                new_statement = _folding_expr(statement[1].expr)  # we replace the line where AssignNode is with folded variant
                name = statement[1].varname

                new_program.append(AssignNode(name, new_statement))
            except:
                new_program.append(statement[1])
        else:
            new_program.append(statement[1])
    
    return new_program
    
    
def _folding_expr(expr: ASTNode) -> ASTNode:
    #given an ASTNode/expression, reduce the expression into a single INTLIT NODE if possible 
    
    if isinstance(expr, IntLitNode):
        value = expr.value
        return IntLitNode(value)
    
    if isinstance(expr, VarRefNode):
        raise FoldingError("VarRefNode in AssignNode, can't fold")
    
    if isinstance(expr, BinOpNode):

        exprleft = _folding_expr(expr.left) # Did you mean: recursion
        exprright = _folding_expr(expr.right)

        #BinOpNode will then be reduced to an IntLitNode and returned to the original tree
        #fold_value = exprleft.value BinopNode.optype exprright.value
        
        if expr.optype is TokenType.PLUS:
            fold_value = exprleft.value + exprright.value
        elif expr.optype is TokenType.MINUS:
            fold_value = exprleft.value - exprright.value
        elif expr.optype is TokenType.TIMES:
            fold_value = exprleft.value * exprright.value
        elif expr.optype is TokenType.DIVIDE:
            fold_value = int(exprleft.value / exprright.value)
        else:
            fold_value = exprleft.value ** exprright.value


        return IntLitNode(fold_value)
        
