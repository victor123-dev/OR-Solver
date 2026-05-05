NAME        APS_Example
OBJSENSE
  MIN
ROWS
 N  OBJ
 L  PREC1
 L  PREC2
 L  MKSP1
 L  MKSP2
 L  DISJ1A
 L  DISJ1B
 L  DISJ2A
 L  DISJ2B
COLUMNS
    MARK0000  'MARKER'                 'INTORG'
    Z121      DISJ1A    100.0
    Z121      DISJ1B    -100.0
    Z122      DISJ2A    100.0
    Z122      DISJ2B    -100.0
    MARK0001  'MARKER'                 'INTEND'
    CMAX      OBJ       1.0
    CMAX      MKSP1     -1.0
    CMAX      MKSP2     -1.0
    X11       PREC1     1.0
    X11       DISJ1A    1.0
    X11       DISJ1B    -1.0
    X12       PREC1     -1.0
    X12       MKSP1     1.0
    X12       DISJ2A    1.0
    X12       DISJ2B    -1.0
    X21       PREC2     -1.0
    X21       MKSP2     1.0
    X21       DISJ1A    -1.0
    X21       DISJ1B    1.0
    X22       PREC2     1.0
    X22       DISJ2A    -1.0
    X22       DISJ2B    1.0
RHS
    RHS1      PREC1     -3.0
    RHS1      PREC2     -4.0
    RHS1      MKSP1     -2.0
    RHS1      MKSP2     -1.0
    RHS1      DISJ1A    97.0
    RHS1      DISJ1B    -1.0
    RHS1      DISJ2A    98.0
    RHS1      DISJ2B    -4.0
BOUNDS
 BV BND1      Z121
 BV BND1      Z122
ENDATA
