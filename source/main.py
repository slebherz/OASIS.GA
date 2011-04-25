"""
	Driver for the GA
"""
import random
import operator

import individual as ind
import chromosome as chrom
import ga
import utils

def main():
	utils.Update_Console()
	testGA = ga.GA()
	testGA.Evolve()
	
if __name__ == "__main__":
    main()