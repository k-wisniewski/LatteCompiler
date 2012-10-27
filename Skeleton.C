/*** BNFC-Generated Visitor Design Pattern Skeleton. ***/
/* This implements the common visitor design pattern.
   Note that this method uses Visitor-traversal of lists, so
   List->accept() does NOT traverse the list. This allows different
   algorithms to use context information differently. */

#include "Skeleton.H"



void Skeleton::visitProgram(Program* t) {} //abstract class
void Skeleton::visitTopDef(TopDef* t) {} //abstract class
void Skeleton::visitArg(Arg* t) {} //abstract class
void Skeleton::visitBlock(Block* t) {} //abstract class
void Skeleton::visitStmt(Stmt* t) {} //abstract class
void Skeleton::visitItem(Item* t) {} //abstract class
void Skeleton::visitType(Type* t) {} //abstract class
void Skeleton::visitExpr(Expr* t) {} //abstract class
void Skeleton::visitAddOp(AddOp* t) {} //abstract class
void Skeleton::visitMulOp(MulOp* t) {} //abstract class
void Skeleton::visitRelOp(RelOp* t) {} //abstract class

void Skeleton::visitTProgram(TProgram *tprogram)
{
  /* Code For TProgram Goes Here */

  tprogram->listtopdef_->accept(this);

}

void Skeleton::visitTFnDef(TFnDef *tfndef)
{
  /* Code For TFnDef Goes Here */

  tfndef->type_->accept(this);
  visitIdent(tfndef->ident_);
  tfndef->listarg_->accept(this);
  tfndef->block_->accept(this);

}

void Skeleton::visitTArg(TArg *targ)
{
  /* Code For TArg Goes Here */

  targ->type_->accept(this);
  visitIdent(targ->ident_);

}

void Skeleton::visitTBlock(TBlock *tblock)
{
  /* Code For TBlock Goes Here */

  tblock->liststmt_->accept(this);

}

void Skeleton::visitEmpty(Empty *empty)
{
  /* Code For Empty Goes Here */


}

void Skeleton::visitBStmt(BStmt *bstmt)
{
  /* Code For BStmt Goes Here */

  bstmt->block_->accept(this);

}

void Skeleton::visitDecl(Decl *decl)
{
  /* Code For Decl Goes Here */

  decl->type_->accept(this);
  decl->listitem_->accept(this);

}

void Skeleton::visitAss(Ass *ass)
{
  /* Code For Ass Goes Here */

  visitIdent(ass->ident_);
  ass->expr_->accept(this);

}

void Skeleton::visitIncr(Incr *incr)
{
  /* Code For Incr Goes Here */

  visitIdent(incr->ident_);

}

void Skeleton::visitDecr(Decr *decr)
{
  /* Code For Decr Goes Here */

  visitIdent(decr->ident_);

}

void Skeleton::visitRet(Ret *ret)
{
  /* Code For Ret Goes Here */

  ret->expr_->accept(this);

}

void Skeleton::visitVRet(VRet *vret)
{
  /* Code For VRet Goes Here */


}

void Skeleton::visitCond(Cond *cond)
{
  /* Code For Cond Goes Here */

  cond->expr_->accept(this);
  cond->stmt_->accept(this);

}

void Skeleton::visitCondElse(CondElse *condelse)
{
  /* Code For CondElse Goes Here */

  condelse->expr_->accept(this);
  condelse->stmt_1->accept(this);
  condelse->stmt_2->accept(this);

}

void Skeleton::visitWhile(While *while)
{
  /* Code For While Goes Here */

  while->expr_->accept(this);
  while->stmt_->accept(this);

}

void Skeleton::visitSExp(SExp *sexp)
{
  /* Code For SExp Goes Here */

  sexp->expr_->accept(this);

}

void Skeleton::visitNoInit(NoInit *noinit)
{
  /* Code For NoInit Goes Here */

  visitIdent(noinit->ident_);

}

void Skeleton::visitInit(Init *init)
{
  /* Code For Init Goes Here */

  visitIdent(init->ident_);
  init->expr_->accept(this);

}

void Skeleton::visitTInt(TInt *tint)
{
  /* Code For TInt Goes Here */


}

void Skeleton::visitTStr(TStr *tstr)
{
  /* Code For TStr Goes Here */


}

void Skeleton::visitTBool(TBool *tbool)
{
  /* Code For TBool Goes Here */


}

void Skeleton::visitTVoid(TVoid *tvoid)
{
  /* Code For TVoid Goes Here */


}

void Skeleton::visitEVar(EVar *evar)
{
  /* Code For EVar Goes Here */

  visitIdent(evar->ident_);

}

void Skeleton::visitELitInt(ELitInt *elitint)
{
  /* Code For ELitInt Goes Here */

  visitInteger(elitint->integer_);

}

