#!/usr/bin/env python
## This code can demultiplex the expression data (fastq).
## Each original sample expression corresponding to one column,
## and each one contains 40 rows data. This code can split them 
## thus one expression data corresponding to one image(column i and row j).
## use: python demutiplex.py "C1-SUM149-H1975"
import os
import sys

image=sys.argv[1]#'C1-SUM149-H1975'
sample_path='/local/disk3/mqzhou/single_cell_image/expression/'+image+'/azizi/'
result_path='/local/disk3/mqzhou/single_cell_image/expression/'+image+'/split/'
if not os.path.exists(result_path):
    os.makedirs(result_path)

for root, dirs, files in os.walk(sample_path):
    for dir in dirs:
        in_path=sample_path+dir+'/'
        out_path=result_path+dir+'/'
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        print(in_path)
        print(out_path)
        os.system("perl mRNASeqHT_demultiplex.pl -i "+in_path+" -o "+out_path)




