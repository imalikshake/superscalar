# Generates Fibinacci up to 9 (term in r3)
ldc r0 c1
ldc r1 c1

ldc r3 c2
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
sys r
sys m 0 10