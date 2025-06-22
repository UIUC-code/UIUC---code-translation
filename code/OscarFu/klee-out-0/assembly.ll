; ModuleID = 'strcmp_sample.bc'
source_filename = "strcmp_sample.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@.str = private unnamed_addr constant [2 x i8] c"a\00", align 1
@.str.1 = private unnamed_addr constant [2 x i8] c"b\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !9 {
entry:
  %retval = alloca i32, align 4
  %a = alloca [8 x i8], align 1
  %b = alloca [8 x i8], align 1
  %i = alloca i32, align 4
  %result = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  call void @llvm.dbg.declare(metadata [8 x i8]* %a, metadata !13, metadata !DIExpression()), !dbg !18
  call void @llvm.dbg.declare(metadata [8 x i8]* %b, metadata !19, metadata !DIExpression()), !dbg !20
  %arraydecay = getelementptr inbounds [8 x i8], [8 x i8]* %a, i64 0, i64 0, !dbg !21
  call void @klee_make_symbolic(i8* %arraydecay, i64 8, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @.str, i64 0, i64 0)), !dbg !22
  %arraydecay1 = getelementptr inbounds [8 x i8], [8 x i8]* %b, i64 0, i64 0, !dbg !23
  call void @klee_make_symbolic(i8* %arraydecay1, i64 8, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @.str.1, i64 0, i64 0)), !dbg !24
  %arrayidx = getelementptr inbounds [8 x i8], [8 x i8]* %a, i64 0, i64 7, !dbg !25
  store i8 0, i8* %arrayidx, align 1, !dbg !26
  %arrayidx2 = getelementptr inbounds [8 x i8], [8 x i8]* %b, i64 0, i64 7, !dbg !27
  store i8 0, i8* %arrayidx2, align 1, !dbg !28
  call void @llvm.dbg.declare(metadata i32* %i, metadata !29, metadata !DIExpression()), !dbg !31
  store i32 0, i32* %i, align 4, !dbg !31
  br label %for.cond, !dbg !32

for.cond:                                         ; preds = %for.inc, %entry
  %0 = load i32, i32* %i, align 4, !dbg !33
  %cmp = icmp slt i32 %0, 7, !dbg !35
  br i1 %cmp, label %for.body, label %for.end, !dbg !36

for.body:                                         ; preds = %for.cond
  %1 = load i32, i32* %i, align 4, !dbg !37
  %idxprom = sext i32 %1 to i64, !dbg !39
  %arrayidx3 = getelementptr inbounds [8 x i8], [8 x i8]* %a, i64 0, i64 %idxprom, !dbg !39
  %2 = load i8, i8* %arrayidx3, align 1, !dbg !39
  %conv = sext i8 %2 to i32, !dbg !39
  %cmp4 = icmp sge i32 %conv, 32, !dbg !40
  %conv5 = zext i1 %cmp4 to i32, !dbg !40
  %conv6 = sext i32 %conv5 to i64, !dbg !39
  call void @klee_assume(i64 %conv6), !dbg !41
  %3 = load i32, i32* %i, align 4, !dbg !42
  %idxprom7 = sext i32 %3 to i64, !dbg !43
  %arrayidx8 = getelementptr inbounds [8 x i8], [8 x i8]* %a, i64 0, i64 %idxprom7, !dbg !43
  %4 = load i8, i8* %arrayidx8, align 1, !dbg !43
  %conv9 = sext i8 %4 to i32, !dbg !43
  %cmp10 = icmp sle i32 %conv9, 126, !dbg !44
  %conv11 = zext i1 %cmp10 to i32, !dbg !44
  %conv12 = sext i32 %conv11 to i64, !dbg !43
  call void @klee_assume(i64 %conv12), !dbg !45
  %5 = load i32, i32* %i, align 4, !dbg !46
  %idxprom13 = sext i32 %5 to i64, !dbg !47
  %arrayidx14 = getelementptr inbounds [8 x i8], [8 x i8]* %b, i64 0, i64 %idxprom13, !dbg !47
  %6 = load i8, i8* %arrayidx14, align 1, !dbg !47
  %conv15 = sext i8 %6 to i32, !dbg !47
  %cmp16 = icmp sge i32 %conv15, 32, !dbg !48
  %conv17 = zext i1 %cmp16 to i32, !dbg !48
  %conv18 = sext i32 %conv17 to i64, !dbg !47
  call void @klee_assume(i64 %conv18), !dbg !49
  %7 = load i32, i32* %i, align 4, !dbg !50
  %idxprom19 = sext i32 %7 to i64, !dbg !51
  %arrayidx20 = getelementptr inbounds [8 x i8], [8 x i8]* %b, i64 0, i64 %idxprom19, !dbg !51
  %8 = load i8, i8* %arrayidx20, align 1, !dbg !51
  %conv21 = sext i8 %8 to i32, !dbg !51
  %cmp22 = icmp sle i32 %conv21, 126, !dbg !52
  %conv23 = zext i1 %cmp22 to i32, !dbg !52
  %conv24 = sext i32 %conv23 to i64, !dbg !51
  call void @klee_assume(i64 %conv24), !dbg !53
  br label %for.inc, !dbg !54

for.inc:                                          ; preds = %for.body
  %9 = load i32, i32* %i, align 4, !dbg !55
  %inc = add nsw i32 %9, 1, !dbg !55
  store i32 %inc, i32* %i, align 4, !dbg !55
  br label %for.cond, !dbg !56, !llvm.loop !57

