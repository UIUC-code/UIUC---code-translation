; ModuleID = 'strcmp_sample.bc'
source_filename = "strcmp_sample.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@.str = private unnamed_addr constant [6 x i8] c"hello\00", align 1
@.str.1 = private unnamed_addr constant [6 x i8] c"world\00", align 1
@.str.2 = private unnamed_addr constant [20 x i8] c"today is a good day\00", align 1
@.str.3 = private unnamed_addr constant [29 x i8] c"openAI creates amazing tools\00", align 1
@.str.4 = private unnamed_addr constant [21 x i8] c"klee helps find bugs\00", align 1
@.str.5 = private unnamed_addr constant [25 x i8] c"symbolic execution rocks\00", align 1
@.str.6 = private unnamed_addr constant [22 x i8] c"rust is safe and fast\00", align 1
@.str.7 = private unnamed_addr constant [21 x i8] c"testing is important\00", align 1
@__const.main.options = private unnamed_addr constant [8 x i8*] [i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str, i32 0, i32 0), i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i32 0, i32 0), i8* getelementptr inbounds ([20 x i8], [20 x i8]* @.str.2, i32 0, i32 0), i8* getelementptr inbounds ([29 x i8], [29 x i8]* @.str.3, i32 0, i32 0), i8* getelementptr inbounds ([21 x i8], [21 x i8]* @.str.4, i32 0, i32 0), i8* getelementptr inbounds ([25 x i8], [25 x i8]* @.str.5, i32 0, i32 0), i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.6, i32 0, i32 0), i8* getelementptr inbounds ([21 x i8], [21 x i8]* @.str.7, i32 0, i32 0)], align 16
@.str.8 = private unnamed_addr constant [6 x i8] c"idx_a\00", align 1
@.str.9 = private unnamed_addr constant [6 x i8] c"idx_b\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @my_strcmp(i8* %a, i8* %b) #0 !dbg !13 {
entry:
  %a.addr = alloca i8*, align 8
  %b.addr = alloca i8*, align 8
  store i8* %a, i8** %a.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %a.addr, metadata !20, metadata !DIExpression()), !dbg !21
  store i8* %b, i8** %b.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %b.addr, metadata !22, metadata !DIExpression()), !dbg !23
  br label %while.cond, !dbg !24

while.cond:                                       ; preds = %while.body, %entry
  %0 = load i8*, i8** %a.addr, align 8, !dbg !25
  %1 = load i8, i8* %0, align 1, !dbg !26
  %conv = sext i8 %1 to i32, !dbg !26
  %tobool = icmp ne i32 %conv, 0, !dbg !26
  br i1 %tobool, label %land.rhs, label %land.end, !dbg !27

land.rhs:                                         ; preds = %while.cond
  %2 = load i8*, i8** %a.addr, align 8, !dbg !28
  %3 = load i8, i8* %2, align 1, !dbg !29
  %conv1 = sext i8 %3 to i32, !dbg !29
  %4 = load i8*, i8** %b.addr, align 8, !dbg !30
  %5 = load i8, i8* %4, align 1, !dbg !31
  %conv2 = sext i8 %5 to i32, !dbg !31
  %cmp = icmp eq i32 %conv1, %conv2, !dbg !32
  br label %land.end

land.end:                                         ; preds = %land.rhs, %while.cond
  %6 = phi i1 [ false, %while.cond ], [ %cmp, %land.rhs ], !dbg !33
  br i1 %6, label %while.body, label %while.end, !dbg !24

while.body:                                       ; preds = %land.end
  %7 = load i8*, i8** %a.addr, align 8, !dbg !34
  %incdec.ptr = getelementptr inbounds i8, i8* %7, i32 1, !dbg !34
  store i8* %incdec.ptr, i8** %a.addr, align 8, !dbg !34
  %8 = load i8*, i8** %b.addr, align 8, !dbg !36
  %incdec.ptr4 = getelementptr inbounds i8, i8* %8, i32 1, !dbg !36
  store i8* %incdec.ptr4, i8** %b.addr, align 8, !dbg !36
  br label %while.cond, !dbg !24, !llvm.loop !37

