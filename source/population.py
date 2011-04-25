"""
	Contains the definition of the population class for the genetic algorithm.
"""
import math
import random
import operator
import sys
import time
import pdb
import os
import xlwt # read excel
import xlrd # write excel

import individual as ind
import chromosome as chro
import evaluator as eval
import utils
import settings

true = 1
false = 0

class Population:
	
	"""
	Data members:
	
	Lists of individuals:
	breeders
	offspring
	
	Dictionaries where chromosome lists map to fitness scores:
	current_pop
	culled_pop
	eval_cache
	
	list of evaluators
	
	average_fitness
	is_init
	max_pop_size 
	mutation_rate
	num_cross_points
	intra_swap_rate
	"""
	
	"""
	****
		Initialization
	****
	"""
	
	"""
		Population Constructor
	"""
	def __init__(self):
		# Init from settings
		self.max_pop_size = int(settings.Get_Setting("max_pop_size"))
		self.mutation_rate = float(settings.Get_Setting("mutation_rate"))
		self.num_cross_points = int(settings.Get_Setting("number_crossover_points"))
		self.intra_swap_rate = int(settings.Get_Setting("intra_swap_rate"))
		
		# Init the rest...
		self.is_init = false
		self.average_fitness = 0
		self.current_pop = {}
		self.culled_pop = {}
		self.eval_cache = {}
		self.breeders = []
		self.offspring = []
		self.evaluators = []
		
		# Init the offspring and current population
		self.Genesis()
		
		# Init the evaluators
		num_procs = int(settings.Get_Setting("number_cpus"))
		eval_type = "smp"
		for i in range (0, num_procs):
			self.evaluators.append(eval.Evaluator(eval_type))
			
	"""
		Build the initial population of uniques.
	"""
	def Genesis(self):
		# If specified, load uniques from a file.
		load_uniques = int(settings.Get_Setting("seed_uniques"))
		if load_uniques:
			self.Load_Uniques()
			
		# Scrape individuals out of the spreadsheet and append them to the offspring.
		workbook_name = settings.GA_book
		unscored_inds = utils.Parse_Individuals(workbook_name, "Solver", 18)

		# Screen out repeats using a local dictionary
		new_unscored_inds = {}
		for ind in unscored_inds:
			ind_tup = utils.Individual_To_Tuple(ind)
			if ind_tup not in new_unscored_inds: # then we've got a unique unscored individual
				# add the unscored unique to the offspring and to the 'screening' dictionary
				self.offspring.append(ind)
				new_unscored_inds[ind_tup] = 1
				
		# We need at least two offspring or at least two scored individuals for
		# the ga to get going. Exit if this is not the case.
		if len(self.offspring) < 2 and len(self.current_pop) < 2:
			error = len(self.offspring), "offspring and", len(self.current_pop), \
					""" in the current population is insufficient to get the ga running.
					At least two unique unscored OR two unique scored individuals are required."""
			print error
			sys.exit()
			
		self.is_init = true
		
	"""
		Load the uniques stored in the GA spreadsheet.
		The workbook is called "Seed Population".
	"""
	def Load_Uniques(self):
		#
		# INCOMPLETE - parse uniques from spreadsheet and add them to the current population.
		#
		pass
		
	"""
	****
		Reproduction Operators:
	****
	"""
	
	"""
		Perform the reproduction operators on a population.
		Select, Crossover, Mutate.
	"""
	def Reproduce(self):
		# Skip reproduction if we don't have enough parents
		if len(self.current_pop) < 2:
			# probe
			print "\n" * 2
			print "Skipping Reproduction--Current Population is too small..."
			return
			
		# Reproduce until there are some offspring to evaluate.
		while len(self.offspring) < 1:
			# Select a pair to breed
			self.Select()
			# Breed the pair to make offspring
			self.Crossover()
			
			# Mutate each of the offspring
			self.Mutate()
			# Throw out the repeats.
			self.Screen_Offspring()
			
	"""
		Select the members of the population that will be
		paired up for breeding.
	"""
	def Select(self):
		# Calculate each individual's fitness score (raw/avg).
		self.Get_Average_Fitness()
		current_pop = self.Get_Current_Pop()
		processed_pop = []
		for ind in current_pop:
			ind.fitness = ind.raw_fitness / self.average_fitness
			processed_pop.append(ind)
		current_pop = processed_pop
		
		"""
			Clear the list of breeders and then select two:
				1) Sort the population on fitness scores
				2) Spin a roulette wheel that has a number of partitions equal
					to the number of individuals. Each partition of the board
					is proportional in size to the fitness score of an individual.
					a) get a random in the range [0, sum of each ind's fitness]
					b) while the sum of scores is less than the random:
						i) iterate through the population adding scores
							to the sum.
					c) the ind selected is the one before the curr index
		"""
		del self.breeders[:]
		for i in range (0,2):
			index = 0
			scores_sum = 0
			# sort ascending on the fitness
			current_pop.sort(key=operator.attrgetter("fitness"))
			upper_bound = sum([ind.fitness for ind in current_pop])
			rand = utils.Rand_In_Range(0, upper_bound)
			
			while scores_sum < rand:
				scores_sum = scores_sum + current_pop[index].fitness
				index = index + 1
			self.breeders.append(current_pop.pop(index - 1))
				
	"""
		Perform chromosome swaps on the pairs of breeders.  Intra
		swaps are performed with a given probability where the forms
		of the chromosomes match and allow intra-swapping.
	"""
	def Crossover(self):
		# Setup
		offspring1 = []
		offspring2 = []
		mate1 = self.breeders[0]
		mate2 = self.breeders[1]
		have_not_crossed = false
		num_chroms = int(settings.Get_Setting("number_chromosomes"))
		crossover_pts = utils.Generate_Random_Indices(self.num_cross_points, num_chroms)
		i = 0
		
		# Do the normal crosses and intra chromosomal gene swaps
		for i in range (0, num_chroms):
			if i in crossover_pts: # do a cross
			
			# Do an intra-chromosomal swap if the rate is >0, otherwise
				# just do a basic crossover swap of entire chromosomes.
				if self.intra_swap_rate > 0:
					chrom1 = mate2.chromosomes[i]
					chrom2 = mate1.chromosomes[i]
					
					# Check for swappability and compatibility
					if chrom1.Intra_Swappable() == True and chrom1.form == chrom2.form:
						random.seed()
						chance = random.random()
						
						# 'Rolled the dice', now see if we swap...
						if chance < (self.intra_swap_rate / 100.0):
							"""
								Intra-swap logic:
									In essence, we pick a random swap point
									and then swap the genes of the two
									chromosomes from the swap point to the
									end of the list of genes.
							"""
							swap_point = random.randint(0, len(chrom1.genes) - 1)
							
							genes_1a = chrom1.genes[:swap_point]
							genes_1b = chrom2.genes[swap_point:]
							genes_1new = genes_1a + genes_1b
							
							genes_2a = chrom2.genes[:swap_point]
							genes_2b = chrom1.genes[swap_point:]
							genes_2new = genes_2a + genes_2b
							
							offspring1.append(chro.Chromosome(genes_1new, chrom1.form, chrom1.swappable))
							offspring2.append(chro.Chromosome(genes_2new, chrom2.form, chrom2.swappable))
						else:
							have_not_crossed = true
					else:
						have_not_crossed = true
				else:
					have_not_crossed = true
				if have_not_crossed:
					# Do a basic crossover
					offspring1.append(mate2.chromosomes[i])
					offspring2.append(mate1.chromosomes[i])
			else:
				# No crossing here...
				offspring1.append(mate1.chromosomes[i])
				offspring2.append(mate2.chromosomes[i])
		self.offspring.append(ind.Individual(offspring1))
		self.offspring.append(ind.Individual(offspring2))
	
	"""
		Mutate each offspring
	"""
	def Mutate(self):
		for child in self.offspring:
			child.Mutate()

	"""
		Remove the worst performers from the population
	""" 
	def Cull(self):
		max_pop_size = int(settings.Get_Setting("max_pop_size"))
		if len(self.current_pop) <= max_pop_size: # then don't cull anyone
			return
		# The new population will comprise the top individuals of the 
		# current population.  Cull the rest.
		saved_pop = self.Get_Best_Individuals(max_pop_size)
		culled_pop = self.Get_Worst_Individuals(len(self.current_pop) - max_pop_size)
		
		# Dump the current population to a list and then empty it
		current_pop_list = self.current_pop.items()
		self.current_pop.clear()

		# Rebuild the current population and add to the culled population
		for saved in saved_pop:
			self.current_pop[utils.Individual_To_Tuple(saved)] = saved.raw_fitness
		for culled in culled_pop:
			self.culled_pop[utils.Individual_To_Tuple(culled)] = culled.raw_fitness
		
	"""
	****
		Utilities
	****
	"""
	
	"""
		Directs the evaluation of the current population members'
		fitness scores to the correct routine.
	"""
	def Eval(self):
		# Wait until at least one evaluator is not busy
		while self.All_Busy():
			time.sleep(1)
		
		# Check the state of each evaluator and assign work to the 
		# evaluator(s) that aren't busy.
		for evaluator in self.evaluators:
			
			#
			# Take care of the cases where the evaluator is either: new,
			# has a successfully evaluated individual, or has a timed-out
			# individual.
			#
			
			# Evaluator is freshly constructed:
			if evaluator.state == "ready":
				pass
			
			# Evaluation was a success:
			elif evaluator.state == "success":
				# Assert that we've not wasted an evaluation!
				ind_tuple = utils.Individual_To_Tuple(evaluator.individual)
				if ind_tuple in self.current_pop or ind_tuple in self.culled_pop:
					print "Oh my, seems we've wasted an eval..."
					sys.exit()	
				# Add individual to the current population and add an
				# entry to the progress log. Increment the # of evals.
				self.current_pop[utils.Individual_To_Tuple(evaluator.individual)] = evaluator.individual.raw_fitness
				settings.log.write(evaluator.individual.To_String() + "\n")
				settings.num_evals += 1
				
				# Update the console screen every-so-often...
				if settings.num_evals % 10 == 0:
					utils.Update_Console()
					
			# Evaluation Timed Out:
			elif evaluator.state == "timeout":
				# Add individual back into offspring because evaluation timed out.
				del eval_cache[utils.Individual_To_Tuple(evaluator.individual)]
				self.offspring.append(evaluator.individual)
				
			# Now that we've handled the possible evaluator
			# states(besides 'busy') get that evaluator working again.
			if evaluator.state != "busy":
				evaluator.state = "ready"
				
				# Skip this if there are no offspring to assign...
				if len(self.offspring) < 1:
					return
				
				# Avoid a repeat of an individual that is in evaluation.
				# Grab an offspring to eval.
				victim = self.offspring.pop(0)
				victim_tuple = utils.Individual_To_Tuple(victim)
				
				# If the ind. is already in the current, culled, or cache dictionaries, then it is a repeat.
				repeat_found = false
				if victim_tuple in self.eval_cache or victim_tuple in self.current_pop or victim_tuple in self.culled_pop:
					repeat_found = true
					# probe
					if settings.num_screened % 300 == 0:
							print "Has screened", settings.num_screened, " repeat individuals to avoid multiple evaluation.\n"
					settings.num_screened = settings.num_screened + 1
				
				# Keep checking until we've got a non-repeat offspring
				while repeat_found:	
					
					# If there are no more offspring then we don't have any to assign to evaluators.
					# Wait until the after the next reproduction.
					if len(self.offspring) < 1:
						if settings.num_empties % 300 == 0:
							print "", settings.num_empties, "iterations with offspring emptying before assignment.\n"
						settings.num_empties += 1
						return
					
					victim = self.offspring.pop(0)
					victim_tuple = utils.Individual_To_Tuple(victim)
					
					if victim_tuple in self.eval_cache or victim_tuple in self.current_pop or victim_tuple in self.culled_pop:
						repeat_found = true
						settings.num_screened = settings.num_screened + 1
					else:
						repeat_found = false
					
				# Assign an individual for evaluation.
				self.eval_cache[utils.Individual_To_Tuple(victim)] = 0
				evaluator.Task(victim)
				
	"""
		Ensure that no individuals are evaluated twice by screening
		the new additions to the group of offspring to check for repeats.
	"""
	def Screen_Offspring(self):
		for child in self.offspring:
			child_tuple = utils.Individual_To_Tuple(child)
			if child_tuple in self.eval_cache or child_tuple in self.current_pop or child_tuple in self.culled_pop:
				self.offspring.remove(child)

				
	"""
		Dump the current population hash into a list of individuals
	"""
	def Get_Current_Pop(self):
		current_pop = []
		current_pop_list = self.current_pop.items()
		for ind in current_pop_list:
			current_pop.append(utils.Tuple_To_Individual(ind))
		return current_pop
	
	def Get_Culled_Pop(self):
		culled_pop = []
		culled_pop_list = self.culled_pop.items()
		for ind in culled_pop_list:
			culled_pop.append(utils.Tuple_To_Individual(ind))
		return culled_pop
	
	"""
		Calculate the average fitness of the current population.
	"""
	def Get_Average_Fitness(self):
		sum = 0
		scores = self.current_pop.values()
		for score in scores:
			sum = sum + float(score)
		self.average_fitness = sum / len(scores)
		
		# Avoid division by zero
		if self.average_fitness == 0:
			self.average_fitness = 0.01
	
	"""
		Check on each of the evaluators. If there are
		any evaluators that are no longer busy then
		return false. Otherwise all are busy so return true.
	"""
	def All_Busy(self):
		for evaluator in self.evaluators:
			evaluator.Update()
		for evaluator in self.evaluators:
			if evaluator.state != "busy":
				return False
		return True
	
	"""
		Get the X most fit individuals in the current population.
	"""
	def Get_Best_Individuals(self, X):
		# Do some bounds assurance on the user input: can't be less
		# than zero, can't be more than the max # in the current pop.
		goal = int(max(0, min(X, len(self.current_pop))))
		
		if len(self.current_pop) < 1:
			print "Current Population is empty."
			sys.exit()
		
		# Convert the current pop hash into a list 
		# that is sorted ascending on raw fitness.
		current_pop_list = self.current_pop.items()
		current_pop_list.sort(key=operator.itemgetter(1))
		
		# Who the best individuals are depends upon the optimization type
		opt_type = "maximize" #INCOMPLETE - make this a setting when other opt types are implemented
		if opt_type == "maximize":
			best = current_pop_list[int(len(current_pop_list) - goal):len(current_pop_list)] # from end - goal to end
		elif opt_type == "minimize":
			best = current_pop_list[:goal] # from start to goal
		elif opt_type == "target":
			pass # calculate the distance of each from the target and sort on distance, then grab the x smallest
		
		# Build individuals from the contents of the tuples
		best_inds = []
		for ind_tuple in best:
			best_inds.append(utils.Tuple_To_Individual(ind_tuple))
		return best_inds
	
	"""	
		Get the most fit individual in the current population.
	"""
	def Get_Best_Individual(self):
		return Get_Best_Individuals(1)[0]
	
	"""
		Get the X least fit individuals in the current population.
	"""
	def Get_Worst_Individuals(self, X):
		# Do some bounds assurance on the user input: can't be less
		# than zero, can't be more than the max # in the current pop.
		goal = int(max(0, min(X, len(self.current_pop))))
		
		if len(self.current_pop) < 1:
			print "Current Population is empty."
			sys.exit()
		
		# Convert the current pop hash into a list 
		# that is sorted ascending on raw fitness.
		current_pop_list = self.current_pop.items()
		current_pop_list.sort(key=operator.itemgetter(1))
		
		# Who the worst individuals are depends upon the optimization type
		opt_type = "maximize" #INCOMPLETE - make this a setting when other opt types are implemented
		if opt_type == "maximize":
			worst = current_pop_list[:goal] # from start to goal
		elif opt_type == "minimize":
			worst = current_pop_list[int(len(current_pop_list) - goal):] # from end - goal to end
		elif opt_type == "target":
			pass # calculate the distance of each from the target and sort on distance, then grab the x largest
		
		# Build individuals from the contents of the tuples
		worst_inds = []
		for ind_tuple in worst:
			worst_inds.append(utils.Tuple_To_Individual(ind_tuple))
		return worst_inds
	
	# Dump all evaluated individuals to a file
	def Dump_Uniques(self):
		uniques_path = os.path.join(settings.Get_Setting("output_dir"), settings.Get_Setting("uniques_filename"))
		uniques_dump = open(uniques_path, "w")
		
		uniques_dump.write("Current Population:\n")
		for unique in self.Get_Current_Pop():
			uniques_dump.write(unique.To_String() + "\n")
		
		uniques_dump.write("Culled Population:\n")
		for unique in self.Get_Culled_Pop():
			uniques_dump.write(unique.To_String() + "\n")
		uniques_dump.write("Done")
		uniques_dump.close()
	
"""
Testing
"""
def main():
		tester = Population()
		tester.Genesis()
		tester.Dump_Uniques()

if __name__ == "__main__":
    main()