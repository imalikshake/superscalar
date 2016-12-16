ldc r10 c20
ldc r9 c20
ldc r11 c29

check :
addi r9 r9 c1
addi r13 r10 c0
cmp r12 r11 r9
blth r12 end

main :
cmp r14 r11 r13
be r14 check

ldr r0 r13
addi r4 r13 c1
ldr r1 r4
cmp r2 r0 r1
bgth r2 increment
j check

increment :
sto r13 r1
addi r13 r13 c1
sto r13 r0
j main

end :
ldc r14 11