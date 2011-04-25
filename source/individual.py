"""
	Contains the definition of the individual class for the genetic algorithm.
"""
import sys
import utils
import chromosome as chrom
import settings

class Individual:
	
	# Data members:
	#
	# chromosomes
	# raw_fitness
	# fitness
	# num_chromosomes
	# state in {queue, eval, ready, timeout, ...}
	
	# Constructor
	def __init__(self, chromosomes, raw_fitness=0.0, state="queue"):
		self.num_chromosomes = int(settings.Get_Setting("number_chromosomes"))
		
		# Ensure the correct number of chromosomes
		if len(chromosomes) != self.num_chromosomes:
			print "Error:", self.num_chromosomes, \
				  "chromosomes needed and", len(chromosomes), "were given."
			sys.exit()
		self.chromosomes = chromosomes[:]
		
		self.state = state
		self.raw_fitness = raw_fitness
		self.fitness = 0
	
	# Mutate the individual
	def Mutate(self):
		for chrom in self.chromosomes:
			chrom.Mutate()
	
	# Find the individual's fitness. This is only called
	# when the evaluation type is set to local.
	def Evaluate(self):
		print "You must implement the Evaluate() method of the individual class!"
		self.raw_fitness = 0
		
	# Format the individual as a string
	def To_String(self):
		ind_string = ""
		for chromosome in self.chromosomes:
			ind_string = ind_string + chromosome.To_String()
			ind_string = ind_string + " ; "
		score = "%.2f" % self.raw_fitness
		ind_string = ind_string + score # + str(self.raw_fitness)
		return ind_string

"""
	Testing
"""
def main():
		tester = Individual([chrom.Chromosome([1,2,3]), chrom.Chromosome(["a","b","c"],"z",False)])
		tester.Print()

if __name__ == "__main__":
    main()