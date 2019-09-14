#!/usr/bin/env python3

import argparse, shutil
import subprocess

from humain.constants import *
from humain.utils import *


if __name__ == '__main__':
	""" Get the simulated execution result from an OCR engine
	"""
	parser = argparse.ArgumentParser("Run the specified OCR engine over all the images of an specified collection.")
    # here pass the folder with the rejected images only 
	parser.add_argument('-d', '--dataset', action="store", required=True, help="Biocollection or dataset name.")
	parser.add_argument('-f', '--file', action="store", required=True, help="Rejected images to process now")
	parser.add_argument('-a', '--accepted', action="store", required=True, help="Accepted images to be removed from folder")
	parser.add_argument('-m', '--metric', action="append", required=True, help="One or more metrics that will be collected when executing the ocr.")
	parser.add_argument('-o', '--out_dir', action="store", required=True, help="Directory where the ocr transcription of the image will be stored.")
	args = parser.parse_args()
	
	# Usage example
	# python3 ~/Summer2019/HuMaIN_Simulator/humain/selfie/tasks/ocr_ds.py -e ocropus -d aocr_insects -m duration -o /home/ialzuru/Summer2019/HuMaIN_Simulator/humain/selfie/results

	# copy and create the dataset required
	# TODO: Pass the project name as well
	subprocess.call(BASE_DIR+"/selfie/tasks/move_files.sh " + args.dataset+ " "+ args.out_dir + " "+ args.accepted, shell = True)
	################################################################################################################################
	# ARGUMENTS VALIDATIONS
	################################################################################################################################

	# args.dataset
	verify_dir( args.dataset, 'The dataset directory (' + args.dataset + ') was not found: ', parser, 1 )

	# args.metric
	metrics_dir = ""
	if len(args.metric) > 0:
		# Metric directory
		metrics_dir = args.dataset + "/metrics"
		verify_dir( metrics_dir, 'The metrics directory was not found.', parser, 3 )
		# Metric files
		for m_name in args.metric:
			verify_file( metrics_dir + "/" + m_name + ".csv", 'The file metric ' + m_name + ' was not found in the metrics directory.', parser, 4 )

	# args.out_dir
	verify_create_dir( args.out_dir, 'The destination directory, for the text file, was not found and could not be created.', parser, 5 )
	output_metrics_dir = args.out_dir + "/metrics"
	verify_create_dir( output_metrics_dir, 'The destination metric directory was not found and could not be created.', parser, 6 )

	################################################################################################################################
	# COPY THE TEXT FILES TO THE EXPERIMENT'S RESULT FOLDER
	################################################################################################################################
	# Create the list of files to process
	filenames = os.listdir(args.dataset)
	filename_list = list(f for f in filenames if f.endswith('.txt'))
	print(filename_list)

	# rejected files 
	rejected_images = []
	with open(args.file, "r") as f_s:
		for line in f_s:
			rejected_images.append( line[:-1].strip() )

	try:
		pathfilename = ""
		for filename in filename_list:
			if filename in rejected_images:
				pathfilename = args.dataset + "/" + filename
				shutil.copy( pathfilename, args.out_dir)
	except (OSError, IOError):
		print('ERROR: The file ' + pathfilename + ' could not be copied to ' + args.out_dir + '.\n')
		sys.exit(8)


	################################################################################################################################
	# INSERT THE LINES WITH THE METRIC'S VALUES - FOR EACH METRIC
	################################################################################################################################	
	if len(args.metric) > 0:
		# Metric files
		for m_name in args.metric:
			metric_filename_src = metrics_dir + "/" + m_name + ".csv"
			try:
				shutil.copy( metric_filename_src, output_metrics_dir )	
			except (OSError, IOError):
				print('ERROR: The metric file ' + metric_filename_src + ' could not be found or copied to ' + output_metrics_dir + '.\n')
				sys.exit(8)

	sys.exit(0)