while.end:                                        ; preds = %land.end
  %9 = load i8*, i8** %a.addr, align 8, !dbg !40
  %10 = load i8, i8* %9, align 1, !dbg !41
  %conv5 = zext i8 %10 to i32, !dbg !42
  %11 = load i8*, i8** %b.addr, align 8, !dbg !43
  %12 = load i8, i8* %11, align 1, !dbg !44
  %conv6 = zext i8 %12 to i32, !dbg !45
  %sub = sub nsw i32 %conv5, %conv6, !dbg !46
  ret i32 %sub, !dbg !47
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !48 {
entry:
  %retval = alloca i32, align 4
  %options = alloca [8 x i8*], align 16
  %idx_a = alloca i32, align 4
  %idx_b = alloca i32, align 4
  %a = alloca i8*, align 8
  %b = alloca i8*, align 8
  %result = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  call void @llvm.dbg.declare(metadata [8 x i8*]* %options, metadata !51, metadata !DIExpression()), !dbg !55
  %0 = bitcast [8 x i8*]* %options to i8*, !dbg !55
  %1 = call i8* @memcpy(i8* %0, i8* bitcast ([8 x i8*]* @__const.main.options to i8*), i64 64), !dbg !55
  call void @llvm.dbg.declare(metadata i32* %idx_a, metadata !56, metadata !DIExpression()), !dbg !57
  call void @llvm.dbg.declare(metadata i32* %idx_b, metadata !58, metadata !DIExpression()), !dbg !59
  %2 = bitcast i32* %idx_a to i8*, !dbg !60
  call void @klee_make_symbolic(i8* %2, i64 4, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.8, i64 0, i64 0)), !dbg !61
  %3 = bitcast i32* %idx_b to i8*, !dbg !62
  call void @klee_make_symbolic(i8* %3, i64 4, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.9, i64 0, i64 0)), !dbg !63
  %4 = load i32, i32* %idx_a, align 4, !dbg !64
  %cmp = icmp sge i32 %4, 0, !dbg !65
  %conv = zext i1 %cmp to i32, !dbg !65
  %conv1 = sext i32 %conv to i64, !dbg !64
  call void @klee_assume(i64 %conv1), !dbg !66
  %5 = load i32, i32* %idx_a, align 4, !dbg !67
  %cmp2 = icmp slt i32 %5, 8, !dbg !68
  %conv3 = zext i1 %cmp2 to i32, !dbg !68
  %conv4 = sext i32 %conv3 to i64, !dbg !67
  call void @klee_assume(i64 %conv4), !dbg !69
  %6 = load i32, i32* %idx_b, align 4, !dbg !70
  %cmp5 = icmp sge i32 %6, 0, !dbg !71
  %conv6 = zext i1 %cmp5 to i32, !dbg !71
  %conv7 = sext i32 %conv6 to i64, !dbg !70
  call void @klee_assume(i64 %conv7), !dbg !72
  %7 = load i32, i32* %idx_b, align 4, !dbg !73
  %cmp8 = icmp slt i32 %7, 8, !dbg !74
  %conv9 = zext i1 %cmp8 to i32, !dbg !74
  %conv10 = sext i32 %conv9 to i64, !dbg !73
  call void @klee_assume(i64 %conv10), !dbg !75
  call void @llvm.dbg.declare(metadata i8** %a, metadata !76, metadata !DIExpression()), !dbg !77
  %8 = load i32, i32* %idx_a, align 4, !dbg !78
  %idxprom = sext i32 %8 to i64, !dbg !79
  %arrayidx = getelementptr inbounds [8 x i8*], [8 x i8*]* %options, i64 0, i64 %idxprom, !dbg !79
  %9 = load i8*, i8** %arrayidx, align 8, !dbg !79
  store i8* %9, i8** %a, align 8, !dbg !77
  call void @llvm.dbg.declare(metadata i8** %b, metadata !80, metadata !DIExpression()), !dbg !81
  %10 = load i32, i32* %idx_b, align 4, !dbg !82
  %idxprom11 = sext i32 %10 to i64, !dbg !83
  %arrayidx12 = getelementptr inbounds [8 x i8*], [8 x i8*]* %options, i64 0, i64 %idxprom11, !dbg !83
  %11 = load i8*, i8** %arrayidx12, align 8, !dbg !83
  store i8* %11, i8** %b, align 8, !dbg !81
  call void @llvm.dbg.declare(metadata i32* %result, metadata !84, metadata !DIExpression()), !dbg !85
  %12 = load i8*, i8** %a, align 8, !dbg !86
  %13 = load i8*, i8** %b, align 8, !dbg !87
  %call = call i32 @my_strcmp(i8* %12, i8* %13), !dbg !88
  store i32 %call, i32* %result, align 4, !dbg !85
  %14 = load i32, i32* %result, align 4, !dbg !89
  ret i32 %14, !dbg !90
}

