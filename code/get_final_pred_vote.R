
### input: image name, e.g. image1
### output: final prediction file, confusion matrix file

eval=function(image){
    library(stringr)
    library(caret)
    library(e1071)
    library(pROC)

    pred_path='../results/'
    pred1=read.csv(paste(pred_path,image,'_model1/pred.csv',sep=''),header=T)
    pred2=read.csv(paste(pred_path,image,'_model2/pred.csv',sep=''),header=T)
    pred3=read.csv(paste(pred_path,image,'_model3/pred.csv',sep=''),header=T)
    pred4=read.csv(paste(pred_path,image,'_model4/pred.csv',sep=''),header=T)
    pred5=read.csv(paste(pred_path,image,'_model5/pred.csv',sep=''),header=T)
    
    target=read.csv(paste('../data/example/',image,'_target.csv',sep=''),header=T)
    target[1]=lapply(target[1],as.character)
    target=target[order(target[,1]),]
    target[,1]=tolower(target[,1])

    order_pred=function(pred){
    	pred[1]=lapply(pred[1],as.character)
        pred=pred[order(pred[,1]),]
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
    pred_vote_3class=vote_pred_3class(pred_list)
    
    ## save final prediction
    final_pred_3class=data.frame(ImageId=pred1[,1],pred=pred_vote_3class)
    
    write.csv(final_pred_3class,paste('../results/prediction/',image,'_vote_3class.csv',sep=''),row.names=FALSE)

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

    # 3 class label
     print(paste('3 class label for',image,'!'))
     target_3class=convert_target_3class(target[,2])
     print('Keep missing:')
     confusion_matrix(target_3class,pred_vote_3class)
     print('Remove missing')
     index=target[,2]==0
     confusion_matrix(target_3class[!(index)],pred_vote_3class[!(index)])
}

args = commandArgs(TRUE)
if (length(args)==0) {
    print('usage: Rscript get_final_pred_vote.R image1')
} else{
    dir.create(file.path('../results', 'prediction'))
    sink('../results/prediction/pred_vote_3class_stats.txt')
    eval(args[1])
    sink()
}

