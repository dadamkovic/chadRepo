#!/usr/bin/env python3

import subprocess
import sys
import os


## Will read file
def installRequirements(req_file="requirements.txt"):
	with open(req_file,"r") as fr:

			package = fr.readline().rstrip('\n')
			while(package != ''):

				try:
					subprocess.check_call([sys.executable, "-m", "pip", "install", package])
				except subprocess.CalledProcessError as exc:
					print("A package "+package+" was not installed!")
				package = fr.readline().rstrip('\n')

if __name__ == "__main__":

	req_file = ''
	if(len(sys.argv) > 1 ):
		req_file = sys.argv[1]
		installRequirements(req_file)
	else:
		installRequirements()
