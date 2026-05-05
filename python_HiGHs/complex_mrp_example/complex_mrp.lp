\ File written by HiGHS .lp file handler
min
 obj: +80 Y_C1_1 +80 Y_C1_2 +80 Y_C1_3 +80 Y_C1_4 +60 Y_C2_1 +60 Y_C2_2 +60 Y_C2_3 +60 Y_C2_4 +70 Y_C3_1 +70 Y_C3_2 +70 Y_C3_3 +70 Y_C3_4 +200 Y_FG1_1 +200 Y_FG1_2 +200 Y_FG1_3 +200 Y_FG1_4 +180 Y_FG2_1 +180 Y_FG2_2 +180 Y_FG2_3 +180 Y_FG2_4 +80 BO_FG1_1 +80 BO_FG1_2 +80 BO_FG1_3 +80 BO_FG1_4 +70 BO_FG2_1 +70 BO_FG2_2 +70 BO_FG2_3 +70 BO_FG2_4 +3 I_C1_1 +3 I_C1_2 +3 I_C1_3 +3 I_C1_4 +2 I_C2_1 +2 I_C2_2 +2 I_C2_3 +2 I_C2_4 +2.5 I_C3_1 +2.5 I_C3_2 +2.5 I_C3_3 +2.5 I_C3_4 +10 I_FG1_1 +10 I_FG1_2 +10 I_FG1_3 +10 I_FG1_4 +8 I_FG2_1 +8 I_FG2_2 +8 I_FG2_3 +8
 I_FG2_4 +15 X_C1_1 +15 X_C1_2 +15 X_C1_3 +15 X_C1_4 +10 X_C2_1 +10 X_C2_2 +10 X_C2_3 +10 X_C2_4 +12 X_C3_1 +12 X_C3_2 +12 X_C3_3 +12 X_C3_4 +50 X_FG1_1 +50 X_FG1_2 +50 X_FG1_3 +50 X_FG1_4 +45 X_FG2_1 +45 X_FG2_2 +45 X_FG2_3 +45 X_FG2_4 
