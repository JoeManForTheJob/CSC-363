; Program 2

.section .text

MV fp, sp
JR func_main
HALT

func_main:
SW fp, 0(sp)
MV fp, sp
ADDI sp, sp, -4

ADDI sp, sp, -4
ADDI sp, sp, -4
ADDI sp, sp, -4
ADDI sp, sp, -4
ADDI sp, sp, -4

LI t1, 0
SW t1, -4(fp)

LI t2, 0
SW t2, -4(fp)

LI t11, 3
SW t11, -4(fp)

LI t12, 1
SW t12, -4(fp)

LI t7, 2
SW t7, -4(fp)

val_loop:
LA t5, 0x10000000
PUTS t5

GETI t3
LA t4, 0x20000000
SW t3, 0(t4)
BLE t3, t1, val_loop


collatz:

PUTI t3

check:
DIV t8, t3, t7
MUL t9, t8, t7
SUB t10, t3, t9

BEQ t10, t1, even

odd:
MUL t3, t3, t11
ADD t3, t3, t12
ADD t2, t2, t12

even:
DIV t3, t3, t7
ADD t2, t2, t12

BNE t3, t12, collatz

finish:

PUTI t2
PUTI t3

ADDI sp, sp, 4
ADDI sp, sp, 4
ADDI sp, sp, 4
ADDI sp, sp, 4
ADDI sp, sp, 4

ADDI sp, sp, 4
MV sp, fp
LW fp, 0(fp)
RET

.section .strings
0x10000000 "Please give a positive integer: \n"
