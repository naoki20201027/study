# -*- coding: utf-8 -*-
# prolog
# ver3: add "load" function
# mw_prolog: handle clauses as list
# 複数リテラルから成るclauseは':-'を省略し第２引数以降を条件として第１引数が成り立つとする
# 例：　a(*x,*y):-b(*x,*z),c(*z,*y). ==> ['a(*x,*y)','b(*x,*z)','c(*z,*y)']
# mw_prolog: 時系列デバッガdbg_tl追加 
# mw_prolog2: 20200605のノートに基づき改修
# mw_prolog3: mwdbg追加
# mw_prolog4: ck_param2()のunifyをmatch_test()に統合
# mw_prolog5: dbのデータ形式を変更　db=[['f(a,b)',[]],['f(b,c)',[]],['gf(*A,*C)',['f(*A,*B)','f(*B,*C)']]]

import pdb

db = []
ml = 0
dbg_lst = ['goal','target','head','body','literal']
cl = 0 #call level
dbg_start = 1 #debug start flag

def prt_dbl(l):
    for i in range(l):
        print(" ",end="")
        
def mwdbg(func): #decorator for debug
    def new_func(*args, **kwargs):
        global cl, dbg_start
        #debug start condition
        if func=='ck_param':
            if args==[grand_father(adam,*x), ['grand_father(adam,*x)', 'prt(*x)']]:
                dbg_start = 1

        if dbg_start==1:
            cl += 1
            fn = str(func).split(" ")
            # print in & out
            prt_dbl(cl)
            print(">>mwdbg > ",fn[1]," > in args:",*args, " kwargs:",kwargs)
        result = func(*args, **kwargs)
        if dbg_start==1:
            prt_dbl(cl)
            print(">>mwdbg > ",fn[1]," > out:", result)
            
            # do something at specific function 
            if fn[1]=="sub":
                print(">>dbg <<this is ",fn[1],"! >>")
            
            # do something at specific status of variable
            '''  
            print("x:",x)
            if x>15:
                print(">>dbg ------ x>15  Intentionally stop!")
                print(3/0) #intentionally error to stop program.
            '''
            cl -= 1
        #prt_dbl(cl)
        #x=input("     ?")
        return result
    return new_func


def init():
    print(">>",end="")
    for w in dbg_lst:
        print(w,",",end="")
    print("")
    
def dbg_tl(lcls):
    print(">>",end="")
    for x in dbg_lst:
        try:
            print(x,lcls[x],",",end="")
            #print(x,",",end="")
        except KeyError:
            print(x,"- ,",end="")
    print("")
        
@mwdbg
def parser(s):
    global db
    st = 0
    flag = 0
    clauses = []
    body = []
    goal = []
    head_body_flag = 0
    eval_request = 0
    s = s.replace(':-',',')
    print("s:",s)
    if s[0:2]=='?-':
        eval_request = 1
        s=s[2:]
    for i in range(len(s)):
        #print("s[",i,"]=",s[i])
        if flag ==0 and s[i]==',':
            literal = s[st:i]
            st = i+1
            if head_body_flag==0:
                clauses.append(literal)
                head_body_flag=1
                print("clauses:",clauses)
            else:
                body.append(literal)
                print("body:",body)
        elif s[i]=='(':
            flag += 1
            #print("flag:",flag)
        elif s[i]==')':
            flag -= 1
            #print("flag:",flag)
        elif flag < 0:
            print("error")
            print(3/0)
        elif s[i]=='.':
            literal = s[st:-1]
            if head_body_flag==0:
                clauses.append(literal)
                head_body_flag==1
                print("clauses:",clauses)
            else:
                body.append(literal)
                print("body:",body)
    clauses.append(body)
    
    print("parser out clauses:",clauses)
    if eval_request==1:
        goal.append(clauses[0])
        if body != []:
            for literal in body:
                goal.append(literal)
        print("goal:",goal)
    else:
        db.append(clauses)
    print("eval_request:",eval_request)
    if eval_request==1:
        #print("db:",db)
        print(">>> ",eval(clauses))
        #db_parser()
    
def prt_db():
    print("db-----------------")
    for cl in db:
        print(cl)

