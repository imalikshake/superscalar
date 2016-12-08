# r1 holds the GCD of the numbers in r0 and r1
ldc r0 c206
ldc r1 c40
ldc r2 c206
ldc r3 c206

modulo :
sub r3 r3 r1
blth r3 gcd
j modulo

gcd :
add r2 r3 r1
be r2 end

addi r0 r1 c0
addi r3 r1 c0
addi r1 r2 c0

j modulo

end :
sys r