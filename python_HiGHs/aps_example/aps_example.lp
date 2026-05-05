\ File written by HiGHS .lp file handler
min
 obj: +1 CMAX 
st
 PREC1: +1 X11 -1 X12 <= -3
 PREC2: -1 X21 +1 X22 <= -4
 MKSP1: -1 CMAX +1 X12 <= -2
 MKSP2: -1 CMAX +1 X21 <= -1
 DISJ1A: +100 Z121 +1 X11 -1 X21 <= +97
 DISJ1B: -100 Z121 -1 X11 +1 X21 <= -1
 DISJ2A: +100 Z122 +1 X12 -1 X22 <= +98
 DISJ2B: -100 Z122 -1 X12 +1 X22 <= -4
bounds
 Z121 <= 1
 Z122 <= 1
bin
 Z121
 Z122
gen
semi
end