void Skeleton::visitELitTrue(ELitTrue *elittrue)
{
  /* Code For ELitTrue Goes Here */


}

void Skeleton::visitELitFalse(ELitFalse *elitfalse)
{
  /* Code For ELitFalse Goes Here */


}

void Skeleton::visitEApp(EApp *eapp)
{
  /* Code For EApp Goes Here */

  visitIdent(eapp->ident_);
  eapp->listexpr_->accept(this);

}

void Skeleton::visitEString(EString *estring)
{
  /* Code For EString Goes Here */

  visitString(estring->string_);

}

void Skeleton::visitNeg(Neg *neg)
{
  /* Code For Neg Goes Here */

  neg->expr_->accept(this);

}

void Skeleton::visitNot(Not *not)
{
  /* Code For Not Goes Here */

  not->expr_->accept(this);

}

void Skeleton::visitEMul(EMul *emul)
{
  /* Code For EMul Goes Here */

  emul->expr_1->accept(this);
  emul->mulop_->accept(this);
  emul->expr_2->accept(this);

}

void Skeleton::visitEAdd(EAdd *eadd)
{
  /* Code For EAdd Goes Here */

  eadd->expr_1->accept(this);
  eadd->addop_->accept(this);
  eadd->expr_2->accept(this);

}

void Skeleton::visitERel(ERel *erel)
{
  /* Code For ERel Goes Here */

  erel->expr_1->accept(this);
  erel->relop_->accept(this);
  erel->expr_2->accept(this);

}

void Skeleton::visitEAnd(EAnd *eand)
{
  /* Code For EAnd Goes Here */

  eand->expr_1->accept(this);
  eand->expr_2->accept(this);

}

void Skeleton::visitEOr(EOr *eor)
{
  /* Code For EOr Goes Here */

  eor->expr_1->accept(this);
  eor->expr_2->accept(this);

}

void Skeleton::visitOpPlus(OpPlus *opplus)
{
  /* Code For OpPlus Goes Here */


}

void Skeleton::visitOpMinus(OpMinus *opminus)
{
  /* Code For OpMinus Goes Here */


}

void Skeleton::visitOpTimes(OpTimes *optimes)
{
  /* Code For OpTimes Goes Here */


}

void Skeleton::visitOpDiv(OpDiv *opdiv)
{
  /* Code For OpDiv Goes Here */


}

void Skeleton::visitOpMod(OpMod *opmod)
{
  /* Code For OpMod Goes Here */


}

void Skeleton::visitOpLTH(OpLTH *oplth)
{
  /* Code For OpLTH Goes Here */


}

void Skeleton::visitOpLE(OpLE *ople)
{
  /* Code For OpLE Goes Here */


}

void Skeleton::visitOpGTH(OpGTH *opgth)
{
  /* Code For OpGTH Goes Here */


}

void Skeleton::visitOpGE(OpGE *opge)
{
  /* Code For OpGE Goes Here */


}

void Skeleton::visitOpEQU(OpEQU *opequ)
{
  /* Code For OpEQU Goes Here */


}

void Skeleton::visitOpNE(OpNE *opne)
{
  /* Code For OpNE Goes Here */


}


void Skeleton::visitListTopDef(ListTopDef* listtopdef)
{
  for (ListTopDef::iterator i = listtopdef->begin() ; i != listtopdef->end() ; ++i)
  {
    (*i)->accept(this);
  }
}

void Skeleton::visitListArg(ListArg* listarg)
{
  for (ListArg::iterator i = listarg->begin() ; i != listarg->end() ; ++i)
  {
    (*i)->accept(this);
  }
}

void Skeleton::visitListStmt(ListStmt* liststmt)
{
  for (ListStmt::iterator i = liststmt->begin() ; i != liststmt->end() ; ++i)
  {
    (*i)->accept(this);
  }
}

void Skeleton::visitListItem(ListItem* listitem)
{
  for (ListItem::iterator i = listitem->begin() ; i != listitem->end() ; ++i)
  {
    (*i)->accept(this);
  }
}

void Skeleton::visitListExpr(ListExpr* listexpr)
{
  for (ListExpr::iterator i = listexpr->begin() ; i != listexpr->end() ; ++i)
  {
    (*i)->accept(this);
  }
}


void Skeleton::visitInteger(Integer x)
{
  /* Code for Integer Goes Here */
}

void Skeleton::visitChar(Char x)
{
  /* Code for Char Goes Here */
}

void Skeleton::visitDouble(Double x)
{
  /* Code for Double Goes Here */
}

void Skeleton::visitString(String x)
{
  /* Code for String Goes Here */
}

void Skeleton::visitIdent(Ident x)
{
  /* Code for Ident Goes Here */
}