def db_parser():
    print("db_parser-------------")
    for clause in db:
        print("clause:",clause)
        head = get_head(clause)
        print("head:",head)
        body = get_body(clause)
        print("body:",body)
        for literal in body:
            print("body literal:",literal)        
        
@mwdbg
def eval(goal_clause):
    global ml #match_level
    #dbg_tl(locals())
    #pdb.set_trace()
    ml += 1
    tf = False
    var_list=[]
    dbger(ml,"==> eval ::",locals(),'goal_clause')
    print("---->>>> length of goal:",len(goal_clause))
    
    if len(goal_clause)>1:
        for goal in goal_clause:
            tf = eval(goal)
            if tf==False:
                return False
            else:
                continue
        return True
    elif len(goal_clause)==1:
        goal = goal_clause
        for db_clause in db:
            head = get_head(db_clause)
            tf, var_list = match_test(goal, head)
            if tf:
                goal, db_clauseunify(var_list, goal, db_clause)
            else:
                return False
            
@mwdbg
def get_program(fn):
    f = open(fn,"r")
    for line in f:
        parsing(line)
        
@mwdbg
def get_pred(literal):
    fp = literal.find('(')
    pred = literal[0:fp]
    return pred
    
@mwdbg
def set_db(s):
    dbg(0,["set_db()-----"])
    db.append(s)
    dbg(0,["db:",db])
    for clauses in db:
        dbg(0,["clauses:",clauses])
        
@mwdbg
def get_head(c):
    return c[0]
    
@mwdbg
def get_body(c):
    body = c[1]
    return body

@mwdbg
def get_body2(c):
    return c[1:]

@mwdbg
def has_body(c):
    ans = False
    if c.find(':-'):
        return True
    else:
        return False

#@mwdbg
def get_params(l):
    dbg(1,["get_param() l:",l])
    #param_body = l[l[0].find('(')+1:l[0].find(')')]
    param_body = l[l.find('(')+1:l.find(')')]
    dbg(1,["param_body:",param_body])
    params = param_body.split(',')
    return params

#@mwdbg
def get_literals(c):
    dbg(0,["get_literals in:",c])
    literals = []
    lp = c.find('),')
    if lp > 0 :
        literals.append(c[0:lp+1])
        left = c[lp+2:]
        left_l = get_literals(left)
        if left_l == []:
            literals.append(left)
    dbg(0,["get_literals out:",literals])
    return literals
    

#@mwdbg
def predicate(l):
    dbg(0,["predicate in:",l])
    pp = l.find('(')
    if pp<0:
        dbg(0,["predicate error"])
        dbg(0,["predicate error"])
    else:
        p = l[0:pp]
        return p
    return "False"

#@mwdbg
def ck_pred(goal, clause):
    dbg_l(1,ml,["ck_pred in:",goal, " & ", clause])
    if clause.find(':-')>0: #条件literalが存在するなら
        dbg_l(0,ml,["条件あり",clause])
        head = get_head(clause) #head literal取得
    else:
        head = clause
    dbg_l(0,ml,["head:",head," ?? goal:",goal])
    if predicate(head)==predicate(goal): #goalと対象headの述語が等しいなら
        return True
    else:
        return False

@mwdbg
def ck_param(goal_clause, db_clause):
    #get head from goal_clause if exist
    dbg_l(1,ml,["ck_param: goal_clause:",goal_clause," db_clause:",db_clause])
    var_list = []
    goal=goal_clause[0]
    
    if goal_clause[0].find(':-')>0: #条件literalが存在するなら
        dbg_l(0,ml,["条件あり",clause])
        head = get_head(clause) #head literal取得
        body = get_body(clause) #body literals取得
    else:
        head = clause
        body = ""
    dbg_l(1,ml,["head:",head," ?? g:",goal])

    #compare parameter of goal and head
    head_params = get_params(head)
    goal_params = get_params(goal)
    dbg_l(1,ml,["param check head_param:",head_params," / goal_params:",goal_params])
    for i in range(len(head_params)):
        dbg_l(1,ml,["head param:",head_params[i]," goal param:",goal_params[i]])
        if head_params[i] [0]=='*':
            body,goal = unify(head_params[i],goal_params[i],goal,body)
            continue
        elif goal_params[i][0]=='*':
            body,goal = unify(goal_params[i],head_params[i],goal,body)
            continue
        elif head_params[i] == goal_params[i]:
            continue
        elif head_params[i]!=goal_params[i]:
            return "False"
    return True, var_list

