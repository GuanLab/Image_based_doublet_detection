#!/usr/bin/env python
## This code can generate gene expression data of images using kallisto.
## Useage: python image_gene_expression.py 'C1-SUM149-H1975'
import os
import sys
image=sys.argv[1]#'C1-SUM149-H1975'
reads_dir='/local/disk3/mqzhou/single_cell_image/expression/'+image+'/split/'
output_dir='/local/disk3/mqzhou/single_cell_image/expression/'+image+'/gene/'
index_dir='/local/disk3/mqzhou/single_cell_image/expression/refs/ensemblGrch38_kallisto_index'
kallisto_dir='/local/disk3/mqzhou/single_cell_image/expression/kallisto/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
for root, dirs, files in os.walk(reads_dir):
    for dir in dirs:
        read_path=reads_dir+dir+'/'#'/local/disk3/mqzhou/single_cell_image/expression/C1-XXX/split/SampleXXX/'
        for root, dirs, files in os.walk(read_path):
            for file in files:#file=114718_GTAGAGGA_S10_ROW13_R2.fastq
                if (file.split('_')[-1]=='R1.fastq'):
                    read_name='_'.join(file.split('_')[:-1])
                    read1_path=read_path+read_name+'_R1.fastq'
                    read2_path=read_path+read_name+'_R2.fastq'
                    output_path=output_dir+str('_'.join(file.split('_')[1]))+'_'+str(file.split('_')[3])+'/'#114718_GTAGAGGA_ROW13
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    os.system(kallisto_dir+"kallisto quant -i "+index_dir+" -o "+output_path+" -t 24 "+read1_path+" "+read2_path)