st
 INV_FG1_1: -1 BO_FG1_1 +1 I_FG1_1 -1 X_FG1_1 = +10
 INV_FG1_2: +1 BO_FG1_1 -1 BO_FG1_2 -1 I_FG1_1 +1 I_FG1_2 -1 X_FG1_2 = -30
 INV_FG1_3: +1 BO_FG1_2 -1 BO_FG1_3 -1 I_FG1_2 +1 I_FG1_3 -1 X_FG1_3 = -40
 INV_FG1_4: +1 BO_FG1_3 -1 BO_FG1_4 -1 I_FG1_3 +1 I_FG1_4 -1 X_FG1_4 = -20
 INV_FG2_1: -1 BO_FG2_1 +1 I_FG2_1 -1 X_FG2_1 = +5
 INV_FG2_2: +1 BO_FG2_1 -1 BO_FG2_2 -1 I_FG2_1 +1 I_FG2_2 -1 X_FG2_2 = -20
 INV_FG2_3: +1 BO_FG2_2 -1 BO_FG2_3 -1 I_FG2_2 +1 I_FG2_3 -1 X_FG2_3 = -25
 INV_FG2_4: +1 BO_FG2_3 -1 BO_FG2_4 -1 I_FG2_3 +1 I_FG2_4 -1 X_FG2_4 = -15
 INV_C1_1: +1 I_C1_1 -1 X_C1_1 +2 X_FG1_1 +1 X_FG2_1 = +20
 INV_C1_2: -1 I_C1_1 +1 I_C1_2 -1 X_C1_2 +2 X_FG1_2 +1 X_FG2_2 = +0
 INV_C1_3: -1 I_C1_2 +1 I_C1_3 -1 X_C1_3 +2 X_FG1_3 +1 X_FG2_3 = +0
 INV_C1_4: -1 I_C1_3 +1 I_C1_4 -1 X_C1_4 +2 X_FG1_4 +1 X_FG2_4 = +0
 INV_C2_1: +1 I_C2_1 -1 X_C2_1 +1 X_FG1_1 = +15
 INV_C2_2: -1 I_C2_1 +1 I_C2_2 -1 X_C2_2 +1 X_FG1_2 = +0
 INV_C2_3: -1 I_C2_2 +1 I_C2_3 -1 X_C2_3 +1 X_FG1_3 = +0
 INV_C2_4: -1 I_C2_3 +1 I_C2_4 -1 X_C2_4 +1 X_FG1_4 = +0
 INV_C3_1: +1 I_C3_1 -1 X_C3_1 +2 X_FG2_1 = +8
 INV_C3_2: -1 I_C3_1 +1 I_C3_2 -1 X_C3_2 +2 X_FG2_2 = +0
 INV_C3_3: -1 I_C3_2 +1 I_C3_3 -1 X_C3_3 +2 X_FG2_3 = +0
 INV_C3_4: -1 I_C3_3 +1 I_C3_4 -1 X_C3_4 +2 X_FG2_4 = +0
 SET_FG1_1: -60 Y_FG1_1 +1 X_FG1_1 <= +0
 SET_FG1_2: -60 Y_FG1_2 +1 X_FG1_2 <= +0
 SET_FG1_3: -60 Y_FG1_3 +1 X_FG1_3 <= +0
 SET_FG1_4: -60 Y_FG1_4 +1 X_FG1_4 <= +0
 SET_FG2_1: -50 Y_FG2_1 +1 X_FG2_1 <= +0
 SET_FG2_2: -50 Y_FG2_2 +1 X_FG2_2 <= +0
 SET_FG2_3: -50 Y_FG2_3 +1 X_FG2_3 <= +0
 SET_FG2_4: -50 Y_FG2_4 +1 X_FG2_4 <= +0
 SET_C1_1: -120 Y_C1_1 +1 X_C1_1 <= +0
 SET_C1_2: -120 Y_C1_2 +1 X_C1_2 <= +0
 SET_C1_3: -120 Y_C1_3 +1 X_C1_3 <= +0
 SET_C1_4: -120 Y_C1_4 +1 X_C1_4 <= +0
 SET_C2_1: -80 Y_C2_1 +1 X_C2_1 <= +0
 SET_C2_2: -80 Y_C2_2 +1 X_C2_2 <= +0
 SET_C2_3: -80 Y_C2_3 +1 X_C2_3 <= +0
 SET_C2_4: -80 Y_C2_4 +1 X_C2_4 <= +0
 SET_C3_1: -80 Y_C3_1 +1 X_C3_1 <= +0
 SET_C3_2: -80 Y_C3_2 +1 X_C3_2 <= +0
 SET_C3_3: -80 Y_C3_3 +1 X_C3_3 <= +0
 SET_C3_4: -80 Y_C3_4 +1 X_C3_4 <= +0
 CAP_R1_1: +5 Y_C1_1 +15 Y_FG1_1 +12 Y_FG2_1 +0.5 X_C1_1 +2 X_FG1_1 +1.5 X_FG2_1 <= +80
 CAP_R1_2: +5 Y_C1_2 +15 Y_FG1_2 +12 Y_FG2_2 +0.5 X_C1_2 +2 X_FG1_2 +1.5 X_FG2_2 <= +80
 CAP_R1_3: +5 Y_C1_3 +15 Y_FG1_3 +12 Y_FG2_3 +0.5 X_C1_3 +2 X_FG1_3 +1.5 X_FG2_3 <= +80
 CAP_R1_4: +5 Y_C1_4 +15 Y_FG1_4 +12 Y_FG2_4 +0.5 X_C1_4 +2 X_FG1_4 +1.5 X_FG2_4 <= +80
 CAP_R2_1: +10 Y_C1_1 +8 Y_C2_1 +6 Y_C3_1 +5 Y_FG1_1 +8 Y_FG2_1 +1 X_C1_1 +0.8 X_C2_1 +0.6 X_C3_1 +0.5 X_FG1_1 +0.8 X_FG2_1 <= +120
 CAP_R2_2: +10 Y_C1_2 +8 Y_C2_2 +6 Y_C3_2 +5 Y_FG1_2 +8 Y_FG2_2 +1 X_C1_2 +0.8 X_C2_2 +0.6 X_C3_2 +0.5 X_FG1_2 +0.8 X_FG2_2 <= +120
 CAP_R2_3: +10 Y_C1_3 +8 Y_C2_3 +6 Y_C3_3 +5 Y_FG1_3 +8 Y_FG2_3 +1 X_C1_3 +0.8 X_C2_3 +0.6 X_C3_3 +0.5 X_FG1_3 +0.8 X_FG2_3 <= +120
 CAP_R2_4: +10 Y_C1_4 +8 Y_C2_4 +6 Y_C3_4 +5 Y_FG1_4 +8 Y_FG2_4 +1 X_C1_4 +0.8 X_C2_4 +0.6 X_C3_4 +0.5 X_FG1_4 +0.8 X_FG2_4 <= +120
 SS_FG1_1: +1 I_FG1_1 >= +5
 SS_FG1_2: +1 I_FG1_2 >= +5
 SS_FG1_3: +1 I_FG1_3 >= +5
 SS_FG1_4: +1 I_FG1_4 >= +5
 SS_FG2_1: +1 I_FG2_1 >= +5
 SS_FG2_2: +1 I_FG2_2 >= +5
 SS_FG2_3: +1 I_FG2_3 >= +5
 SS_FG2_4: +1 I_FG2_4 >= +5
 SS_C1_1: +1 I_C1_1 >= +10
 SS_C1_2: +1 I_C1_2 >= +10
 SS_C1_3: +1 I_C1_3 >= +10
 SS_C1_4: +1 I_C1_4 >= +10
 SS_C2_1: +1 I_C2_1 >= +8
 SS_C2_2: +1 I_C2_2 >= +8
 SS_C2_3: +1 I_C2_3 >= +8
 SS_C2_4: +1 I_C2_4 >= +8
 SS_C3_1: +1 I_C3_1 >= +6
 SS_C3_2: +1 I_C3_2 >= +6
 SS_C3_3: +1 I_C3_3 >= +6
 SS_C3_4: +1 I_C3_4 >= +6
bounds
 Y_C1_1 <= 1
 Y_C1_2 <= 1
 Y_C1_3 <= 1
 Y_C1_4 <= 1
 Y_C2_1 <= 1
 Y_C2_2 <= 1
 Y_C2_3 <= 1
 Y_C2_4 <= 1
 Y_C3_1 <= 1
 Y_C3_2 <= 1
 Y_C3_3 <= 1
 Y_C3_4 <= 1
 Y_FG1_1 <= 1
 Y_FG1_2 <= 1
 Y_FG1_3 <= 1
 Y_FG1_4 <= 1
 Y_FG2_1 <= 1
 Y_FG2_2 <= 1
 Y_FG2_3 <= 1
 Y_FG2_4 <= 1
bin
 Y_C1_1
 Y_C1_2
 Y_C1_3
 Y_C1_4
 Y_C2_1
 Y_C2_2
 Y_C2_3
 Y_C2_4
 Y_C3_1
 Y_C3_2
 Y_C3_3
 Y_C3_4
 Y_FG1_1
 Y_FG1_2
 Y_FG1_3
 Y_FG1_4
 Y_FG2_1
 Y_FG2_2
 Y_FG2_3
 Y_FG2_4
gen
semi
end
