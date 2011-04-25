# Check the last line of uniques.out to see if the population dump completed.
for line in open("uniques.out", "r"): pass
if "Done" not in line return

lines = (line.split(";") for line in open("uniques.out", "r"))

current_pop = True

for line in lines:
	
	# Check to see if it is time to begin adding individuals to the culled population
	if "Culled" in line[0]: # then
		current_pop = False