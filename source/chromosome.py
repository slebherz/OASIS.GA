"""
	Contains the definition of the chromosome class for the genetic algorithm.
"""
import random
import utils
import settings

class Chromosome:
	
	# Data members:
	#
	# genes
	# form
	# swappable
	
	# Constructor
	def __init__(self, genes=[], form="A", swappable=True):
		self.genes = genes
		self.form = form.lower()
		self.swappable = swappable
	
	# Mutate the chromosome
	def Mutate(self):
		mutation_rate = float(settings.Get_Setting("mutation_rate"))
		new_genes = []
		for gene in self.genes:
			# Roll the dice to see whether we mutate the gene
			if random.random() < (mutation_rate / 100):
				
				# Parse the gene
				# gene format:
				#	([val]*[lower bound]*[upper bound]*[type]
				gene_members = gene.split("*")
				type = gene_members[3].strip(")")
				if type == "f":
					value = float(gene_members[0].strip("("))
				elif type == "i":
					value = int(gene_members[0].strip("("))
				else:
					print "Unknown gene type: ", type
				lower_bound = float(gene_members[1])
				upper_bound = float(gene_members[2])
				
				# Do the mutation
				if type == "f": # Mutate the float
					value = utils.Rand_In_Range(lower_bound, upper_bound)
				elif type == "i": # Mutate the integer
					value = random.randint(lower_bound, upper_bound)
				else:
					print "Unknown gene type: ", type
				
				# Round decimals to two places.  Read up on float limitations in Python
				# for an explanation as to why we cannot simply round the value to two 
				# decimal places.  Also, check out the decimal object.
				if type == "f":
					rounded_val = "%.3f" % value
					#print rounded_val, value
					#raw_input("")
					new_genes.append("(" + rounded_val + "*" + str(lower_bound) + "*" + str(upper_bound) + "*" + str(type) + ")")
				else:
					new_genes.append("(" + str(value) + "*" + str(lower_bound) + "*" + str(upper_bound) + "*" + str(type) + ")")
			else:
				new_genes.append(gene)
		self.genes = new_genes
					
	# Test for intra-chromosome swappability
	def Intra_Swappable(self):
		return self.swappable
	
	# Format the chromosome as a string
	def To_String(self):
		chrom_str = ""
		count = 1
		for gene in self.genes:
			gene = gene.split("*")
			gene[0] = gene[0].strip("(")
			chrom_str = chrom_str + str(gene[0])
			if count != len(self.genes):
				chrom_str = chrom_str + " , "
			count = count + 1
		return chrom_str
		
"""
	Testing
"""
def main():
		tester = Chromosome([1,2,3],"CC",False)
		tester.Print()

if __name__ == "__main__":
    main()