proc add # a => r1, b => r2 & return value => r0
add r4, r1, r2
mov r3, r4
mov r0, r3
ret
proc main # return value => r0
call iget, r3
mov r1, r3
call iget, r4
mov r2, r4
call add, r5, r1, r2
call iput, r5
mov r0, 0
ret