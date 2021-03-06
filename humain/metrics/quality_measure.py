#!/usr/bin/env python3

##########################################################################################
# Developers: 	Icaro Alzuru and Aditi Malladi
# Project: 		HuMaIN (http://humain.acis.ufl.edu)
# Description: 	Compute the quality (similarity to the ground truth data) of the extracted 
# 				term values
##########################################################################################
# Copyright 2019    Advanced Computing and Information Systems (ACIS) Lab - UF
#                   (https://www.acis.ufl.edu/)
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file 
# except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the 
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied. See the License for the specific language governing permissions 
# and limitations under the License.
##########################################################################################

import os, sys, argparse, re
import pandas as pd
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance

from humain.utils import *


if __name__ == '__main__':
	""" Compute the quality (similarity to the ground truth data) of the extracted term values
	"""
	parser = argparse.ArgumentParser("Compute the quality (similarity to the ground truth data) of the extracted term values.")
	parser.add_argument('-a', '--accepted_file', action="append", required=True, help="One or more values files with accepted term values.")
	parser.add_argument('-g', '--ground_truth', action="store", required=True, help="Ground truth values for the Specimens' term.")
	parser.add_argument('-o', '--output_file', action="store", required=True, help="File with the Damerau-Levenshtein similarity to the ground truth data of the accepted values.")
	args = parser.parse_args()

	# Usage: python3 ./quality_measure.py -a ~/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_ds/accepted/accepted.tsv -a ~/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/consensus_ds/accepted/accepted.tsv -g ~/Summer2019/HuMaIN_Simulator/datasets/aocr_mix100/gtruth/terms/dwc_eventDate.tsv -o ~/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/quality.csv

	################################################################################################################################
	# ARGUMENTS VALIDATIONS

	# args.accepted_file
	for pathfilename in args.accepted_file:
		verify_file( pathfilename, 'The output data file (' + pathfilename + ') was not found.', parser, 1 )
	# args.ground_truth
	verify_file( args.ground_truth, 'The ground truth data file (' + args.ground_truth + ') was not found.', parser, 2 )
	# args.output_file
	verify_create_file( args.output_file, 'The output data file, for the similarity values, could not be created.', parser, 3 )

	################################################################################################################################
	# READ THE GROUND TRUTH DATA AND LOAD THEM IN A DICTIONARY
	specimen_gt_value = {}
	with open( args.ground_truth, "r") as f_gt:
		next(f_gt)
		for line in f_gt:
			line = line[:-1] 
			filename, value_gt = "", ""
			try:
				filename, value_gt = line.split("\t")
				filename = filename[:-4]
			except ValueError:
				print("\nERROR: The ground truth file does not have the (filename, value) expected format.\n")
				sys.exit(4)
			specimen_gt_value[filename] = value_gt

	################################################################################################################################
	# READ THE CANDIDATE (ACCEPTED) VALUES AND LOAD THEM IN A DICTIONARY
	candidate_value = {}
	for pathfilename in args.accepted_file:
		with open( pathfilename, "r") as f_can:
			for line in f_can:
				line = line[:-1] 
				filename, ed_value = "", ""
				try:
					filename, ed_value = line.split("\t")
					filename = filename[:-4]
				except ValueError:
					print("\nERROR: The accepted values file (" + pathfilename + ") does not have the (filename, value) expected format.\n")
					print("line: ", line)
					sys.exit(5)
				candidate_value[filename] = ed_value

	################################################################################################################################
	# COMPARISON: COMPUTATION OF THE DAMERAU-LEVENSTEIN SIMILARITY BETWEEN THE GROUND TRUTH VALUES AND THE ACCEPTED VALUES
	sim_text = ""
	pattern = re.compile('[\W_]+')
	for specimen in specimen_gt_value.keys():
		if specimen in candidate_value.keys():
			# Eliminate special characters
			clean_gt_value = pattern.sub(' ', specimen_gt_value[specimen].lower()).replace('  ', ' ').replace('  ', ' ')
			clean_candidate_value = pattern.sub(' ', candidate_value[specimen].lower()).replace('  ', ' ').replace('  ', ' ')
			sim = 1.0 - normalized_damerau_levenshtein_distance( clean_gt_value, clean_candidate_value )
			sim_text += specimen + "," + str(sim) + "\n"
		# else:
		# 	sim_text += specimen + ",0.0\n"

	################################################################################################################################
	# COMPARISON RESULTS ARE WRITTEN TO THE OUTPUT FILE
	with open(args.output_file, "w+") as f_out:
		f_out.write( sim_text )
