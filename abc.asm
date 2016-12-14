ldc r3 c7

modulo :
subi r3 r3 c1
subi r3 r3 c1
subi r3 r3 c1
subi r3 r3 c1
blth r3 modulo
j gcd

gcd :
ldc r4 c1
