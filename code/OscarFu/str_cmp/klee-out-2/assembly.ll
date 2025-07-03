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
@.str.10 = private unnamed_addr constant [30 x i8] c"Comparing '%s' vs '%s' -> %d\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !11 {
entry:
  %retval = alloca i32, align 4
  %options = alloca [8 x i8*], align 16
  %idx_a = alloca i32, align 4
  %idx_b = alloca i32, align 4
  %a = alloca i8*, align 8
  %b = alloca i8*, align 8
  %result = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  call void @llvm.dbg.declare(metadata [8 x i8*]* %options, metadata !15, metadata !DIExpression()), !dbg !22
  %0 = bitcast [8 x i8*]* %options to i8*, !dbg !22
  %1 = call i8* @memcpy(i8* %0, i8* bitcast ([8 x i8*]* @__const.main.options to i8*), i64 64), !dbg !22
  call void @llvm.dbg.declare(metadata i32* %idx_a, metadata !23, metadata !DIExpression()), !dbg !24
  call void @llvm.dbg.declare(metadata i32* %idx_b, metadata !25, metadata !DIExpression()), !dbg !26
  %2 = bitcast i32* %idx_a to i8*, !dbg !27
  call void @klee_make_symbolic(i8* %2, i64 4, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.8, i64 0, i64 0)), !dbg !28
  %3 = bitcast i32* %idx_b to i8*, !dbg !29
  call void @klee_make_symbolic(i8* %3, i64 4, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.9, i64 0, i64 0)), !dbg !30
  %4 = load i32, i32* %idx_a, align 4, !dbg !31
  %cmp = icmp sge i32 %4, 0, !dbg !32
  %conv = zext i1 %cmp to i32, !dbg !32
  %conv1 = sext i32 %conv to i64, !dbg !31
  call void @klee_assume(i64 %conv1), !dbg !33
  %5 = load i32, i32* %idx_a, align 4, !dbg !34
  %cmp2 = icmp slt i32 %5, 8, !dbg !35
  %conv3 = zext i1 %cmp2 to i32, !dbg !35
  %conv4 = sext i32 %conv3 to i64, !dbg !34
  call void @klee_assume(i64 %conv4), !dbg !36
  %6 = load i32, i32* %idx_b, align 4, !dbg !37
  %cmp5 = icmp sge i32 %6, 0, !dbg !38
  %conv6 = zext i1 %cmp5 to i32, !dbg !38
  %conv7 = sext i32 %conv6 to i64, !dbg !37
  call void @klee_assume(i64 %conv7), !dbg !39
  %7 = load i32, i32* %idx_b, align 4, !dbg !40
  %cmp8 = icmp slt i32 %7, 8, !dbg !41
  %conv9 = zext i1 %cmp8 to i32, !dbg !41
  %conv10 = sext i32 %conv9 to i64, !dbg !40
  call void @klee_assume(i64 %conv10), !dbg !42
  call void @llvm.dbg.declare(metadata i8** %a, metadata !43, metadata !DIExpression()), !dbg !44
  %8 = load i32, i32* %idx_a, align 4, !dbg !45
  %idxprom = sext i32 %8 to i64, !dbg !46
  %arrayidx = getelementptr inbounds [8 x i8*], [8 x i8*]* %options, i64 0, i64 %idxprom, !dbg !46
  %9 = load i8*, i8** %arrayidx, align 8, !dbg !46
  store i8* %9, i8** %a, align 8, !dbg !44
  call void @llvm.dbg.declare(metadata i8** %b, metadata !47, metadata !DIExpression()), !dbg !48
  %10 = load i32, i32* %idx_b, align 4, !dbg !49
  %idxprom11 = sext i32 %10 to i64, !dbg !50
  %arrayidx12 = getelementptr inbounds [8 x i8*], [8 x i8*]* %options, i64 0, i64 %idxprom11, !dbg !50
  %11 = load i8*, i8** %arrayidx12, align 8, !dbg !50
  store i8* %11, i8** %b, align 8, !dbg !48
  call void @llvm.dbg.declare(metadata i32* %result, metadata !51, metadata !DIExpression()), !dbg !52
  %12 = load i8*, i8** %a, align 8, !dbg !53
  %13 = load i8*, i8** %b, align 8, !dbg !54
  %call = call i32 @strcmp(i8* %12, i8* %13) #6, !dbg !55
  store i32 %call, i32* %result, align 4, !dbg !52
  %14 = load i8*, i8** %a, align 8, !dbg !56
  %15 = load i8*, i8** %b, align 8, !dbg !57
  %16 = load i32, i32* %result, align 4, !dbg !58
  %call13 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([30 x i8], [30 x i8]* @.str.10, i64 0, i64 0), i8* %14, i8* %15, i32 %16), !dbg !59
  %17 = load i32, i32* %result, align 4, !dbg !60
  ret i32 %17, !dbg !61
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: argmemonly nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #2

declare dso_local void @klee_make_symbolic(i8*, i64, i8*) #3

