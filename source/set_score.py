"""
	This script must:
		Find the score for the run and place it in final_score.txt.
		final_score.txt format:
			score: <SCORE>

	sys.argv[1] is the run directory which is where the onevar output should go.

	During onevar execution, errors are supressed so output checks must 
	be performed IN THIS CODE to make sure that the onevar execution 
	was a success. If it failed then set the score to the specified 
	error score.
	
	sys.argv[2] is the score to assign on error
"""
import os
import sys
import subprocess
import utils

#
# Get the score.  This is where some pretty non-generic stuff should go.
#
score = None

proc = subprocess.Popen(['python pm.py', sys.argv[1]], shell=True)
proc.wait()

# 1) Grab the last value from the 'TOTAL' line.  
#

# try to parse the file containing the score--it might not be there at all.
try:
	# Reverse the line order so we hit the 'TOTAL' line quickly.
	onevar_output = utils.Lines_In_File(os.path.join(sys.argv[1], "GA_Scoring.txt"))
	onevar_output.reverse()
		
	for line in onevar_output:
		if "TOTAL" in line:
			line = line.split()
			score = float(line[-1])
			#
			# INCOMPLETE - Fix the pop::Select() code to handle negative scores...
			# then remove this statement:
			score = max(score, 0)
except IOError:
	pass

# Set the score to the error-score if the score is not set by the time 
# we've finished parsing the 1v output in GA_Scoring.txt 
if score == None:
	score = float(sys.argv[2])
	
# 2) Now, write the score to an output file
#

out_path = os.path.join(sys.argv[1], "final_score.txt")

out_file = open(out_path, "w")
out_file.writelines("score: " + str(score))
out_file.close()