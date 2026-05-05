\ File written by HiGHS .lp file handler
min
 obj: +50 Y1 +50 Y2 +10 X1 +10 X2 +2 I1 +2 I2 
st
 INV1: -1 X1 +1 I1 = -5
 INV2: -1 X2 -1 I1 +1 I2 = -15
 SET1: -100 Y1 +1 X1 <= +0
 SET2: -100 Y2 +1 X2 <= +0
 CAP1: +1 X1 <= +20
 CAP2: +1 X2 <= +20
 SS1: +1 I1 >= +2
 SS2: +1 I2 >= +2
bounds
 Y1 <= 1
 Y2 <= 1
bin
 Y1
 Y2
gen
semi
end
