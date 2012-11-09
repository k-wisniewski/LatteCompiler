#include "SemanticAnalyzer.hpp"



void Typecheck::visitProgram(Program* t) {} //abstract class
void Typecheck::visitTopDef(TopDef* t) {} //abstract class
void Typecheck::visitArg(Arg* t) {} //abstract class
void Typecheck::visitBlock(Block* t) {} //abstract class
void Typecheck::visitStmt(Stmt* t) {} //abstract class
void Typecheck::visitItem(Item* t) {} //abstract class
void Typecheck::visitType(Type* t) {} //abstract class
void Typecheck::visitExpr(Expr* t) {} //abstract class
void Typecheck::visitAddOp(AddOp* t) {} //abstract class
void Typecheck::visitMulOp(MulOp* t) {} //abstract class
void Typecheck::visitRelOp(RelOp* t) {} //abstract class

void Typecheck::visitCProgram(CProgram *cprogram)
{
    
    cprogram->listtopdef_->accept(this);

}

void Typecheck::visitCFnDef(CFnDef *cfndef)
{
    //cfndef->type_->accept(this);
    //cfndef->listarg_->accept(this);
    visitIdent(cfndef->ident_);
    definedFunctions.insert(std::make_pair(currentSymbol, cfndef));
    environmentStack.push_back(Env());
    for (auto it = cfndef->listarg_->begin; it != cfndef->listarg_->end(); ++it)
    {
        environmentStack.rbegin()->insert(
            make_pair(it->ident_, VariableInfo(*(it->type_), it->ident_)));
    }
    environmentStack.pop_back();
    cfndef->block_->accept(this);
}

void Typecheck::visitCArg(CArg *carg)
{
    /* Code For CArg Goes Here */

    carg->type_->accept(this);
    visitIdent(carg->ident_);

}

void Typecheck::visitSBlock(SBlock *sblock)
{
    /* Code For SBlock Goes Here */

    sblock->liststmt_->accept(this);
}

void Typecheck::visitSEmpty(SEmpty *sempty)
{
    /* Code For SEmpty Goes Here */


}

void Typecheck::visitSBStmt(SBStmt *sbstmt)
{
    /* Code For SBStmt Goes Here */
    environmentStack.push_back(Env());
    sbstmt->block_->accept(this);
    environmentStack.pop_back();
}

void Typecheck::visitSDecl(SDecl *sdecl)
{
    /* Code For SDecl Goes Here */
    sdecl->type_->accept(this);
    sdecl->listitem_->accept(this);

}

void Typecheck::visitSAss(SAss *sass)
{
    /* Code For SAss Goes Here */

    visitIdent(sass->ident_);
    sass->expr_->accept(this);

}

void Typecheck::visitSIncr(SIncr *sincr)
{
    /* Code For SIncr Goes Here */

    visitIdent(sincr->ident_);

}

void Typecheck::visitSDecr(SDecr *sdecr)
{
    /* Code For SDecr Goes Here */

    visitIdent(sdecr->ident_);

}

void Typecheck::visitSRet(SRet *sret)
{
    /* Code For SRet Goes Here */

    sret->expr_->accept(this);

}

void Typecheck::visitSVRet(SVRet *svret)
{
    /* Code For SVRet Goes Here */


}

void Typecheck::visitSCond(SCond *scond)
{
    /* Code For SCond Goes Here */

    scond->expr_->accept(this);
    scond->stmt_->accept(this);

}

void Typecheck::visitSCondElse(SCondElse *scondelse)
{
    /* Code For SCondElse Goes Here */

    scondelse->expr_->accept(this);
    scondelse->stmt_1->accept(this);
    scondelse->stmt_2->accept(this);

}

void Typecheck::visitSWhile(SWhile *swhile)
{
    /* Code For SWhile Goes Here */

    swhile->expr_->accept(this);
    swhile->stmt_->accept(this);

}

void Typecheck::visitSExp(SExp *sexp)
{
    /* Code For SExp Goes Here */

    sexp->expr_->accept(this);

}

void Typecheck::visitSNoInit(SNoInit *snoinit)
{
    /* Code For SNoInit Goes Here */

    visitIdent(snoinit->ident_);

    environmentStack.rbegin()->insert(
        VariableInfo(lastType, currentSymbol));
}

void Typecheck::visitSInit(SInit *sinit)
{
    /* Code For SInit Goes Here */

    visitIdent(sinit->ident_);
    sinit->expr_->accept(this);

}

void Typecheck::visitTInt(TInt *tint)
{
    this.lastType = *tint;
}

void Typecheck::visitTStr(TStr *tstr)
{
    this.lastType = *tstr;
}

void Typecheck::visitTBool(TBool *tbool)
{
    this.lastType = *tbool;
}

void Typecheck::visitTVoid(TVoid *tvoid)
{
    this.lastType = *tvoid;
}

void Typecheck::visitEVar(EVar *evar)
{
    visitIdent(evar->ident_);

}

