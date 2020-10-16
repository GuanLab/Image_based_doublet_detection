

## train 5 models
#python train/train_50_50_50.py train --dataset='../data/left_out_1_2/model1/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model1/logs/'
#echo "finish model1"
#python train/train_50_50_50.py train --dataset='../data/left_out_1_2/model2/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model2/logs/'
#echo "finish model2"
#python train/train_50_50_50.py train --dataset='../data/left_out_1_2/model3/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model3/logs/'
#echo "finish model3"
#python train/train_50_50_50.py train --dataset='../data/left_out_1_2/model4/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model4/logs/'
#echo "finish model4"
#python train/train_50_50_50.py train --dataset='../data/left_out_1_2/model5/' --subset="train" --weights=imagenet --logs='../results/left_out_1_2/model5/logs/'
#echo "finish model5"
## make prediction
dir=$(ls -l ../results/left_out_1_2/model1/logs/ |awk '/^d/ {print $NF}')
echo $dir
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='detect_model1' --weights="../results/left_out_1_2/model1/logs/${dir}/mask_rcnn_sci_0150.h5"
#echo "finish model1 detecting"

## get final prediction by majority voting


