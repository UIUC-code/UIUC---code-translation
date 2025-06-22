; ModuleID = 'c_runner.c'
source_filename = "c_runner.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque

@stderr = external dso_local global %struct._IO_FILE*, align 8
@.str = private unnamed_addr constant [27 x i8] c"Usage: %s string1 string2\0A\00", align 1
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @my_strcmp(i8* %a, i8* %b) #0 !dbg !9 {
entry:
  %a.addr = alloca i8*, align 8
  %b.addr = alloca i8*, align 8
  store i8* %a, i8** %a.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %a.addr, metadata !16, metadata !DIExpression()), !dbg !17
  store i8* %b, i8** %b.addr, align 8
  call void @llvm.dbg.declare(metadata i8** %b.addr, metadata !18, metadata !DIExpression()), !dbg !19
  %0 = load i8*, i8** %a.addr, align 8, !dbg !20
  %1 = load i8*, i8** %b.addr, align 8, !dbg !21
  %call = call i32 @strcmp(i8* %0, i8* %1) #4, !dbg !22
  ret i32 %call, !dbg !23
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: nounwind readonly willreturn
declare dso_local i32 @strcmp(i8*, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main(i32 %argc, i8** %argv) #0 !dbg !24 {
entry:
  %retval = alloca i32, align 4
  %argc.addr = alloca i32, align 4
  %argv.addr = alloca i8**, align 8
  %a = alloca i8*, align 8
  %b = alloca i8*, align 8
  %result = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  store i32 %argc, i32* %argc.addr, align 4
  call void @llvm.dbg.declare(metadata i32* %argc.addr, metadata !29, metadata !DIExpression()), !dbg !30
  store i8** %argv, i8*** %argv.addr, align 8
  call void @llvm.dbg.declare(metadata i8*** %argv.addr, metadata !31, metadata !DIExpression()), !dbg !32
  %0 = load i32, i32* %argc.addr, align 4, !dbg !33
  %cmp = icmp slt i32 %0, 3, !dbg !35
  br i1 %cmp, label %if.then, label %if.end, !dbg !36

if.then:                                          ; preds = %entry
  %1 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !dbg !37
  %2 = load i8**, i8*** %argv.addr, align 8, !dbg !39
  %arrayidx = getelementptr inbounds i8*, i8** %2, i64 0, !dbg !39
  %3 = load i8*, i8** %arrayidx, align 8, !dbg !39
  %call = call i32 (%struct._IO_FILE*, i8*, ...) @fprintf(%struct._IO_FILE* %1, i8* getelementptr inbounds ([27 x i8], [27 x i8]* @.str, i64 0, i64 0), i8* %3), !dbg !40
  store i32 1, i32* %retval, align 4, !dbg !41
  br label %return, !dbg !41

if.end:                                           ; preds = %entry
  call void @llvm.dbg.declare(metadata i8** %a, metadata !42, metadata !DIExpression()), !dbg !43
  %4 = load i8**, i8*** %argv.addr, align 8, !dbg !44
  %arrayidx1 = getelementptr inbounds i8*, i8** %4, i64 1, !dbg !44
  %5 = load i8*, i8** %arrayidx1, align 8, !dbg !44
  store i8* %5, i8** %a, align 8, !dbg !43
  call void @llvm.dbg.declare(metadata i8** %b, metadata !45, metadata !DIExpression()), !dbg !46
  %6 = load i8**, i8*** %argv.addr, align 8, !dbg !47
  %arrayidx2 = getelementptr inbounds i8*, i8** %6, i64 2, !dbg !47
  %7 = load i8*, i8** %arrayidx2, align 8, !dbg !47
  store i8* %7, i8** %b, align 8, !dbg !46
  call void @llvm.dbg.declare(metadata i32* %result, metadata !48, metadata !DIExpression()), !dbg !49
  %8 = load i8*, i8** %a, align 8, !dbg !50
  %9 = load i8*, i8** %b, align 8, !dbg !51
  %call3 = call i32 @my_strcmp(i8* %8, i8* %9), !dbg !52
  store i32 %call3, i32* %result, align 4, !dbg !49
  %10 = load i32, i32* %result, align 4, !dbg !53
  %call4 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.1, i64 0, i64 0), i32 %10), !dbg !54
  store i32 0, i32* %retval, align 4, !dbg !55
  br label %return, !dbg !55