; Function Attrs: argmemonly nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #2

declare dso_local void @klee_make_symbolic(i8*, i64, i8*) #3

declare dso_local void @klee_assume(i64) #3

; Function Attrs: noinline nounwind uwtable
define dso_local i8* @memcpy(i8* %destaddr, i8* %srcaddr, i64 %len) #4 !dbg !91 {
entry:
  %destaddr.addr = alloca i8*, align 8
  %srcaddr.addr = alloca i8*, align 8
  %len.addr = alloca i64, align 8
  %dest = alloca i8*, align 8
  %src = alloca i8*, align 8
  store i8* %destaddr, i8** %destaddr.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %destaddr.addr, metadata !101, metadata !DIExpression()), !dbg !102
  store i8* %srcaddr, i8** %srcaddr.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %srcaddr.addr, metadata !103, metadata !DIExpression()), !dbg !104
  store i64 %len, i64* %len.addr, align 8
  call void @llvm.dbg.declare(metadata i64* %len.addr, metadata !105, metadata !DIExpression()), !dbg !106
  call void @llvm.dbg.declare(metadata i8** %dest, metadata !107, metadata !DIExpression()), !dbg !109
  %0 = load i8*, i8** %destaddr.addr, align 8, !dbg !110
  store i8* %0, i8** %dest, align 8, !dbg !109
  call void @llvm.dbg.declare(metadata i8** %src, metadata !111, metadata !DIExpression()), !dbg !112
  %1 = load i8*, i8** %srcaddr.addr, align 8, !dbg !113
  store i8* %1, i8** %src, align 8, !dbg !112
  br label %while.cond, !dbg !114

while.cond:                                       ; preds = %while.body, %entry
  %2 = load i64, i64* %len.addr, align 8, !dbg !115
  %dec = add i64 %2, -1, !dbg !115
  store i64 %dec, i64* %len.addr, align 8, !dbg !115
  %cmp = icmp ugt i64 %2, 0, !dbg !116
  br i1 %cmp, label %while.body, label %while.end, !dbg !114

while.body:                                       ; preds = %while.cond
  %3 = load i8*, i8** %src, align 8, !dbg !117
  %incdec.ptr = getelementptr inbounds i8, i8* %3, i32 1, !dbg !117
  store i8* %incdec.ptr, i8** %src, align 8, !dbg !117
  %4 = load i8, i8* %3, align 1, !dbg !118
  %5 = load i8*, i8** %dest, align 8, !dbg !119
  %incdec.ptr1 = getelementptr inbounds i8, i8* %5, i32 1, !dbg !119
  store i8* %incdec.ptr1, i8** %dest, align 8, !dbg !119
  store i8 %4, i8* %5, align 1, !dbg !120
  br label %while.cond, !dbg !114, !llvm.loop !121

