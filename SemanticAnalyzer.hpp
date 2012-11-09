#ifndef __SEMANTIC_ANALYZER_HPP
#define __SEMANTIC_ANALYZER_HPP

#include <Absyn.H>
#include <vector>
#include <algorithm>
#include <boost/unordered_map.hpp>
#include <boost/unordered_set.hpp>
#include <exception>
#include <utility>


class IdentifierAlreadyDefined : public exception
{

}

class VariableInfo
{
    Type type;
    Ident name;

public:
    VariableInfo(Type const& type, Ident const& name) :
        type(type), name(name) {}

    Type& getType()
    {
        return this.type;
    }

    Ident& getName()
    {
        return this.name;
    }
};

class Typecheck : Visitor
{
private:
    typedef boost::unordered_map<Ident, VariableInfo> Env;

    Ident currentSymbol;
    std::vector<Env> environmentStack;
    boost::unordered_map<Ident, CFnDef> definedFunctions;

    bool isKnownVariable(Ident const& variableName)
    {
        return environmentStack.rbegin()->find(variableName) !=
            environmentStack.rbegin()->end();
    }

    VariableInfo& getVariableInfo(Ident symbolName)
    {
        return *(symbolTable.find(symbolName));
    }
 
public:
    void visitProgram(Program *p);
    void visitTopDef(TopDef *p);
    void visitArg(Arg *p);
    void visitBlock(Block *p);
    void visitStmt(Stmt *p);
    void visitItem(Item *p);
    void visitType(Type *p);
    void visitExpr(Expr *p);
    void visitAddOp(AddOp *p);
    void visitMulOp(MulOp *p);
    void visitRelOp(RelOp *p);
    void visitCProgram(CProgram *p);
    void visitCFnDef(CFnDef *p);
    void visitCArg(CArg *p);
    void visitSBlock(SBlock *p);
    void visitSEmpty(SEmpty *p);
    void visitSBStmt(SBStmt *p);
    void visitSDecl(SDecl *p);
    void visitSNoInit(SNoInit *p);
    void visitSInit(SInit *p);
    void visitSAss(SAss *p);
    void visitSIncr(SIncr *p);
    void visitSDecr(SDecr *p);
    void visitSRet(SRet *p);
    void visitSVRet(SVRet *p);
    void visitSCond(SCond *p);
    void visitSCondElse(SCondElse *p);
    void visitSWhile(SWhile *p);
    void visitSExp(SExp *p);
    void visitTInt(TInt *p);
    void visitTStr(TStr *p);
    void visitTBool(TBool *p);
    void visitTVoid(TVoid *p);
    void visitEVar(EVar *p);
    void visitELitInt(ELitInt *p);
    void visitELitTrue(ELitTrue *p);
    void visitELitFalse(ELitFalse *p);
    void visitEApp(EApp *p);
    void visitEString(EString *p);
    void visitNeg(Neg *p);
    void visitNot(Not *p);
    void visitEMul(EMul *p);
    void visitEAdd(EAdd *p);
    void visitERel(ERel *p);
    void visitEAnd(EAnd *p);
    void visitEOr(EOr *p);
    void visitOPlus(OPlus *p);
    void visitOMinus(OMinus *p);
    void visitOTimes(OTimes *p);
    void visitODiv(ODiv *p);
    void visitOMod(OMod *p);
    void visitOLTH(OLTH *p);
    void visitOLE(OLE *p);
    void visitOGTH(OGTH *p);
    void visitOGE(OGE *p);
    void visitOEQU(OEQU *p);
    void visitONE(ONE *p);
    void visitListTopDef(ListTopDef *p);
    void visitListArg(ListArg *p);
    void visitListStmt(ListStmt *p);
    void visitListItem(ListItem *p);
    void visitListExpr(ListExpr *p);

    void visitInteger(Integer x);
    void visitChar(Char x);
    void visitDouble(Double x);
    void visitString(String x);
    void visitIdent(Ident const& name);

};

#endif
