# x5 (three 24-B target tails) + a fourth, short-lived 24-B execute-local tail copy %t24 at the join
# (target.sroa.8 -> t24 -> target1), allocated right after %target.sroa.8 (frame position near holder_key)
import runpy, os
x5 = runpy.run_path(os.path.join(os.path.dirname(__file__), 'x5.py'))['edit']
def edit(t):
    t = x5(t)
    a = '%target.sroa.8 = alloca [24 x i8], align 8'
    assert t.count(a) == 1
    t = t.replace(a, a + '\n  %t24 = alloca [24 x i8], align 8')
    m = ('call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 1 dereferenceable(9) %target.sroa.8.0.target1.sroa_idx, '
         'ptr noundef nonnull align 1 dereferenceable(9) %target.sroa.8, i64 9, i1 false)')
    assert t.count(m) == 1
    new = ('call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %t24)\n'
           '  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(9) %t24, ptr noundef nonnull align 1 dereferenceable(9) %target.sroa.8, i64 9, i1 false)\n'
           '  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 1 dereferenceable(9) %target.sroa.8.0.target1.sroa_idx, ptr noundef nonnull align 8 dereferenceable(9) %t24, i64 9, i1 false)\n'
           '  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %t24)')
    return t.replace(m, new)