while.end:                                        ; preds = %while.cond
  %6 = load i8*, i8** %destaddr.addr, align 8, !dbg !122
  ret i8* %6, !dbg !123
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { argmemonly nofree nounwind willreturn }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0, !5}
!llvm.module.flags = !{!7, !8, !9, !10, !11}
!llvm.ident = !{!12, !12}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, retainedTypes: !3, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "strcmp_sample.c", directory: "/code/OscarFu")
!2 = !{}
!3 = !{!4}
!4 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!5 = distinct !DICompileUnit(language: DW_LANG_C99, file: !6, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!6 = !DIFile(filename: "/tmp/klee_src/runtime/Freestanding/memcpy.c", directory: "/tmp/klee_build130stp_z3/runtime/Freestanding")
!7 = !{i32 7, !"Dwarf Version", i32 4}
!8 = !{i32 2, !"Debug Info Version", i32 3}
!9 = !{i32 1, !"wchar_size", i32 4}
!10 = !{i32 7, !"uwtable", i32 1}
!11 = !{i32 7, !"frame-pointer", i32 2}
!12 = !{!"clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)"}
!13 = distinct !DISubprogram(name: "my_strcmp", scope: !1, file: !1, line: 3, type: !14, scopeLine: 3, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!14 = !DISubroutineType(types: !15)
!15 = !{!16, !17, !17}
!16 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!17 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !18, size: 64)
!18 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !19)
!19 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!20 = !DILocalVariable(name: "a", arg: 1, scope: !13, file: !1, line: 3, type: !17)
!21 = !DILocation(line: 3, column: 27, scope: !13)
!22 = !DILocalVariable(name: "b", arg: 2, scope: !13, file: !1, line: 3, type: !17)
!23 = !DILocation(line: 3, column: 42, scope: !13)
!24 = !DILocation(line: 4, column: 5, scope: !13)
!25 = !DILocation(line: 4, column: 13, scope: !13)
!26 = !DILocation(line: 4, column: 12, scope: !13)
!27 = !DILocation(line: 4, column: 15, scope: !13)
!28 = !DILocation(line: 4, column: 20, scope: !13)
!29 = !DILocation(line: 4, column: 19, scope: !13)
!30 = !DILocation(line: 4, column: 26, scope: !13)
!31 = !DILocation(line: 4, column: 25, scope: !13)
!32 = !DILocation(line: 4, column: 22, scope: !13)
!33 = !DILocation(line: 0, scope: !13)
!34 = !DILocation(line: 5, column: 10, scope: !35)
!35 = distinct !DILexicalBlock(scope: !13, file: !1, line: 4, column: 30)
!36 = !DILocation(line: 6, column: 10, scope: !35)
!37 = distinct !{!37, !24, !38, !39}
!38 = !DILocation(line: 7, column: 5, scope: !13)
!39 = !{!"llvm.loop.mustprogress"}
!40 = !DILocation(line: 8, column: 28, scope: !13)
!41 = !DILocation(line: 8, column: 27, scope: !13)
!42 = !DILocation(line: 8, column: 12, scope: !13)
!43 = !DILocation(line: 8, column: 48, scope: !13)
!44 = !DILocation(line: 8, column: 47, scope: !13)
!45 = !DILocation(line: 8, column: 32, scope: !13)
!46 = !DILocation(line: 8, column: 30, scope: !13)
!47 = !DILocation(line: 8, column: 5, scope: !13)
!48 = distinct !DISubprogram(name: "main", scope: !1, file: !1, line: 11, type: !49, scopeLine: 11, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!49 = !DISubroutineType(types: !50)
!50 = !{!16}
!51 = !DILocalVariable(name: "options", scope: !48, file: !1, line: 12, type: !52)
!52 = !DICompositeType(tag: DW_TAG_array_type, baseType: !17, size: 512, elements: !53)
!53 = !{!54}
!54 = !DISubrange(count: 8)
!55 = !DILocation(line: 12, column: 17, scope: !48)
!56 = !DILocalVariable(name: "idx_a", scope: !48, file: !1, line: 22, type: !16)
!57 = !DILocation(line: 22, column: 9, scope: !48)
!58 = !DILocalVariable(name: "idx_b", scope: !48, file: !1, line: 22, type: !16)
!59 = !DILocation(line: 22, column: 16, scope: !48)
!60 = !DILocation(line: 24, column: 24, scope: !48)
!61 = !DILocation(line: 24, column: 5, scope: !48)
!62 = !DILocation(line: 25, column: 24, scope: !48)
!63 = !DILocation(line: 25, column: 5, scope: !48)
!64 = !DILocation(line: 27, column: 17, scope: !48)
!65 = !DILocation(line: 27, column: 23, scope: !48)
!66 = !DILocation(line: 27, column: 5, scope: !48)
!67 = !DILocation(line: 28, column: 17, scope: !48)
!68 = !DILocation(line: 28, column: 23, scope: !48)
!69 = !DILocation(line: 28, column: 5, scope: !48)
!70 = !DILocation(line: 29, column: 17, scope: !48)
!71 = !DILocation(line: 29, column: 23, scope: !48)
!72 = !DILocation(line: 29, column: 5, scope: !48)
!73 = !DILocation(line: 30, column: 17, scope: !48)
!74 = !DILocation(line: 30, column: 23, scope: !48)
!75 = !DILocation(line: 30, column: 5, scope: !48)
!76 = !DILocalVariable(name: "a", scope: !48, file: !1, line: 32, type: !17)
!77 = !DILocation(line: 32, column: 17, scope: !48)
!78 = !DILocation(line: 32, column: 29, scope: !48)
!79 = !DILocation(line: 32, column: 21, scope: !48)
!80 = !DILocalVariable(name: "b", scope: !48, file: !1, line: 33, type: !17)
!81 = !DILocation(line: 33, column: 17, scope: !48)
!82 = !DILocation(line: 33, column: 29, scope: !48)
!83 = !DILocation(line: 33, column: 21, scope: !48)
!84 = !DILocalVariable(name: "result", scope: !48, file: !1, line: 35, type: !16)
!85 = !DILocation(line: 35, column: 9, scope: !48)
!86 = !DILocation(line: 35, column: 28, scope: !48)
!87 = !DILocation(line: 35, column: 31, scope: !48)
!88 = !DILocation(line: 35, column: 18, scope: !48)
!89 = !DILocation(line: 37, column: 12, scope: !48)
!90 = !DILocation(line: 37, column: 5, scope: !48)
!91 = distinct !DISubprogram(name: "memcpy", scope: !92, file: !92, line: 12, type: !93, scopeLine: 12, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !5, retainedNodes: !2)
!92 = !DIFile(filename: "klee_src/runtime/Freestanding/memcpy.c", directory: "/tmp")
!93 = !DISubroutineType(types: !94)
!94 = !{!95, !95, !96, !98}
!95 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!96 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !97, size: 64)
!97 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!98 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !99, line: 46, baseType: !100)
!99 = !DIFile(filename: "llvm-130-install_O_D_A/lib/clang/13.0.1/include/stddef.h", directory: "/tmp")
!100 = !DIBasicType(name: "long unsigned int", size: 64, encoding: DW_ATE_unsigned)
!101 = !DILocalVariable(name: "destaddr", arg: 1, scope: !91, file: !92, line: 12, type: !95)
!102 = !DILocation(line: 12, column: 20, scope: !91)
!103 = !DILocalVariable(name: "srcaddr", arg: 2, scope: !91, file: !92, line: 12, type: !96)
!104 = !DILocation(line: 12, column: 42, scope: !91)
!105 = !DILocalVariable(name: "len", arg: 3, scope: !91, file: !92, line: 12, type: !98)
!106 = !DILocation(line: 12, column: 58, scope: !91)
!107 = !DILocalVariable(name: "dest", scope: !91, file: !92, line: 13, type: !108)
!108 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!109 = !DILocation(line: 13, column: 9, scope: !91)
!110 = !DILocation(line: 13, column: 16, scope: !91)
!111 = !DILocalVariable(name: "src", scope: !91, file: !92, line: 14, type: !17)
!112 = !DILocation(line: 14, column: 15, scope: !91)
!113 = !DILocation(line: 14, column: 21, scope: !91)
!114 = !DILocation(line: 16, column: 3, scope: !91)
!115 = !DILocation(line: 16, column: 13, scope: !91)
!116 = !DILocation(line: 16, column: 16, scope: !91)
!117 = !DILocation(line: 17, column: 19, scope: !91)
!118 = !DILocation(line: 17, column: 15, scope: !91)
!119 = !DILocation(line: 17, column: 10, scope: !91)
!120 = !DILocation(line: 17, column: 13, scope: !91)
!121 = distinct !{!121, !114, !117, !39}
!122 = !DILocation(line: 18, column: 10, scope: !91)
!123 = !DILocation(line: 18, column: 3, scope: !91)
