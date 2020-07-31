eval=function(image){
    library(stringr)
    library(caret)
    library(e1071)
    library(pROC)

    #pred_path=paste('/local/disk3/mqzhou/single_cell_image/mask_rcnn_cell_machine/sci_2class/results/',train,'/',sep='')
    pred_path='/local/disk3/mqzhou/single_cell_image/mask_rcnn_cell_machine/sci_2class/results/'
    pred1=read.csv(paste(pred_path,image,'_model1/pred.csv',sep=''),header=T)
    pred2=read.csv(paste(pred_path,image,'_model2/pred.csv',sep=''),header=T)
    pred3=read.csv(paste(pred_path,image,'_model3/pred.csv',sep=''),header=T)
    pred4=read.csv(paste(pred_path,image,'_model4/pred.csv',sep=''),header=T)
    pred5=read.csv(paste(pred_path,image,'_model5/pred.csv',sep=''),header=T)

    target=read.csv(paste('/local/disk3/mqzhou/single_cell_image/target/',image,'_target.csv',sep=''),header=T)
    target[1]=lapply(target[1],as.character)
    target=target[order(target[,1]),]
    target[,1]=tolower(target[,1])

    order_pred=function(pred){
    	pred[1]=lapply(pred[1],as.character)
        pred=pred[order(pred[,1]),]
        return(pred)
    }

    vote_pred_binary=function(pred_list){#binary label: true(doublet)/false
        vote_num=length(pred_list)
        pred_len=dim(pred_list[[1]])[1]
        pred=c()
        for (i in 1:pred_len){
            num_true=0
            num_false=0
            for (j in 1:vote_num){
                pp=pred_list[[j]][i,2]
                if (pp>1){#double
                    num_true=num_true+1
                }
                else{
                    num_false=num_false+1
                }
            }
            if (num_true>num_false){
               pred=c(pred,TRUE)
            }
            else{
               pred=c(pred,FALSE)
            }
        }
        return(pred)
    }

    vote_pred_3class=function(pred_list){#3 class label: doublet/singlet/missing
    	vote_num=length(pred_list)
    	pred_len=dim(pred_list[[1]])[1]
    	pred=c()
    	for (i in 1:pred_len){
    		num_true=0
    		num_false=0
            num_missing=0
    		for (j in 1:vote_num){
    			pp=pred_list[[j]][i,2]
    			if (pp>1){#double
    				num_true=num_true+1
    			}
    			else if (pp==1){
    				num_false=num_false+1
    			}
                else {num_missing=num_missing+1}
    		}
            p_index=which.max(c(num_true,num_false,num_missing))
            p_label=c('doublet','singlet','missing')
            pred=c(pred,p_label[p_index])
    	}
    	return(pred)
    }

    pred1=order_pred(pred1)
    pred2=order_pred(pred2)
    pred3=order_pred(pred3)
    pred4=order_pred(pred4)
    pred5=order_pred(pred5)
    pred_list=list(pred1,pred2,pred3,pred4,pred5)
    #pred_vote_binary=vote_pred_binary(pred_list)
    pred_vote_3class=vote_pred_3class(pred_list)
    ## save final prediction
    #final_pred_binary=data.frame(ImamgeId=pred1[,1],pred=pred_vote_binary)
    final_pred_3class=data.frame(ImageId=pred1[,1],pred=pred_vote_3class)
   # write.csv(final_pred_binary,paste('/local/disk3/mqzhou/single_cell_image/prediction/',image,'_vote_binary.csv',sep=''),row.names=FALSE)
    write.csv(final_pred_3class,paste('/local/disk3/mqzhou/single_cell_image/prediction/',image,'_vote_3class.csv',sep=''),row.names=FALSE)

    convert_target_3class=function(num){
        new=c()
        for (i in 1:length(num)){
            if (num[i]==0){new=c(new,'missing')}
            else if (num[i]==1){new=c(new,'singlet')}
            else{new=c(new,'doublet')}
        }
        return(new)
    }

    confusion_matrix=function(target,pred){
        u=union(target,pred)
        xtab=table(factor(pred,u),factor(target,u))
        print(confusionMatrix(xtab))
    }

   # # binary label
   # print(paste('Binary label for',image,'!'))
   # target_binary=target[,2]>1#true if double
   # print('Keep missing:')
   # confusion_matrix(target_binary,pred_vote_binary)
   # print('Remove missing')
   # index=target[,2]==0
   # confusion_matrix(target_binary[!(index)],pred_vote_binary[!(index)])
    
   # # save predict wrong index after rm
   # ids=target[!(index),1]
   # w_index=as.character(pred_vote_binary[!(index)])!=target_binary[!(index)]
   # wrong_pred_id=ids[w_index]
   # wrong=data.frame(ids=wrong_pred_id,pred1=pred1[!(index),][w_index,2],pred2=pred2[!(index),][w_index,2],
   #             pred3=pred3[!(index),][w_index,2],pred4=pred4[!(index),][w_index,2],pred5=pred5[!(index),][w_index,2],
   #            pred=pred_vote_binary[!(index)][w_index],target=target[!(index),][w_index,2],target_b=target_binary[!(index)][w_index])
   # write.csv(wrong,paste('/local/disk3/mqzhou/single_cell_image/prediction/pred_rm_missing_wrong_index/',image,'_vote_pred_wrong.csv',sep=''),row.names=FALSE)

    # 3 class label
     print(paste('3 class label for',image,'!'))
     target_3class=convert_target_3class(target[,2])
     print('Keep missing:')
     confusion_matrix(target_3class,pred_vote_3class)
     print('Remove missing')
     index=target[,2]==0
     confusion_matrix(target_3class[!(index)],pred_vote_3class[!(index)])
    # save predic wrong index
     ids=target[,1]
     w_index=as.character(pred_vote_3class)!=target_3class
     wrong_pred_id=ids[w_index]
     wrong=data.frame(ids=wrong_pred_id,pred1=pred1[w_index,2],pred2=pred2[w_index,2],
                pred3=pred3[w_index,2],pred4=pred4[w_index,2],pred5=pred5[w_index,2],
               pred=pred_vote_3class[w_index],target=target[w_index,2],target_3class=target_3class[w_index])
    write.csv(wrong,paste('/local/disk3/mqzhou/single_cell_image/evaluation/pred_rm_missing_wrong_index/',image,'_vote_3class_pred_wrong.csv',sep=''),row.names=FALSE)


    #train_dir='/local/disk3/mqzhou/single_cell_image/mask_rcnn_cell_machine/image_labeled/'
    #train_ids=list.files(train_dir,pattern=paste(str_to_title(image),'_',sep=''))
    #train_ids=tolower(unlist(strsplit(train_ids,'.png')))
    #test_ids=setdiff(target[,1],train_ids)#exclude training from the whole image
    #get_test_index=function(test_ids,target_name){
    #  inds=c()
    #  for (i in test_ids){
    #    ind=which(target_name==i)
    #    inds=c(inds,ind)
    #  }
    #  return(inds)
    #}
    #test_index=get_test_index(test_ids,target[,1])
    #accuracy=sum(pred_vote[test_index]==target_binary[test_index])/length(test_index)
    #print(paste('accuracy for',image,'is',accuracy))
    #index=target[test_index,2]==0
    #accuracy_delete=sum((pred_vote[test_index][!(index)])==target_binary[test_index][!(index)])/(length(test_index)-length(which(index)))# 0.9426049(cutoff 0.5)
    #print(paste('accuracy for',image,'with deleting missing is',accuracy_delete))

}

sink('/local/disk3/mqzhou/single_cell_image/prediction/pred_vote_3class_stats.txt')
eval('image1')
eval('image2')
eval('image3')
eval('image5')
eval('image6')
eval('image7')
eval('image8')
eval('image9')
eval('image10')
eval('image11')
sink()


