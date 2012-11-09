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

void Skeleton::visitCProgram(CProgram *cprogram)
{
  /* Code For CProgram Goes Here */

  cprogram->listtopdef_->accept(this);

}

void Skeleton::visitCFnDef(CFnDef *cfndef)
{
  /* Code For CFnDef Goes Here */

  cfndef->type_->accept(this);
  visitIdent(cfndef->ident_);
  cfndef->listarg_->accept(this);
  cfndef->block_->accept(this);

}

void Skeleton::visitCArg(CArg *carg)
{
  /* Code For CArg Goes Here */

  carg->type_->accept(this);
  visitIdent(carg->ident_);

}

void Skeleton::visitSBlock(SBlock *sblock)
{
  /* Code For SBlock Goes Here */

  sblock->liststmt_->accept(this);

}

void Skeleton::visitSEmpty(SEmpty *sempty)
{
  /* Code For SEmpty Goes Here */


}

void Skeleton::visitSBStmt(SBStmt *sbstmt)
{
  /* Code For SBStmt Goes Here */

  sbstmt->block_->accept(this);

}

void Skeleton::visitSDecl(SDecl *sdecl)
{
  /* Code For SDecl Goes Here */

  sdecl->type_->accept(this);
  sdecl->listitem_->accept(this);

}

void Skeleton::visitSAss(SAss *sass)
{
  /* Code For SAss Goes Here */

  visitIdent(sass->ident_);
  sass->expr_->accept(this);

}

void Skeleton::visitSIncr(SIncr *sincr)
{
  /* Code For SIncr Goes Here */

  visitIdent(sincr->ident_);

}

void Skeleton::visitSDecr(SDecr *sdecr)
{
  /* Code For SDecr Goes Here */

  visitIdent(sdecr->ident_);

}

void Skeleton::visitSRet(SRet *sret)
{
  /* Code For SRet Goes Here */

  sret->expr_->accept(this);

}

void Skeleton::visitSVRet(SVRet *svret)
{
  /* Code For SVRet Goes Here */


}

void Skeleton::visitSCond(SCond *scond)
{
  /* Code For SCond Goes Here */

  scond->expr_->accept(this);
  scond->stmt_->accept(this);

}

void Skeleton::visitSCondElse(SCondElse *scondelse)
{
  /* Code For SCondElse Goes Here */

  scondelse->expr_->accept(this);
  scondelse->stmt_1->accept(this);
  scondelse->stmt_2->accept(this);

}

void Skeleton::visitSWhile(SWhile *swhile)
{
  /* Code For SWhile Goes Here */

  swhile->expr_->accept(this);
  swhile->stmt_->accept(this);

}

void Skeleton::visitSExp(SExp *sexp)
{
  /* Code For SExp Goes Here */

  sexp->expr_->accept(this);

}

void Skeleton::visitSNoInit(SNoInit *snoinit)
{
  /* Code For SNoInit Goes Here */

  visitIdent(snoinit->ident_);

}

void Skeleton::visitSInit(SInit *sinit)
{
  /* Code For SInit Goes Here */

  visitIdent(sinit->ident_);
  sinit->expr_->accept(this);

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

void Skeleton::visitOPlus(OPlus *oplus)
{
  /* Code For OPlus Goes Here */


}

void Skeleton::visitOMinus(OMinus *ominus)
{
  /* Code For OMinus Goes Here */


}

void Skeleton::visitOTimes(OTimes *otimes)
{
  /* Code For OTimes Goes Here */


}

void Skeleton::visitODiv(ODiv *odiv)
{
  /* Code For ODiv Goes Here */


}

void Skeleton::visitOMod(OMod *omod)
{
  /* Code For OMod Goes Here */


}

void Skeleton::visitOLTH(OLTH *olth)
{
  /* Code For OLTH Goes Here */


}

void Skeleton::visitOLE(OLE *ole)
{
  /* Code For OLE Goes Here */


}

void Skeleton::visitOGTH(OGTH *ogth)
{
  /* Code For OGTH Goes Here */


}

void Skeleton::visitOGE(OGE *oge)
{
  /* Code For OGE Goes Here */


}

void Skeleton::visitOEQU(OEQU *oequ)
{
  /* Code For OEQU Goes Here */


}

void Skeleton::visitONE(ONE *one)
{
  /* Code For ONE Goes Here */


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