for.end:                                          ; preds = %for.cond
  call void @llvm.dbg.declare(metadata i32* %result, metadata !60, metadata !DIExpression()), !dbg !61
  %arraydecay25 = getelementptr inbounds [8 x i8], [8 x i8]* %a, i64 0, i64 0, !dbg !62
  %arraydecay26 = getelementptr inbounds [8 x i8], [8 x i8]* %b, i64 0, i64 0, !dbg !63
  %call = call i32 @strcmp(i8* %arraydecay25, i8* %arraydecay26) #4, !dbg !64
  store i32 %call, i32* %result, align 4, !dbg !61
  ret i32 0, !dbg !65
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare dso_local void @klee_make_symbolic(i8*, i64, i8*) #2

declare dso_local void @klee_assume(i64) #2

; Function Attrs: nounwind readonly willreturn
declare dso_local i32 @strcmp(i8*, i8*) #3

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind readonly willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readonly willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!3, !4, !5, !6, !7}
!llvm.ident = !{!8}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "strcmp_sample.c", directory: "/code/OscarFu")
!2 = !{}
!3 = !{i32 7, !"Dwarf Version", i32 4}
!4 = !{i32 2, !"Debug Info Version", i32 3}
!5 = !{i32 1, !"wchar_size", i32 4}
!6 = !{i32 7, !"uwtable", i32 1}
!7 = !{i32 7, !"frame-pointer", i32 2}
!8 = !{!"clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)"}
!9 = distinct !DISubprogram(name: "main", scope: !1, file: !1, line: 4, type: !10, scopeLine: 4, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!10 = !DISubroutineType(types: !11)
!11 = !{!12}
!12 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!13 = !DILocalVariable(name: "a", scope: !9, file: !1, line: 5, type: !14)
!14 = !DICompositeType(tag: DW_TAG_array_type, baseType: !15, size: 64, elements: !16)
!15 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!16 = !{!17}
!17 = !DISubrange(count: 8)
!18 = !DILocation(line: 5, column: 10, scope: !9)
!19 = !DILocalVariable(name: "b", scope: !9, file: !1, line: 5, type: !14)
!20 = !DILocation(line: 5, column: 16, scope: !9)
!21 = !DILocation(line: 6, column: 24, scope: !9)
!22 = !DILocation(line: 6, column: 5, scope: !9)
!23 = !DILocation(line: 7, column: 24, scope: !9)
!24 = !DILocation(line: 7, column: 5, scope: !9)
!25 = !DILocation(line: 8, column: 5, scope: !9)
!26 = !DILocation(line: 8, column: 10, scope: !9)
!27 = !DILocation(line: 9, column: 5, scope: !9)
!28 = !DILocation(line: 9, column: 10, scope: !9)
!29 = !DILocalVariable(name: "i", scope: !30, file: !1, line: 12, type: !12)
!30 = distinct !DILexicalBlock(scope: !9, file: !1, line: 12, column: 5)
!31 = !DILocation(line: 12, column: 14, scope: !30)
!32 = !DILocation(line: 12, column: 10, scope: !30)
!33 = !DILocation(line: 12, column: 21, scope: !34)
!34 = distinct !DILexicalBlock(scope: !30, file: !1, line: 12, column: 5)
!35 = !DILocation(line: 12, column: 23, scope: !34)
!36 = !DILocation(line: 12, column: 5, scope: !30)
!37 = !DILocation(line: 13, column: 23, scope: !38)
!38 = distinct !DILexicalBlock(scope: !34, file: !1, line: 12, column: 33)
!39 = !DILocation(line: 13, column: 21, scope: !38)
!40 = !DILocation(line: 13, column: 26, scope: !38)
!41 = !DILocation(line: 13, column: 9, scope: !38)
!42 = !DILocation(line: 14, column: 23, scope: !38)
!43 = !DILocation(line: 14, column: 21, scope: !38)
!44 = !DILocation(line: 14, column: 26, scope: !38)
!45 = !DILocation(line: 14, column: 9, scope: !38)
!46 = !DILocation(line: 15, column: 23, scope: !38)
!47 = !DILocation(line: 15, column: 21, scope: !38)
!48 = !DILocation(line: 15, column: 26, scope: !38)
!49 = !DILocation(line: 15, column: 9, scope: !38)
!50 = !DILocation(line: 16, column: 23, scope: !38)
!51 = !DILocation(line: 16, column: 21, scope: !38)
!52 = !DILocation(line: 16, column: 26, scope: !38)
!53 = !DILocation(line: 16, column: 9, scope: !38)
!54 = !DILocation(line: 17, column: 5, scope: !38)
!55 = !DILocation(line: 12, column: 29, scope: !34)
!56 = !DILocation(line: 12, column: 5, scope: !34)
!57 = distinct !{!57, !36, !58, !59}
!58 = !DILocation(line: 17, column: 5, scope: !30)
!59 = !{!"llvm.loop.mustprogress"}
!60 = !DILocalVariable(name: "result", scope: !9, file: !1, line: 19, type: !12)
!61 = !DILocation(line: 19, column: 9, scope: !9)
!62 = !DILocation(line: 19, column: 25, scope: !9)
!63 = !DILocation(line: 19, column: 28, scope: !9)
!64 = !DILocation(line: 19, column: 18, scope: !9)
!65 = !DILocation(line: 20, column: 5, scope: !9)
