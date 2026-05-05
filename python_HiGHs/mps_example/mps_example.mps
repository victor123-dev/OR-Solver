NAME        MPS_Example
OBJSENSE
  MIN
ROWS
 N  OBJ
 E  INV1
 E  INV2
 L  SET1
 L  SET2
 L  CAP1
 L  CAP2
 G  SS1
 G  SS2
COLUMNS
    MARK0000  'MARKER'                 'INTORG'
    Y1        OBJ       50.0
    Y1        SET1      -100.0
    Y2        OBJ       50.0
    Y2        SET2      -100.0
    MARK0001  'MARKER'                 'INTEND'
    X1        OBJ       10.0
    X1        INV1      -1.0
    X1        SET1      1.0
    X1        CAP1      1.0
    X2        OBJ       10.0
    X2        INV2      -1.0
    X2        SET2      1.0
    X2        CAP2      1.0
    I1        OBJ       2.0
    I1        INV1      1.0
    I1        INV2      -1.0
    I1        SS1       1.0
    I2        OBJ       2.0
    I2        INV2      1.0
    I2        SS2       1.0
RHS
    RHS1      INV1      -5.0
    RHS1      INV2      -15.0
    RHS1      CAP1      20.0
    RHS1      CAP2      20.0
    RHS1      SS1       2.0
    RHS1      SS2       2.0
BOUNDS
 BV BND1      Y1
 BV BND1      Y2
ENDATA
