def edit(t):
    a='%target.sroa.0 = alloca [7 x i8], align 1'
    assert t.count(a)==1
    return t.replace(a,'%target.sroa.0 = alloca [24 x i8], align 8')