declare dso_local void @klee_assume(i64) #3

; Function Attrs: nounwind readonly willreturn
declare dso_local i32 @strcmp(i8*, i8*) #4

declare dso_local i32 @printf(i8*, ...) #3

; Function Attrs: noinline nounwind uwtable
define dso_local i8* @memcpy(i8* %destaddr, i8* %srcaddr, i64 %len) #5 !dbg !62 {
entry:
  %destaddr.addr = alloca i8*, align 8
  %srcaddr.addr = alloca i8*, align 8
  %len.addr = alloca i64, align 8
  %dest = alloca i8*, align 8
  %src = alloca i8*, align 8
  store i8* %destaddr, i8** %destaddr.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %destaddr.addr, metadata !72, metadata !DIExpression()), !dbg !73
  store i8* %srcaddr, i8** %srcaddr.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %srcaddr.addr, metadata !74, metadata !DIExpression()), !dbg !75
  store i64 %len, i64* %len.addr, align 8
  call void @llvm.dbg.declare(metadata i64* %len.addr, metadata !76, metadata !DIExpression()), !dbg !77
  call void @llvm.dbg.declare(metadata i8** %dest, metadata !78, metadata !DIExpression()), !dbg !80
  %0 = load i8*, i8** %destaddr.addr, align 8, !dbg !81
  store i8* %0, i8** %dest, align 8, !dbg !80
  call void @llvm.dbg.declare(metadata i8** %src, metadata !82, metadata !DIExpression()), !dbg !83
  %1 = load i8*, i8** %srcaddr.addr, align 8, !dbg !84
  store i8* %1, i8** %src, align 8, !dbg !83
  br label %while.cond, !dbg !85

while.cond:                                       ; preds = %while.body, %entry
  %2 = load i64, i64* %len.addr, align 8, !dbg !86
  %dec = add i64 %2, -1, !dbg !86
  store i64 %dec, i64* %len.addr, align 8, !dbg !86
  %cmp = icmp ugt i64 %2, 0, !dbg !87
  br i1 %cmp, label %while.body, label %while.end, !dbg !85

while.body:                                       ; preds = %while.cond
  %3 = load i8*, i8** %src, align 8, !dbg !88
  %incdec.ptr = getelementptr inbounds i8, i8* %3, i32 1, !dbg !88
  store i8* %incdec.ptr, i8** %src, align 8, !dbg !88
  %4 = load i8, i8* %3, align 1, !dbg !89
  %5 = load i8*, i8** %dest, align 8, !dbg !90
  %incdec.ptr1 = getelementptr inbounds i8, i8* %5, i32 1, !dbg !90
  store i8* %incdec.ptr1, i8** %dest, align 8, !dbg !90
  store i8 %4, i8* %5, align 1, !dbg !91
  br label %while.cond, !dbg !85, !llvm.loop !92

while.end:                                        ; preds = %while.cond
  %6 = load i8*, i8** %destaddr.addr, align 8, !dbg !94
  ret i8* %6, !dbg !95
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { argmemonly nofree nounwind willreturn }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readonly willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nounwind readonly willreturn }

