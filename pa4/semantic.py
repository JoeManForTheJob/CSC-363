from acdcast import *

class SemanticError(Exception):
    pass


def semanticanalysis(program: list[ASTNode]) -> None:

    declared = []
    initialized = []

    for linenumber, statement in enumerate(program, start=1):
        _semantic_check_stmt(statement, declared, initialized, linenumber)
    
    return None


def _semantic_check_stmt(statement: ASTNode, declared: list[str], initialized: list[str], linenumber: int) -> None:

    if isinstance(statement, IntDclNode):
        varname = statement.varname
        if varname in declared:
            raise SemanticError(f"Variable {varname!r} redeclared at line {linenumber}")
        else:
            declared.append(varname)
            return None
        
    
    if isinstance(statement, PrintNode):
        varname = statement.varname
        if varname not in declared:
            raise SemanticError(f"Trying to print undeclared variable {varname!r} at line {linenumber}")
        elif varname not in initialized:
            raise SemanticError(f"Trying to print uninitialized variable {varname!r} at line {linenumber}")
        else:
            return None

    
    if isinstance(statement, AssignNode):
        varname = statement.varname
        expr = statement.expr
        if varname not in declared:
            raise SemanticError(f"Assignment to undeclared variable {varname!r} at line {linenumber}")
        elif _semantic_check_expr(expr, declared, initialized, linenumber):
            initialized.append(varname)
            return None


    raise SemanticError("Unknown statement type at line {linenumber}")
    # Catches any weird statement types; this should never happen for a validly parsed program
    # Keeping it here though will help if your parser has an undiscovered or unfixed bug


def _semantic_check_expr(expr: ASTNode, declared: list[str], initialized: list[str], linenumber: int) -> bool:
    if isinstance(expr, IntLitNode):
        return True
    
    if isinstance(expr, VarRefNode):
        varname = expr.varname
        if varname not in declared:
            raise SemanticError(f"Use of undeclared variable {varname!r} at line {linenumber}")
        elif varname not in initialized:
            raise SemanticError(f"Use of unitialized variable {varname!r} at line {linenumber}")
        else:
            return True
        
    if isinstance(expr, BinOpNode):
        exprleft = expr.left
        exprright = expr.right
        if _semantic_check_expr(exprleft, declared, initialized, linenumber) and _semantic_check_expr(exprright, declared, initialized, linenumber):
            return True
        else:
            return False
    
    raise SemanticError(f"Unknown expression type at line {linenumber}")
    # Catches any weird statement types; this should never happen for a validly parsed program
    # Keeping it here though will help if your parser has an undiscovered or unfixed bug