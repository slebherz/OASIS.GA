"""
***
	Utility and Misc functions:
***
"""
import copy
import random
import os
import xlrd # for excel reading/writing

import settings
import individual as ind
import chromosome as chro

# Excel cell object types (see xlrd module docs for more info)
EMPTY = 0
STRING = 1
ERROR = 5

"""
	Clear the console
"""
def Clear_Console():
	os.system(['clear','cls'][os.name == 'nt'])

"""
	Update the console
"""
def Update_Console():
	Clear_Console()
	print "\n" * 2
	print "--------------------------------------"
	print "\n" * 2
	print "Evaluated " + str(settings.num_evals) + " of " + str(int(settings.Get_Setting("max_evals"))) + "\n\n"
	print "\n"
	print "--------------------------------------"
	
"""
	Return all of the lines in a file.  Returns an empty list if
	there is an IOError.
"""
def Lines_In_File(filename):
	try:
		file = open(filename, "r")
	except IOError:
		return []
	return file.readlines()

#
# INCOMPLETE - REMOVE THIS AND USE RANDOM.UNIFORM(LOWER, UPPER) INSTEAD!!!
#
def Rand_In_Range(lower, upper):
	if upper == lower:
		return upper
	return ((random.random()*100) % (upper - lower)) + lower
	
"""
	Calculate the average fitness of a list of individuals
"""
def Calc_Avg_Fitness(individuals):
	sum = 0
	for individual in individuals:
		sum = sum + individual.raw_fitness
	return sum / len(individuals)

"""
	Pair up a list of individuals.
	Does not destroy the original list.
"""
def Build_Pairs(individuals):
	# Shuffle a copy of the list of individuals
	members = copy.deepcopy(individuals)
	random.seed()
	random.shuffle(members)
	
	pair = []
	pairs = []
	# Build pairs until the list is empty or has a lone member left.
	while len(members) > 1:
		pair.append(members.pop())
		pair.append(members.pop())
		pairs.append(copy.deepcopy(pair))
		del pair[:]
	return pairs

"""
	Generate a list of random indices in a specified range.
	Usually, num_indices will be user defined and the upper
	bound will be the number of chromosomes.
"""
def Generate_Random_Indices(num_indices, upper_bound):
	rand_indices = []
	# Determine the number of random indices
	if num_indices <= 0:
		num_indices = random.randint(1,upper_bound - 1)
		print num_indices
	else:
		num_indices = min(num_indices, upper_bound - 1)
	
	# Pull indices at random from a 'bag' of indices
	indices = [x for x in range (0,upper_bound)]
	random.shuffle(indices)
	for i in range (0, num_indices):
		rand_indices.append(indices.pop())
	rand_indices.sort()
	return rand_indices
	
"""
	Each individual's fitness score is looked up based on its chromosomes
	and forms which are hashed into a dictionary.
	Lists are not hashable data structures, so the chromosomes and genes
	must be fit into tuples first.
"""
def Individual_To_Tuple(individual):
	chroms = []
	# Turn each chromosome into a tuple
	for chrom in individual.chromosomes:
		chroms.append(tuple([tuple(chrom.genes), chrom.form, chrom.swappable]))
	# Turn the chromosomes into a tuple
	return tuple(chroms)

"""
	Takes an individual that is in tuple format and builds
	an actual Individual object from the data contained 
	within the tuples.
"""
def Tuple_To_Individual(ind_tuple):
	chroms = []
	for chromosome in ind_tuple[0]:
		chroms.append(chro.Chromosome(list(chromosome[0]), chromosome[1], chromosome[2]))
	return ind.Individual(chroms, float(ind_tuple[1]), "ready")

"""
	Builds a list of genes (keeping them in order!)
	given an individual.
"""	
def Build_Genes_List(individual):
	genes_list = []
	tup_ind = Individual_To_Tuple(individual)
	for tup_chrom in tup_ind:
		for gene in tup_chrom[0]:
			gene = gene.split("*")
			gene[0] = gene[0].strip("(")
			genes_list.append(gene[0])
	return genes_list
	
