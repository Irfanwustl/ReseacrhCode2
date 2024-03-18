import time
import os
import sys
import numpy as np 

input_file_name=sys.argv[1] ## should be sorted

out_director=sys.argv[2]

out_file_name=out_director+"/"+os.path.basename(input_file_name)+"_std"


with open (input_file_name) as f:
	with open (out_file_name,'w') as outputfile:
		
		line=f.readline()
		if line:
			if line.strip():
				str_list=line.split()
				current_chr=str_list[4]
				current_start=str_list[5]
				current_end=str_list[6]
				val=float(str_list[3])
				current_list=[]
				current_list.append(val)
				while True:
					line=f.readline()
					if line:
						if line.strip():
							new_str_list=line.split()
							new_chr=new_str_list[4]
							new_start=new_str_list[5]
							new_end=new_str_list[6]
							new_val=float(new_str_list[3])

							if new_chr==current_chr and new_start==current_start and new_end==current_end :
								current_list.append(new_val)
							else:
								std=np.std(current_list)
								
								str_to_write=current_chr+":"+current_start+"-"+current_end+"\t"+str(std)+"\t"+str(len(current_list))+"\n"
								outputfile.write(str_to_write)

								current_chr=new_chr
								current_start=new_start
								current_end=new_end

								current_list=[]
								current_list.append(new_val)
					else:

						std=np.std(current_list)
						str_to_write=current_chr+":"+current_start+"-"+current_end+"\t"+str(std)+"\t"+str(len(current_list))+"\n"
						outputfile.write(str_to_write)
						break





				


		