void Typecheck::visitELitInt(ELitInt *elitint)
{
    /* Code For ELitInt Goes Here */

    visitInteger(elitint->integer_);

}

void Typecheck::visitELitTrue(ELitTrue *elittrue)
{
    /* Code For ELitTrue Goes Here */


}

void Typecheck::visitELitFalse(ELitFalse *elitfalse)
{
    /* Code For ELitFalse Goes Here */


}

void Typecheck::visitEApp(EApp *eapp)
{
    /* Code For EApp Goes Here */

    visitIdent(eapp->ident_);
    eapp->listexpr_->accept(this);

}

void Typecheck::visitEString(EString *estring)
{
    /* Code For EString Goes Here */

    visitString(estring->string_);

}

void Typecheck::visitNeg(Neg *neg)
{
    /* Code For Neg Goes Here */

    neg->expr_->accept(this);

}

void Typecheck::visitNot(Not *not)
{
    /* Code For Not Goes Here */

    not->expr_->accept(this);

}

void Typecheck::visitEMul(EMul *emul)
{
    /* Code For EMul Goes Here */

    emul->expr_1->accept(this);
    emul->mulop_->accept(this);
    emul->expr_2->accept(this);

}

void Typecheck::visitEAdd(EAdd *eadd)
{
    /* Code For EAdd Goes Here */

    eadd->expr_1->accept(this);
    eadd->addop_->accept(this);
    eadd->expr_2->accept(this);

}

void Typecheck::visitERel(ERel *erel)
{
    /* Code For ERel Goes Here */

    erel->expr_1->accept(this);
    erel->relop_->accept(this);
    erel->expr_2->accept(this);

}

void Typecheck::visitEAnd(EAnd *eand)
{
    /* Code For EAnd Goes Here */

    eand->expr_1->accept(this);
    eand->expr_2->accept(this);

}

void Typecheck::visitEOr(EOr *eor)
{
    /* Code For EOr Goes Here */

    eor->expr_1->accept(this);
    eor->expr_2->accept(this);

}

void Typecheck::visitOPlus(OPlus *oplus)
{
    /* Code For OPlus Goes Here */


}

void Typecheck::visitOMinus(OMinus *ominus)
{
    /* Code For OMinus Goes Here */


}

void Typecheck::visitOTimes(OTimes *otimes)
{
    /* Code For OTimes Goes Here */


}

void Typecheck::visitODiv(ODiv *odiv)
{
    /* Code For ODiv Goes Here */


}

void Typecheck::visitOMod(OMod *omod)
{
    /* Code For OMod Goes Here */


}

void Typecheck::visitOLTH(OLTH *olth)
{
    /* Code For OLTH Goes Here */


}

void Typecheck::visitOLE(OLE *ole)
{
    /* Code For OLE Goes Here */


}

void Typecheck::visitOGTH(OGTH *ogth)
{
    /* Code For OGTH Goes Here */


}

void Typecheck::visitOGE(OGE *oge)
{
    /* Code For OGE Goes Here */


}

void Typecheck::visitOEQU(OEQU *oequ)
{
    /* Code For OEQU Goes Here */


}

void Typecheck::visitONE(ONE *one)
{
    /* Code For ONE Goes Here */


}


void Typecheck::visitListTopDef(ListTopDef* listtopdef)
{
    for (std::vector<TopDef*>::iterator i = listtopdef->begin() ; i != listtopdef->end() ; ++i)
    {
        (*i)->accept(this);
    }
}

void Typecheck::visitListArg(ListArg* listarg)
{
    for (std::vector<Arg*>::iterator i = listarg->begin() ; i != listarg->end() ; ++i)
    {
        (*i)->accept(this);
    }
}

void Typecheck::visitListStmt(ListStmt* liststmt)
{
    for (std::vector<Stmt*>::iterator i = liststmt->begin() ; i != liststmt->end() ; ++i)
    {
        (*i)->accept(this);
    }
}

void Typecheck::visitListItem(ListItem* listitem)
{
    for (std::vector<Item*>::iterator i = listitem->begin() ; i != listitem->end() ; ++i)
    {
        (*i)->accept(this);
    }
}

void Typecheck::visitListExpr(ListExpr* listexpr)
{
    for (std::vector<Expr*>::iterator i = listexpr->begin() ; i != listexpr->end() ; ++i)
    {
        (*i)->accept(this);
    }
}


void Typecheck::visitInteger(Integer x)
{
    /* Code for Integer Goes Here */
}

void Typecheck::visitChar(Char x)
{
    /* Code for Char Goes Here */
}

void Typecheck::visitDouble(Double x)
{
    /* Code for Double Goes Here */
}

void Typecheck::visitString(String x)
{
    /* Code for String Goes Here */
}

void Typecheck::visitIdent(Ident const& name)
{
    if (isKnownSymbol(name))
    {
        throw IdentifierAlreadyDefined;
    }
    currentSymbol = name;
}

