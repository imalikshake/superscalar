# Generates Fibinacci up to n (n is stored in r3 and the nth fib number is in r1)
ldc r3 c20


ldc r0 c1
ldc r1 c1

ldc r2 c0

sto r2 r0
addi r2 r2 c1
sto r2 r1
addi r2 r2 c1

label :
cmp r4 r3 r2
be r4 label2

add r0 r0 r1
add r1 r0 r1

sto r2 r0
addi r2 r2 c1

cmp r4 r3 r2
be r4 label2

sto r2 r1
addi r2 r2 c1
j label

label2 :
ldc r5 c0