!llvm.dbg.cu = !{!0, !3}
!llvm.module.flags = !{!5, !6, !7, !8, !9}
!llvm.ident = !{!10, !10}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "strcmp_sample.c", directory: "/code/OscarFu")
!2 = !{}
!3 = distinct !DICompileUnit(language: DW_LANG_C99, file: !4, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!4 = !DIFile(filename: "/tmp/klee_src/runtime/Freestanding/memcpy.c", directory: "/tmp/klee_build130stp_z3/runtime/Freestanding")
!5 = !{i32 7, !"Dwarf Version", i32 4}
!6 = !{i32 2, !"Debug Info Version", i32 3}
!7 = !{i32 1, !"wchar_size", i32 4}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = !{i32 7, !"frame-pointer", i32 2}
!10 = !{!"clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)"}
!11 = distinct !DISubprogram(name: "main", scope: !1, file: !1, line: 5, type: !12, scopeLine: 5, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!12 = !DISubroutineType(types: !13)
!13 = !{!14}
!14 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!15 = !DILocalVariable(name: "options", scope: !11, file: !1, line: 6, type: !16)
!16 = !DICompositeType(tag: DW_TAG_array_type, baseType: !17, size: 512, elements: !20)
!17 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !18, size: 64)
!18 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !19)
!19 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!20 = !{!21}
!21 = !DISubrange(count: 8)
!22 = !DILocation(line: 6, column: 17, scope: !11)
!23 = !DILocalVariable(name: "idx_a", scope: !11, file: !1, line: 16, type: !14)
!24 = !DILocation(line: 16, column: 9, scope: !11)
!25 = !DILocalVariable(name: "idx_b", scope: !11, file: !1, line: 16, type: !14)
!26 = !DILocation(line: 16, column: 16, scope: !11)
!27 = !DILocation(line: 18, column: 24, scope: !11)
!28 = !DILocation(line: 18, column: 5, scope: !11)
!29 = !DILocation(line: 19, column: 24, scope: !11)
!30 = !DILocation(line: 19, column: 5, scope: !11)
!31 = !DILocation(line: 21, column: 17, scope: !11)
!32 = !DILocation(line: 21, column: 23, scope: !11)
!33 = !DILocation(line: 21, column: 5, scope: !11)
!34 = !DILocation(line: 22, column: 17, scope: !11)
!35 = !DILocation(line: 22, column: 23, scope: !11)
!36 = !DILocation(line: 22, column: 5, scope: !11)
!37 = !DILocation(line: 23, column: 17, scope: !11)
!38 = !DILocation(line: 23, column: 23, scope: !11)
!39 = !DILocation(line: 23, column: 5, scope: !11)
!40 = !DILocation(line: 24, column: 17, scope: !11)
!41 = !DILocation(line: 24, column: 23, scope: !11)
!42 = !DILocation(line: 24, column: 5, scope: !11)
!43 = !DILocalVariable(name: "a", scope: !11, file: !1, line: 26, type: !17)
!44 = !DILocation(line: 26, column: 17, scope: !11)
!45 = !DILocation(line: 26, column: 29, scope: !11)
!46 = !DILocation(line: 26, column: 21, scope: !11)
!47 = !DILocalVariable(name: "b", scope: !11, file: !1, line: 27, type: !17)
!48 = !DILocation(line: 27, column: 17, scope: !11)
!49 = !DILocation(line: 27, column: 29, scope: !11)
!50 = !DILocation(line: 27, column: 21, scope: !11)
!51 = !DILocalVariable(name: "result", scope: !11, file: !1, line: 29, type: !14)
!52 = !DILocation(line: 29, column: 9, scope: !11)
!53 = !DILocation(line: 29, column: 25, scope: !11)
!54 = !DILocation(line: 29, column: 28, scope: !11)
!55 = !DILocation(line: 29, column: 18, scope: !11)
!56 = !DILocation(line: 31, column: 46, scope: !11)
!57 = !DILocation(line: 31, column: 49, scope: !11)
!58 = !DILocation(line: 31, column: 52, scope: !11)
!59 = !DILocation(line: 31, column: 5, scope: !11)
!60 = !DILocation(line: 33, column: 12, scope: !11)
!61 = !DILocation(line: 33, column: 5, scope: !11)
!62 = distinct !DISubprogram(name: "memcpy", scope: !63, file: !63, line: 12, type: !64, scopeLine: 12, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !3, retainedNodes: !2)
!63 = !DIFile(filename: "klee_src/runtime/Freestanding/memcpy.c", directory: "/tmp")
!64 = !DISubroutineType(types: !65)
!65 = !{!66, !66, !67, !69}
!66 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!67 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !68, size: 64)
!68 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!69 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !70, line: 46, baseType: !71)
!70 = !DIFile(filename: "llvm-130-install_O_D_A/lib/clang/13.0.1/include/stddef.h", directory: "/tmp")
!71 = !DIBasicType(name: "long unsigned int", size: 64, encoding: DW_ATE_unsigned)
!72 = !DILocalVariable(name: "destaddr", arg: 1, scope: !62, file: !63, line: 12, type: !66)
!73 = !DILocation(line: 12, column: 20, scope: !62)
!74 = !DILocalVariable(name: "srcaddr", arg: 2, scope: !62, file: !63, line: 12, type: !67)
!75 = !DILocation(line: 12, column: 42, scope: !62)
!76 = !DILocalVariable(name: "len", arg: 3, scope: !62, file: !63, line: 12, type: !69)
!77 = !DILocation(line: 12, column: 58, scope: !62)
!78 = !DILocalVariable(name: "dest", scope: !62, file: !63, line: 13, type: !79)
!79 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!80 = !DILocation(line: 13, column: 9, scope: !62)
!81 = !DILocation(line: 13, column: 16, scope: !62)
!82 = !DILocalVariable(name: "src", scope: !62, file: !63, line: 14, type: !17)
!83 = !DILocation(line: 14, column: 15, scope: !62)
!84 = !DILocation(line: 14, column: 21, scope: !62)
!85 = !DILocation(line: 16, column: 3, scope: !62)
!86 = !DILocation(line: 16, column: 13, scope: !62)
!87 = !DILocation(line: 16, column: 16, scope: !62)
!88 = !DILocation(line: 17, column: 19, scope: !62)
!89 = !DILocation(line: 17, column: 15, scope: !62)
!90 = !DILocation(line: 17, column: 10, scope: !62)
!91 = !DILocation(line: 17, column: 13, scope: !62)
!92 = distinct !{!92, !85, !88, !93}
!93 = !{!"llvm.loop.mustprogress"}
!94 = !DILocation(line: 18, column: 10, scope: !62)
!95 = !DILocation(line: 18, column: 3, scope: !62)
