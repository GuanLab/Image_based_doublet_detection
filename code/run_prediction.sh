## run prediction from saved model

## make predictions on image1
python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model1' --weights="../data/model/model1/mask_rcnn_sci_0150.h5"

python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model2' --weights="../data/model/model2/mask_rcnn_sci_0150.h5"

python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model3' --weights="../data/model/model3/mask_rcnn_sci_0150.h5"

python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model4' --weights="../data/model/model4/mask_rcnn_sci_0150.h5"

python train/train_50_50_50.py detect --dataset='../data/detect/' --subset=test --submit='image1_model5' --weights="../data/model/model5/mask_rcnn_sci_0150.h5"


# ## get final prediction by majority voting
Rscript get_final_pred_vote.R image1
