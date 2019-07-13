#!/usr/bin/env python3
import argparse, shutil
import pandas as pd

from humain.common.constants import *
from humain.common.utils import *


if __name__ == '__main__':
	""" Simulated version of the regular expression Event Date extraction
	"""
	parser = argparse.ArgumentParser("Run the simulated version of the regular expression Event Date extraction.")
	parser.add_argument('-d', '--fulltext_dir', action="store", required=True, help="Directory with the fulltext transcription files of the images.")
	parser.add_argument('-f', '--regexp_file', action="store", required=True, help="File with the correspondent Event Date extracted using the regular expresion algorithm.")	
	parser.add_argument('-m', '--metric', action="append", required=False, help="One or more metrics that will be collected when running the regular expression extraction.")
	parser.add_argument('-o', '--output_dir', action="store", required=True, help="Directory where the accepted and rejected extractions will be stored.")
	#"File with (image, event_date) pairs extracted using regular expression.")
	#parser.add_argument('-u', '--unknown_file', action="store", required=True, help="File with the list of text files for which no Event Date could be extracted.")
	args = parser.parse_args()
	
	# Usage example: python3 reg_expr_dataset.py -d /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/ocr_dataset -f /home/ialzuru/Summer2019/HuMaIN_Simulator/datasets/aocr_insects/reg_exp/gc-ocr/reg_expr.tsv -m duration -o /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset
	# python3 reg_expr_dataset.py 
	# -d /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/ocr_dataset 
	# -f /home/ialzuru/Summer2019/HuMaIN_Simulator/datasets/aocr_insects/reg_exp/gc-ocr/reg_expr.tsv -m duration 
	# -o /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset

	# python3 reg_expr_dataset.py -d /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/ocr_dataset -f /home/ialzuru/Summer2019/HuMaIN_Simulator/datasets/aocr_insects/reg_exp/gc-ocr/reg_expr.tsv -m duration -a /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset/accepted.csv -u /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset/rejected.csv
	# -a /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset/accepted.csv
	# -u /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results/event_date_001/reg_expr_dataset/rejected.csv

	################################################################################################################################
	# ARGUMENTS VALIDATIONS
	################################################################################################################################

	#### INPUTS
	# args.fulltext_dir
	verify_dir( args.fulltext_dir, 'The fulltext transcription directory (' + args.fulltext_dir + ') was not found: ', parser, 1 )

	# args.regexp_file
	verify_file( args.regexp_file, 'The event dates file (' + args.regexp_file + ') was not found: ', parser, 2 )

	# args.metric
	metrics_dir = os.path.dirname( args.regexp_file )
	if len(args.metric) > 0:
		# Metric directory
		metrics_dir = metrics_dir + "/metrics"
		verify_dir( metrics_dir, 'The metrics directory was not found.', parser, 3 )
		# Metric files
		for m_name in args.metric:
			metric_file = metrics_dir + "/" + m_name + ".csv"
			verify_file( metric_file, 'The file metric ' + metric_file + ' was not found in the metrics directory.', parser, 4 )

	#### OUTPUTS
	# Output directory: args.output_dir
	verify_create_dir( args.output_dir, 'The output directory could not be created.', parser, 5 )
	# Output subdirectories for the accepted values and rejected specimens
	verify_create_dir( args.output_dir + "/accepted", 'The output directory for the accepted event date values could not be created.', parser, 6 )
	verify_create_dir( args.output_dir + "/rejected", 'The output directory for the rejected specimens could not be created.', parser, 7 )
	# Output files
	accepted_file = args.output_dir + "/accepted/accepted.tsv"
	rejected_file = args.output_dir + "/rejected/rejected.txt"
	verify_create_file( accepted_file, 'The output file, for the extracted event dates, could not be created.', parser, 8 )
	verify_create_file( rejected_file, 'The output file of rejected specimens, could not be created.', parser, 9 )
	# Metric folders
	verify_create_dir( args.output_dir + "/accepted/metrics", 'The output metrics directory for the accepted event date values could not be created.', parser, 10 )
	verify_create_dir( args.output_dir + "/rejected/metrics", 'The output metrics directory for the rejected specimens could not be created.', parser, 11 )

	################################################################################################################################
	# LOAD IN A DATAFRAME THE EXTRACTED EVENT DATE VALUES USING REGULAR EXPRESIONS
	df = pd.read_csv( args.regexp_file, sep='\t', names=['filename', 'value'] )
	df = df.fillna('')

	################################################################################################################################
	# LOAD IN DIFFERENT STRUCTURES THE ACCEPTED (WITH EVENT DATE) AND REJECTED SPECIMENS
	accepted_dict = {}
	rejected_list = []

	for index, row in df.iterrows():
		if row['value'] == '':
			rejected_list.append( row['filename'] )
		else:
			accepted_dict[ row['filename'] ] = row['value']

	################################################################################################################################
	# CREATE THE METRIC FILES
		
	# For each metric, divide the values in Accepted and Rejected
	for m_name in args.metric:
		# Loads the metric values in a dataframe
		metric_file = metrics_dir + "/" + m_name + ".csv"
		df_metric = pd.read_csv( metric_file, names=['filename', 'value'] )
		accepted_txt = ""
		rejected_txt = ""
		# Divide the metric value in Accepted and Rejected
		for index, row in df_metric.iterrows():
			if row['filename'] in accepted_dict.keys():
				accepted_txt += row['filename'] + "," + str(row['value']) + "\n"
			else:
				rejected_txt += row['filename'] + "," + str(row['value']) + "\n"

		# Create and fill the Accepted metric file
		new_metric_filename = args.output_dir + "/accepted/metrics/" + m_name + ".csv"
		with open(new_metric_filename, "w+") as f_m:
			f_m.write( accepted_txt )
		# Create and fill the Rejected metric file
		new_metric_filename = args.output_dir + "/rejected/metrics/" + m_name + ".csv"
		with open(new_metric_filename, "w+") as f_m:
			f_m.write( rejected_txt )

	################################################################################################################################
	# SAVE THE ACCEPTED VALUES AND REJECTED SPECIMENS
	
	# Accepted Values
	accepted_txt = ""
	for filename, value in accepted_dict.items(): 
		accepted_txt += filename + "\t" + value + "\n"
	with open(accepted_file, "w+") as f_a:
		f_a.write( accepted_txt )

	# Rejected Specimens
	rejected_txt = ""
	for filename in rejected_list: 
		rejected_txt += filename + "\n"
	with open(rejected_file, "w+") as f_r:
		f_r.write( rejected_txt )

	sys.exit(0)