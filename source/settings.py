"""
	Handles the setup and accessing of the settings for the genetic algorithm.
	Make sure the value of init_file matches the name of the settings file.
"""
import os
import datetime as dt
import xlrd

import utils

settings = {}		# Global GA and OASIS settings lookup
is_init = False		# Has the settings lookup been initialized?
num_evals = 0		# Tracks the number of successful evaluations
first_eval = True   # The first evaluation requires some extra work
num_iters = 0       # Tracks the number of main-evolve-loop iterations
num_screened = 1	# Tracks the number of repeat individuals who weren't re-evaluated
num_empties = 0		# Counts iterations where no offspring make it to evaluation
log = None			# Global log
GA_book = "..\output\genetic-algorithm.xls" # Spreadsheet where settings are stored
	

# Parse and load the settings from the GA wrapper spreadsheet
def init():
	# Excel spreadsheet cell mapping used only for settings initialization
	GA_sheet = "GA Settings"
	GA_cell = { \
		"max_evals" : (4,3), \
		"max_pop_size" : (8,3), \
		"mutation_rate" : (9,3), \
		"number_crossover_points" : (10,3), \
		"intra_swap_rate" : (11,3), \
		"number_chromosomes" : (16,3), \
		"eval_timeout" : (23,3), \
		"error_fitness" : (24,3), \
		"seed_uniques" : (25,3), \
		"uniques_filename" : (26,3), \
		"number_cpus" : (27,3), \
		"output_dir" : (28,3), \
		"source_dir" : (29,3), \
	}

	OASIS_sheet = "OASIS Settings"
	OASIS_cell = { \
		"home_dir" : (7,3), \
		"run_dir" : (8,3), \
		"onevar_dir" : (15,3), \
		"onevar_commands" : (16,3), \
		"template_dir" : (22,3) \
	}
	
	# Parse the cells out of the spreadsheet and insert them into the settings lookup
	book = xlrd.open_workbook(GA_book)
	sheet = book.sheet_by_name(GA_sheet)
	
	# Grab the GA settings
	for cell in GA_cell:
		row, col = GA_cell[cell][0], GA_cell[cell][1]
		settings[cell] = sheet.cell_value(row, col)
	
	# Grab the OASIS settings
	sheet = book.sheet_by_name(OASIS_sheet)
	for cell in OASIS_cell:
		row, col = OASIS_cell[cell][0], OASIS_cell[cell][1]
		settings[cell] = sheet.cell_value(row, col)
	is_init = True

# Grab a setting
def Get_Setting(x):
	if not is_init:
		init()
	return settings[x]

# Ready the log for writing by the GA
def Log_Setup():
	global log
	log_output_path = Get_Setting("output_dir")
	time = dt.datetime.now().strftime("%Y-%m-%d__%Hh%Mm")
	log_name = time + "__log.txt"
	log = open(os.path.join(log_output_path,log_name), "w")
	log.write("Log initially written on " + time + "\n")
	
	log.write("Settings:\n")
	for setting in settings:
		log.write(setting + " : ")
	log.write("\n\n****************************************\n\n")
	# Dump the log file's path to a file so that another script
	# can figure out what the most recent output is.
	log_dump = open("latest_log.txt", "w")
	log_dump.write(os.path.join(log_output_path,log_name))
	log_dump.close()