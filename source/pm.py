
# PERFORMANCE MEASURES

import sys
import os

# open 1v file for Rotoiti Levels

f = open(os.path.join(sys.argv[1],'RotoitiLevel.txt'))
var1 = f.read()
val = []
a = 0

# parse the file to array "val"

while a < 3652:
	val.append(float(var1[(73+20*a):(80+20*a)]))
	a += 1

f.close

# iti_lev is the sorted array of Levels

iti_lev = val
iti_lev.sort()
iti_lev.reverse()

# write the sorted array
"""
g = open('c:\data.txt', 'w')
a = 0
while a < 3652:
       g.write(str(iti_lev[a]))
       g.write('\n')
       a += 1
g.close
"""
# open 1v file for Rotorua Levels

f = open(os.path.join(sys.argv[1],'RotoruaLevel.txt'))
var1 = f.read()
val = []
a = 0

# parse the file to array "val"

while a < 3652:
	val.append(float(var1[(73+20*a):(80+20*a)]))
	a += 1

f.close

# rua_lev is the sorted array of Levels

rua_lev = val

rua_lev.sort()
rua_lev.reverse()

# write the sorted array
"""
g = open('c:\data2.txt', 'w')
a = 0
while a < 3652:
       g.write(str(rua_lev[a]))
       g.write('\n')
       a += 1
g.close
"""
# open 1v file for Okere outflow

f = open(os.path.join(sys.argv[1],'OkereOutflow.txt'))
var1 = f.read()
val = []
a = 0

# parse the file to array "val"

while a < 3652:
	val.append(float(var1[(75+20*a):(80+20*a)]))
	a += 1

f.close

# okr_out is the sorted array of outflow

okr_out = val

okr_out.sort()
okr_out.reverse()

# write the sorted array
"""
g = open('c:\data3.txt', 'w')
a = 0
while a < 3652:
       g.write(str(okr_out[a]))
       g.write('\n')
       a += 1
g.close
"""
# Figures 5,6,7,8 Level catagories

c5 = 0.0
c6 = 0.0
c7 = 0.0
c8 = 0.0

i = 0
while i < 3652:
	if iti_lev[i] < 279.191:
		c6 = c6 + 1
	if iti_lev[i] < 279.406:
		c5 = c5 + 1
	if iti_lev[i] >= 279.041:
		c7 = c7 + 1
		if iti_lev[i] <= 279.191:
			c8 = c8 + 1
	i += 1

c5 = c5 / 3652 * 100
c6 = c6 / 3652 * 100
c7 = c7 / 3652 * 100
c8 = c8 / 3652 * 100

# Figure 11, 12, 13  Flows

c11 = 0.0
c12 = 0.0
c13 = 0.0

i = 0
while i < 3652:
	if okr_out[i] <= 40:
		c11 = c11 + 1
	if okr_out[i] >= 7.9:
		c13 = c13 + 1
	if okr_out[i] <= 26:
		if okr_out[i] >= 13.6:
			c12 = c12 + 1
	i += 1

c11 = c11 / 3652 * 100
c12 = c12 / 3652 * 100
c13 = c13 / 3652 * 100

PMscore = c5 + c6 + c7 + c8 + c11 + c12 + c13

g = open(os.path.join(sys.argv[1], "GA_Scoring.txt"), 'w')
g.write(str(c5))
g.write('\n')
g.write(str(c6))
g.write('\n')
g.write(str(c7))
g.write('\n')
g.write(str(c8))
g.write('\n')
g.write(str(c11))
g.write('\n')
g.write(str(c12))
g.write('\n')
g.write(str(c13))
g.write('\n')
g.write('\n')
g.write('TOTAL ' + str(PMscore))
g.close