"""
	Pull out a chunk of a column in the table from a starting
	cell to the first blank cell encountered.
"""
def Get_Slice(sheet, col, start_row=0, end_row=None): 
	# Grab the part of the column we care about.
	slice = sheet.col_slice(col, start_row)

	# Pull out the values and stop on either the first blank cell
	# or the end of the range.
	vals = []
	count = start_row
	for val in slice:
		if val.ctype != EMPTY and val.ctype != ERROR: # we've found something.
			if val.ctype == STRING:
				vals.append(str(val.value))
			else:
				vals.append(val.value)
		else: # we've hit an empty cell so we're done looking for substitutes.
			break
			
		if count == end_row: # we've reached the end of the slice.
			break
		count += 1
	return vals

"""
	Parse individuals from the first row of the
	specified sheet from the specified workbook.
"""
def Parse_Individuals(book_name, sheet_name, first_row):
	# Open the workbook to the correct worksheet
	book = xlrd.open_workbook(book_name)
	sheet = book.sheet_by_name(sheet_name)
	
	# Set up the indices of important cells.
	#  INCOMPLETE - is there a cleaner way to do this??
	first_data_row = first_row
	subs_col = 1
	first_data_col = 1
	last_data_col = 13

	# 1) Find the number of parameters that each individual should have.
	#

	# Grab the part of the substitutes column we care about.
	slice = Get_Slice(sheet, subs_col, first_data_row)
	num_subs = len(slice)

	# 2) Pull out the data-containing cells from the table, col by col.
	#

	data_cols = []
	for i in range (first_data_col, last_data_col + 1):
		slice = Get_Slice(sheet, i, first_data_row, first_data_row + num_subs)
		data_cols.append(slice)
	
	# Set the index into data_cols to be the column number in the spreadsheet.
	mins = 			data_cols[1]
	maxs = 			data_cols[2]
	types = 		data_cols[3]
	chrom_nums = 	data_cols[4]
	chrom_forms = 	data_cols[5]
	chrom_swap = 	data_cols[6]
	comments = 	    data_cols[12]

	# 3) Build individuals and return them in a list.

	individuals = []
	ind_1_col = 	7
	ind_n_col = 	11
	for ind_parms_list in data_cols[ind_1_col:ind_n_col+1]:

		# Ignore any parameter lists that don't have as many parameters
		# as there are substitutes because we can't make an incomplete individual.
		if len(ind_parms_list) < num_subs:
			# probe
			print "Ignoring individual: incomplete parameter list. Missing", \
				num_subs - len(ind_parms_list), "parameters."
			for parm in ind_parms_list:
				print "\t" + str(parm)
			print ""
			break
		
		i = 0
		genes = []
		chroms = []
		curr_chrom = chrom_nums[i]
		for parm in ind_parms_list: # build a gene.
			if types[i] == "i" or types[i] == "b": # then round to zero decimal places
				gene = "(" + str(int(round(parm, 0))) + "*" + str(mins[i]) + "*" + str(maxs[i]) + \
				"*" + str(types[i]) + ")"
			elif types[i] == "f": # then round to three decimal places
				rounded_parm = "%.3f" % parm
				gene = "(" + str(rounded_parm) + "*" + str(mins[i]) + "*" + str(maxs[i]) + \
					"*" + str(types[i]) + ")"
			else:
				gene = "(" + str(parm) + "*" + str(mins[i]) + "*" + str(maxs[i]) + \
					"*" + str(types[i]) + ")"
			genes.append(gene)
			
			# Determine whether it is time to build a new chromosome.
			next_i = i + 1
			build_chrom = False
			if next_i == num_subs: # we've hit the last gene...
				build_chrom = True
			elif chrom_nums[i] != chrom_nums[next_i]: # we've hit a new chromosome
				build_chrom = True
			
			# Convert chromosome swappability from a string to a boolean
			if chrom_swap[i] == True:
				swappability = True
			else:
				swappability = False
			
			if build_chrom: # then make a new chrom with the genes we've gathered.
				chroms.append(chro.Chromosome(genes, chrom_forms[i], swappability))
				genes = []
				new_chrom = False
			# and on to the next parameter...
			i += 1
		# Build a new individual with the list of chromosomes we've gathered.
		individuals.append(ind.Individual(chroms))
		chroms = []
	return individuals