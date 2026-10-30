def edit(t):
    for a,b in [('%target.i.sroa.9 = alloca [9 x i8], align 1','%target.i.sroa.9 = alloca [24 x i8], align 8'),
                ('%_37.sroa.11 = alloca [16 x i8], align 8','%_37.sroa.11 = alloca [24 x i8], align 8'),
                ('%target.sroa.8 = alloca [9 x i8], align 1','%target.sroa.8 = alloca [24 x i8], align 8')]:
        assert t.count(a)==1, a
        t=t.replace(a,b)
    return t
