"""
	Contains the definition of the evaluator class for the genetic algorithm.
"""
import random
import sys
import math
import subprocess
import os
import shutil
import time
import datetime as dt

import individual as ind
import settings
import utils

class Evaluator:
	
	"""
	Data Members:
	
	individual
	state:
		ready - just contructed
		busy - evaluating
		success - successfully evaluated
		timeout - evaluation timed out
	progress:
		ready - just constructed
		running model - model is in execution
		finished model - model execution complete
		timeout - model execution has timed out
	eval_type:
		Normal - calls the individual's evaluation routine
		SMP - multiprocessing on one computer
		Condor - distributed processing
	process - the process handle
	run_path - path to the evaluator's current run
	start_time - datetime object that stores start time of model execution
	"""
	
	"""
	****
		Initialization
	****
	"""
	
	"""
		Construct an evaluator.
	"""
	def __init__(self, eval_type):
		self.eval_type = eval_type
		self.state = "ready"
		self.progress = "ready"
		self.individual = None
		self.process = None
		self.run_path = ""
		self.start_time = None
	
	"""
		Assign an individual to the evaluator and begin evaluation.
	"""
	def Task(self, individual):
		self.individual = individual
		self.Evaluate()
	
	"""
	****
		Evaluation
	****
	"""
	def Evaluate(self):
		self.state = "busy"
	
		# Call the right evaluation routine...
		if self.eval_type == "normal":
			self.Normal_Eval()
		elif self.eval_type == "smp":
			self.SMP_Eval()
		elif self.eval_type == "condor":
			self.Condor_Eval()
		else:
			print "Evaluation type '" + self.eval_type + "' is unsupported."
			sys.exit()
	
	# Find out whether the evaluator's individual has finished evaluation.
	def Update(self):
		# Skip the updating of non-busy evaluators.
		if self.state != "busy":
			return
		
		# Call the right evaluation routine...
		if self.eval_type == "normal":
			self.Normal_Update()
		elif self.eval_type == "smp":
			self.SMP_Update()
		elif self.eval_type == "condor":
			self.Condor_Update()
		else:
			print "Evaluation type '" + self.eval_type + "' is unsupported."
			sys.exit()
			
	"""
	****
		Evaluation Sub-Types
	****
	"""
	
	# Single process evaluation
	def Normal_Eval(self):
		self.individual.Evaluate()

	# Single process update
	def Normal_Update(self):
		if self.individual.state == "ready":
			self.state == "success"
		
	# Multi-process single machine evaluation
	def SMP_Eval(self):
		self.Prep_Directory()
		self.Prep_Parms()
		self.progress = "running model"
		self.Run_Model()
		
	# Multi-process single machine update
	def SMP_Update(self):
		
		# Abort if we've timed out
		if self.Timed_Out():
			# Update states.
			self.progress = "finished model"
			self.state = "timeout"
			self.individual.state = "timeout"
			
			# End the process and clean up.
			self.process.kill()
			self.Clean_Up()
			return
		
		# Otherwise check on our process.
		if self.progress == "running model":
			# probe
			if self.process == None:
				print "progress = running model but there is no process..."
				sys.exit()
			# Poll Process
			self.process.poll()
			
			if self.process.returncode == None: # Do nothing, model is running.
				return
			else: # We're done processing!
				self.progress = "finished model"
				self.state = "success"
				if self.Sim_Success(): # then run onevar.
					self.Run_Onevar()
					self.Set_Score()
				else: # whoops, the model didn't execute successfully.
					self.Set_Error_Score()
				self.Clean_Up()
				
	# Multi-machine evaluation
	def Condor_Eval(self):
		print "Called Evaluator::Condor_Eval()"
		"""
			1) package up the individual
			2) queue up condor jobs
			3) return when the individual is either ready or timed-out
		"""
	
	# Multi-machine update
	def Condor_Update(self):
		pass
	
	"""
	****
		Evaluation Helpers
	****
	"""
	
	# Copy the template run directory into a unique run directory
	def Prep_Directory(self):
		run_path = settings.Get_Setting("run_dir")
		template_dname = settings.Get_Setting("template_dir")
		src_path = os.path.join(run_path, template_dname)
		
		# Generate a directory name.
		dname = str(random.randint(0,1000)) + "_ga_run"
		dest_path = os.path.join(run_path, dname)
		
		# Ensure our directory name is unique.
		while os.path.isdir(dest_path):
			dname = str(random.randint(0,1000)) + "_ga_run"
			dest_path = os.path.join(run_path, dname)
			
		# Copy template run into new directory
		shutil.copytree(src_path, dest_path)
		self.run_path = dest_path
		
	# Prepare the model parameters for the simulation run.
	def Prep_Parms(self):
		# Set up access to the parameters file.
		parms_path = os.path.join(self.run_path, "ocl\GA_parms.ocl")
		if not os.path.exists(parms_path):
			# probe
			print "File:", parms_path, " not found."
			sys.exit()
		lines = utils.Lines_In_File(parms_path)
		
		# Determine the number of lines that contain substitute commands.
		num_subs = 0
		for line in lines:
			if ":substitute:" in line or ":Substitute:" in line:
				num_subs += 1
		
		# Build a list of the genes to be added to each substitute command.
		gene_count = 0
		genes = utils.Build_Genes_List(self.individual)
		
		# probe
		if num_subs < len(genes):
			print "more genes than lines in ga_parms..."
			print num_subs
			print genes
			sys.exit()
		
		# Add the parameters to the template ga parms file.
		# Leave the line alone unless it has a substitute command within.
		new_lines = []
		for line in lines:
			if ":substitute:" in line or ":Substitute:" in line: # then add a ga parm to the line.
				line = line.strip("\n") + str(genes[gene_count]) + "\n"
				gene_count += 1
			new_lines.append(line)
			
		# Re-write the new lines into the ga parameters file.
		parms_file = open(parms_path, "w")
		parms_file.writelines(new_lines)
		parms_file.close()
		
	# Run a simulation.
	def Run_Model(self):
		# generate command
		home_path = settings.Get_Setting("home_dir")
		cmd = os.path.join(home_path, "model.exe") + " dir=" + self.run_path
		
		# Suppress model.exe msgbox errors for all runs after the first
		if settings.first_eval:
			settings.first_eval = False
		else: # add the flag to supress errors
			cmd += " NoClick"
		self.start_time = dt.datetime.now()
		self.process = subprocess.Popen(cmd, shell=True)
		
		#
		# INCOMPLETE - remove sleep if errors persist.
		#
		time.sleep(.25)
		
	# Parse debug.out to guesstimate whether the run was a success.
	def Sim_Success(self):
		goal = 0
		
		# try to parse debug.out--it might not be there at all.
		try:
			# parse debug.out and set sim_success accordingly
			debug_path = os.path.join(self.run_path, "debug.out")
			
			# If we find 'Completed' and Elapsed in the file
			# then the sim executed successfully. We get a point
			# for each occurrence of the 'goal' words.
			for line in utils.Lines_In_File(debug_path):
				if "Completed" in line:
					goal += 1
				if "Elapsed" in line:
					goal += 1
		except IOError:
			pass
			
		# If we've hit our two goal words, the sim was a success.
		if goal == 2:
			return True
		else:
			return False
	
	# Run specified onevar commands
	def Run_Onevar(self):
		onev_exe_path = os.path.join(settings.Get_Setting("home_dir"), "onevar.exe")
		onev_dir_path = settings.Get_Setting("onevar_dir")
		
		"""
			Each command is a [name].1v file. The commands setting is stored as one long string.
		The string is split by whitespace into separate words so that the files may be processed
		one by one. They should be processed front to back in case a later command requires
		output from a prior command(s).
		"""
		commands = settings.Get_Setting("onevar_commands").split()
		
		for cmd in commands:
			# Generate the command. Supress errors--they need to be checked for in a non-generic way.
			# sample: command = [onevar exe path] dir=[run path] in=[.1v path]
			onev_file_path = os.path.join(onev_dir_path, cmd)
			cmd_line = onev_exe_path + " dir=" + self.run_path + " in=" + onev_file_path + " NoClick"
			
			"""
				Start the onev processing.  We'll wait for each to finish since they run pretty quickly.
			Sort of INCOMPLETE: For a long running onevar file, our parallelization efficiency
			will take a hit because our 'main' process is the process waiting around after
			each run for all of the onev's to be processed. To change this behavior: this function,
			the Update() function, and the evaluator.progress states will need revision.
			"""
			onev_proc = subprocess.Popen([cmd_line], shell=True)
			onev_proc.wait()
			
	# Set the score for an individual after they have been evaluated.
	# final_score.txt is expected to be written into the run directory
	# in the file format:
	#	score: [SCORE]
	def Set_Score(self):
		err_score = str(settings.Get_Setting("error_fitness"))
		# Spawn set_score.py to find the score by some unknown means...
		proc = subprocess.Popen(['python set_score.py', self.run_path, err_score], shell=True)
		proc.wait()

		# Set the score to the value in the output file final_score.txt
		score_path = os.path.join(self.run_path, "final_score.txt")
		for line in utils.Lines_In_File(score_path):
			if "score" in line:
				line = line.split(":")
				self.individual.raw_fitness = float(line[-1])
				
	# Set the score to the specified score to assign upon an error
	def Set_Error_Score(self):
		self.individual.raw_fitness = settings.Get_Setting("error_fitness")
	
	# Evaluation is complete so delete the run directory--if we can.
	def Clean_Up(self):
		try:
			if os.path.isdir(self.run_path):
				shutil.rmtree(self.run_path)
		except WindowsError:
			pass
		
	# Determines whether a process has timed out.
	def Timed_Out(self):
		timeout_limit = settings.Get_Setting("eval_timeout")
		# Determine whether we've timed out.
		curr_time = dt.datetime.now()
		# Calculate elapsed time in seconds.
		time_evalling = (curr_time - self.start_time).seconds
		if time_evalling >= timeout_limit: # then we've timed out...
			return True
		return False