@mwdbg
def ck_param2(goal_clause, db_clause):
    #get head from goal_clause if exist
    dbg_l(1,ml,["ck_param: goal_clause:",goal_clause," db_clause:",db_clause])
    #key_list = []
    #var_list = []
    unify_dic = {}
    goal=goal_clause[0]
    head=db_clause[0]
    #compare parameter of goal and head
    head_params = get_params(head)
    goal_params = get_params(goal)
    body=db_clause[1:]
    dbg_l(2,ml,["param check head_param:",head_params," / goal_params:",goal_params])
    for i in range(len(head_params)):
        dbg_l(2,ml,["head param:",head_params[i]," / goal param:",goal_params[i]])
        if head_params[i][0]=='*':
            #key_list.append(head_params[i])
            #var_list.append(goal_params[i])
            #dbg_l(3,ml,["head_params[i]:",head_params[i]," / goal_params[i]:",goal_params[i]])
            #dbg_l(3,ml,["pre update unify_dic:",unify_dic])
            unify_dic.update(zip([head_params[i]], [goal_params[i]]))
            #dbg_l(3,ml,["unify_dic:",unify_dic])
            #goal,body = unify(head_params[i],goal_params[i],goal,body)
            continue
        elif goal_params[i][0]=='*':
            #dbg_l(3,ml,["head_params[i]:",head_params[i]," / goal_params[i]:",goal_params[i]])
            #dbg_l(3,ml,["pre update unify_dic:",unify_dic])
            unify_dic.update(zip([goal_params[i]], [head_params[i]]))
            #dbg_l(3,ml,["unify_dic:",unify_dic])
            #goal,body = unify(goal_params[i],head_params[i],goal,body)
            continue
        elif head_params[i] == goal_params[i]:
            continue
        elif head_params[i]!=goal_params[i]:
            return "False"
    return True, unify_dic


@mwdbg
def unify(hensu, atai, goal, body):
    dbg_l(2,ml,["unify: ",hensu, ",", atai, ",",body,",",goal])
    #dbg_l(2,ml,["body_type:",type(body)," goal_type:",type(goal)])
    if type(body) is list:
        body2=[]
        for literal in body:
            literal = literal.replace(hensu,atai)
            body2.append(literal)
        body = body2
    elif type(body) is str:
        body = body.replace(hensu,atai)
    else:
        print("Error : body is not list,str!")
    
    if type(goal) is list:
        goal2=[]
        for literal in goal:
            literal = literal.replace(hensu,atai)
            goal2.append(literal)
        goal = goal2
    elif type(goal) is str:
        goal = goal.replace(hensu,atai)
    else:
        print("Error : goal is not list,str!")
    
    return goal,body

def dbg_l(f,lvl, s):
    if f>=4:
        for i in range(lvl):
            print("  ",end="")
        print("+++",end="")
        for i in range(len(s)):
            print(s[i],end="")
            #print(" / ",end="")
        print("")

def dbg(f,s):
    if f==1:
        for i in range(len(s)):
            print(s[i],end="")
        print("")

def dbger(dl,idx,lcls, *vars):
    #https://note.nkmk.me/python-args-kwargs-usage/
    for i in range(dl):
        print(" ",end="")
    print(">>",end="")
    print(idx,end="")
    for var in vars:
        for lcl in lcls:
            if var==lcl:
                print(var,":",lcls[lcl],",  ",end="")
    #print("")
    #x = input('next')
    
def z_end():
    dbg(0,["end"])
                
if __name__ == '__main__':
    s = "f(a,b)."
    parser(s)
    s = "f(b,c)."
    parser(s)
    s = "g_f(*A,*C):-f(*A,*B),f(*B,*C)."
    parser(s)
    prt_db()
    s = "?-g_f(a,*x),prt(*x)."
    parser(s)
    