return:                                           ; preds = %if.end, %if.then
  %11 = load i32, i32* %retval, align 4, !dbg !56
  ret i32 %11, !dbg !56
}

declare dso_local i32 @fprintf(%struct._IO_FILE*, i8*, ...) #3

declare dso_local i32 @printf(i8*, ...) #3

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind readonly willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readonly willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!3, !4, !5, !6, !7}
!llvm.ident = !{!8}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "c_runner.c", directory: "/code/OscarFu")
!2 = !{}
!3 = !{i32 7, !"Dwarf Version", i32 4}
!4 = !{i32 2, !"Debug Info Version", i32 3}
!5 = !{i32 1, !"wchar_size", i32 4}
!6 = !{i32 7, !"uwtable", i32 1}
!7 = !{i32 7, !"frame-pointer", i32 2}
!8 = !{!"clang version 13.0.1 (https://github.com/llvm/llvm-project.git 75e33f71c2dae584b13a7d1186ae0a038ba98838)"}
!9 = distinct !DISubprogram(name: "my_strcmp", scope: !1, file: !1, line: 4, type: !10, scopeLine: 4, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!10 = !DISubroutineType(types: !11)
!11 = !{!12, !13, !13}
!12 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!13 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !14, size: 64)
!14 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !15)
!15 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!16 = !DILocalVariable(name: "a", arg: 1, scope: !9, file: !1, line: 4, type: !13)
!17 = !DILocation(line: 4, column: 27, scope: !9)
!18 = !DILocalVariable(name: "b", arg: 2, scope: !9, file: !1, line: 4, type: !13)
!19 = !DILocation(line: 4, column: 42, scope: !9)
!20 = !DILocation(line: 5, column: 19, scope: !9)
!21 = !DILocation(line: 5, column: 22, scope: !9)
!22 = !DILocation(line: 5, column: 12, scope: !9)
!23 = !DILocation(line: 5, column: 5, scope: !9)
!24 = distinct !DISubprogram(name: "main", scope: !1, file: !1, line: 8, type: !25, scopeLine: 8, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!25 = !DISubroutineType(types: !26)
!26 = !{!12, !12, !27}
!27 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !28, size: 64)
!28 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !15, size: 64)
!29 = !DILocalVariable(name: "argc", arg: 1, scope: !24, file: !1, line: 8, type: !12)
!30 = !DILocation(line: 8, column: 14, scope: !24)
!31 = !DILocalVariable(name: "argv", arg: 2, scope: !24, file: !1, line: 8, type: !27)
!32 = !DILocation(line: 8, column: 27, scope: !24)
!33 = !DILocation(line: 9, column: 9, scope: !34)
!34 = distinct !DILexicalBlock(scope: !24, file: !1, line: 9, column: 9)
!35 = !DILocation(line: 9, column: 14, scope: !34)
!36 = !DILocation(line: 9, column: 9, scope: !24)
!37 = !DILocation(line: 10, column: 17, scope: !38)
!38 = distinct !DILexicalBlock(scope: !34, file: !1, line: 9, column: 19)
!39 = !DILocation(line: 10, column: 56, scope: !38)
!40 = !DILocation(line: 10, column: 9, scope: !38)
!41 = !DILocation(line: 11, column: 9, scope: !38)
!42 = !DILocalVariable(name: "a", scope: !24, file: !1, line: 13, type: !13)
!43 = !DILocation(line: 13, column: 17, scope: !24)
!44 = !DILocation(line: 13, column: 21, scope: !24)
!45 = !DILocalVariable(name: "b", scope: !24, file: !1, line: 14, type: !13)
!46 = !DILocation(line: 14, column: 17, scope: !24)
!47 = !DILocation(line: 14, column: 21, scope: !24)
!48 = !DILocalVariable(name: "result", scope: !24, file: !1, line: 16, type: !12)
!49 = !DILocation(line: 16, column: 9, scope: !24)
!50 = !DILocation(line: 16, column: 28, scope: !24)
!51 = !DILocation(line: 16, column: 31, scope: !24)
!52 = !DILocation(line: 16, column: 18, scope: !24)
!53 = !DILocation(line: 17, column: 20, scope: !24)
!54 = !DILocation(line: 17, column: 5, scope: !24)
!55 = !DILocation(line: 19, column: 5, scope: !24)
!56 = !DILocation(line: 20, column: 1, scope: !24)
