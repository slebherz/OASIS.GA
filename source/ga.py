"""
	Contains the definition of the GA class for the genetic algorithm.
"""
import sys

import population as pop
import utils
import settings

class GA:

	# Data members:
	#
	# population
	# current_iter
	# max_evals
	
	# Constructor
	def __init__(self):
		self.max_evals = int(settings.Get_Setting("max_evals"))
		self.current_iter = 1
		self.population = pop.Population()
		settings.Log_Setup()
		
	"""
		Evolves a population until some stopping criteria are met
	"""
	def Evolve(self):
		while not self.Finished():
		
			# Eval, Cull, then Reproduce.
			self.population.Eval()
			self.population.Cull()
			self.population.Reproduce()
			
			# Dump uniques every-so-often and continue evolving...
			if settings.num_evals % 10 == 0:
				self.population.Dump_Uniques()
			settings.num_iters = settings.num_iters + 1

		# Evolution complete...
		self.population.Dump_Uniques()
		return
	
	"""
		Check the stopping conditions
	"""
	def Finished(self):
		if settings.num_evals >= self.max_evals:
			return True
		return False

"""
	Testing
"""
def main():
		tester = GA()
		tester.Evolve()

if __name__ == "__main__":
    main()