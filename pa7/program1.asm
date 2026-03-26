; Program 1
.section .text

MV fp, sp
JR func_main
HALT

func_main:
SW fp, 0(sp)
MV fp, sp
ADDI sp, sp, -4

GETI t0
LA t1, 0x20000000
SW t2, 0(t1)

GETI t3
LA t4, 0x20000004
SW t5, 0(t4)

BLE t0, t3, else1
LA t6, 0x10000208
PUTS t6
J finish

else1:
BEQ t0, t3, else2
LA t6, 0x10000000
PUTS t6
J finish

else2:
LA t6, 0x10000104
PUTS t6

finish:
ADDI sp, sp, 4
MV sp, fp
LW fp, 0(fp)
RET

.section .strings
0x10000000 "a is less than b\n"
0x10000104 "a is equal to b\n"
0x10000208 "a is greater than b\n"