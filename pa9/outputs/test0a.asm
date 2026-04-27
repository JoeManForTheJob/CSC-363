; Symbol table GLOBAL
; name true type STRING location 0x10000000 value "True\n"
; name false type STRING location 0x10000004 value "False\n"
; name a type INT location 0x20000000
; name b type INT location 0x20000004

.section .text
;Current temp: null
;IR Code: 
LA t2, 0x20000000
LI t1, 2
SW t1, 0(t2)
LA t4, 0x20000004
LI t3, 3
SW t3, 0(t4)
LA t5, 0x20000000
LW t6, 0(t5)
LA t7, 0x20000004
LW t8, 0(t7)
BGE t6, t8, out_1
LA t9, 0x10000000
PUTS t9
out_1:
LI t10, 0
HALT


.section .strings
0x10000000 "True\n"
0x10000004 "False\n"