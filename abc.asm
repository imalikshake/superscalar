check :
ldc r0 c10
ldc r10 c20
addi r13 r10 c0
addi r4 r13 c1
ldr r1 r4
cmp r2 r0 r1
bgth r2 increment
j check

increment :
ldc r3 c9