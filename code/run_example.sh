#### run the example

# ## train 5 models, left out image 1 and image 2 as test sets
python train/train_50_50_50.py train --dataset='/data/example/left_out_1_2/model1/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model1/logs/'
python train/train_50_50_50.py train --dataset='/data/example/left_out_1_2/model2/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model2/logs/'
python train/train_50_50_50.py train --dataset='/data/example/left_out_1_2/model3/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model3/logs/'
python train/train_50_50_50.py train --dataset='/data/example/left_out_1_2/model4/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model4/logs/'
python train/train_50_50_50.py train --dataset='/data/example/left_out_1_2/model5/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model5/logs/'


# ## make predictions on image1
dir1=$(ls -l ../results/left_out_1_2/model1/logs/ |awk '/^d/ {print $NF}')
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model1' --weights="../results/left_out_1_2/model1/logs/${dir1}/mask_rcnn_sci_0150.h5"

dir2=$(ls -l ../results/left_out_1_2/model2/logs/ |awk '/^d/ {print $NF}')
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model2' --weights="../results/left_out_1_2/model2/logs/${dir2}/mask_rcnn_sci_0150.h5"

dir3=$(ls -l ../results/left_out_1_2/model3/logs/ |awk '/^d/ {print $NF}')
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model3' --weights="../results/left_out_1_2/model3/logs/${dir3}/mask_rcnn_sci_0150.h5"

dir4=$(ls -l ../results/left_out_1_2/model4/logs/ |awk '/^d/ {print $NF}')
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model4' --weights="../results/left_out_1_2/model4/logs/${dir4}/mask_rcnn_sci_0150.h5"

dir5=$(ls -l ../results/left_out_1_2/model5/logs/ |awk '/^d/ {print $NF}')
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model5' --weights="../results/left_out_1_2/model5/logs/${dir5}/mask_rcnn_sci_0150.h5"


# ## get final prediction by majority voting
Rscript get_final_pred_vote.R image1




