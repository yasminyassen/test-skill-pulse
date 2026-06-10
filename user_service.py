def p(a,b,c,d,e,f,g,h,i,j,k,l,m,n):
    if a==1:
        if b>c:
            if d!=None:
                if e=='X' or e=='Y' or e=='Z':
                    if f>=18:
                        if g!='':
                            if h==1 or h==2 or h==3:
                                if i%2==0:
                                    r=b*0.97
                                    if j=='vip':r=r*0.90
                                    if k>5:r=r-50
                                    if l=='EGP':r=r*49.5
                                    elif l=='SAR':r=r*3.75
                                    x=0
                                    for q in m:
                                        x=x+q[2]*q[3]
                                    if n:x=x*1.14
                                    return r,x,r+x
                                else:return None
                            else:return -3
                        else:return -2
                    else:return -1
                else:return 0
            else:return 0
        else:return 0
    elif a==2:
        # copy-paste من فوق بس بدون الـ tax
        if b>c:
            if d!=None:
                if e=='X' or e=='Y':
                    r=b*0.97
                    if j=='vip':r=r*0.90
                    return r
        return 0
    elif a==3:
        # refund — نفس الحسابات تالت مرة
        if b>c:
            r=b*0.97
            if l=='EGP':r=r*49.5
            return r*(-1)
        return 0
