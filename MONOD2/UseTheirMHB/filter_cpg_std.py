import time
import os
import sys


input_file_name=sys.argv[1]
out_director=sys.argv[2]
cpg_cutoff=int(sys.argv[3]) ###>=
std_cutoff=float(sys.argv[4]) ##<=

out_file_name=out_director+"/"+os.path.basename(input_file_name)


with open (input_file_name) as f:

	with open (out_file_name,'w') as outputfile:
		while True:
			line=f.readline()
			if line:
				
				if line.strip():
					str_list=line.split()
					std=float(str_list[3])
					cpg=int(str_list[4])
					if std <=std_cutoff and cpg >=cpg_cutoff:
						str_to_write=str_list[0]+"\t"+str_list[1]+"\t"+str_list[2]+"\t"+str_list[5]+"\n"
						outputfile.write(str_to_write)
			else:
				break
