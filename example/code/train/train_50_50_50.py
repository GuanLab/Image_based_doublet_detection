"""
Mask R-CNN
Train on the nuclei segmentation dataset from the
Kaggle 2018 Data Science Bowl
https://www.kaggle.com/c/data-science-bowl-2018/

Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla

------------------------------------------------------------

Usage: import the module (see Jupyter notebooks for examples), or run from
       the command line as such:

    # Train a new model starting from ImageNet weights
    python3 nucleus.py train --dataset=/path/to/dataset --subset=train --weights=imagenet

    # Train a new model starting from specific weights file
    python3 nucleus.py train --dataset=/path/to/dataset --subset=train --weights=/path/to/weights.h5

    # Resume training a model that you had trained earlier
    python3 nucleus.py train --dataset=/path/to/dataset --subset=train --weights=last

    # Generate submission file
    python3 nucleus.py detect --dataset=/path/to/dataset --subset=train --weights=<last or /path/to/weights.h5>
"""

# Set matplotlib backend
# This has to be done before other importa that might
# set it, but only if we're running in script mode
# rather than being imported.
if __name__ == '__main__':
    import matplotlib
    # Agg backend runs without a display
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

import os
import sys
import json
import datetime
import numpy as np
import skimage
import imgaug
import cv2

# Root directory of the project
#ROOT_DIR = os.path.abspath("/local/disk3/mqzhou/single_cell_image/mask_rcnn_cell_machine/sci_2class/")
#ROOT_DIR= os.path.abspath ("../code/")
# Import Mask RCNN
sys.path.append('../code/train/')  # To find local version of the library
from mrcnn.config import Config
from mrcnn import utils
from mrcnn import model as modellib
from mrcnn import visualize

#config = tf.ConfigProto()
#config.gpu_options.per_process_gpu_memory_fraction = 0.45
#set_session(tf.Session(config=config))

# Path to trained weights file
#COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
#DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
DEFAULT_LOGS_DIR = "../results/logs/"
# Results directory
# Save submission files here
#RESULTS_DIR = os.path.join(ROOT_DIR, "results/")
RESULTS_DIR = "../results/"
############################################################
#  Configurations
############################################################

class SciConfig(Config):
    """Configuration for training on the nucleus segmentation dataset."""
    # Give the configuration a recognizable name
    NAME = "sci"

    # Adjust depending on your GPU memory
    IMAGES_PER_GPU = 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 2  # Background + cell+instrument

    # Number of training and validation steps per epoch
    STEPS_PER_EPOCH = 100
    #STEPS_PER_EPOCH = (657 - len(VAL_IMAGE_IDS)) // IMAGES_PER_GPU
   # VALIDATION_STEPS = max(1, len(VAL_IMAGE_IDS) // IMAGES_PER_GPU)

    # Don't exclude based on confidence. Since we have two classes
    # then 0.5 is the minimum anyway as it picks between nucleus and BG
    DETECTION_MIN_CONFIDENCE = 0

    # Backbone network architecture
    # Supported values are: resnet50, resnet101
    BACKBONE = "resnet50"

    # Input image resizing
    # Random crops of size 512x512
    IMAGE_RESIZE_MODE = "crop"
    IMAGE_MIN_DIM = 320
    IMAGE_MAX_DIM = 320
    IMAGE_MIN_SCALE = 2.0

    # Length of square anchor side in pixels
    RPN_ANCHOR_SCALES = (8, 16, 32, 64, 128)

    # ROIs kept after non-maximum supression (training and inference)
    POST_NMS_ROIS_TRAINING = 1000
    POST_NMS_ROIS_INFERENCE = 2000

    # Non-max suppression threshold to filter RPN proposals.
    # You can increase this during training to generate more propsals.
    RPN_NMS_THRESHOLD = 0.9

    # How many anchors per image to use for RPN training
    RPN_TRAIN_ANCHORS_PER_IMAGE = 64

    # Image mean (RGB)
    MEAN_PIXEL = np.array([43.53, 39.56, 48.22])

    # If enabled, resizes instance masks to a smaller size to reduce
    # memory load. Recommended when using high-resolution images.
    USE_MINI_MASK = True
    MINI_MASK_SHAPE = (224, 224)  # (height, width) of the mini-mask
    MINI_MASK_SHAPE = (3, 3)  # (height, width) of the mini-mask

    # Number of ROIs per image to feed to classifier/mask heads
    # The Mask RCNN paper uses 512 but often the RPN doesn't generate
    # enough positive proposals to fill this and keep a positive:negative
    # ratio of 1:3. You can increase the number of proposals by adjusting
    # the RPN NMS threshold.
    TRAIN_ROIS_PER_IMAGE = 128

    # Maximum number of ground truth instances to use in one image
    MAX_GT_INSTANCES = 10

    # Max number of final detections per image
    DETECTION_MAX_INSTANCES = 10


class SciInferenceConfig(SciConfig):
    # Set batch size to 1 to run one image at a time
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    # Don't resize imager for inferencing
    IMAGE_RESIZE_MODE = "pad64"
    # Non-max suppression threshold to filter RPN proposals.
    # You can increase this during training to generate more propsals.
    RPN_NMS_THRESHOLD = 0.7


############################################################
#  Dataset
############################################################

class SciDataset(utils.Dataset):

    def load_sci(self, dataset_dir, subset):
        """Load a subset of the nuclei dataset.

        dataset_dir: Root directory of the dataset
        subset: Subset to load. Either the name of the sub-directory,
                such as stage1_train, stage1_test, ...etc. or, one of:
                * train: stage1_train excluding validation images
                * val: validation images from VAL_IMAGE_IDS
        """
        # Add classes. We have one class.
        # Naming the dataset nucleus, and the class nucleus
        self.add_class("sci", 1, "cell")
        self.add_class("sci", 2, "machine")
     

        # Which subset?
        # "val": use hard-coded list above
        # "train": use data from stage1_train minus the hard-coded list above
        # else: use the data from the specified sub-directory
        #assert subset in ["train", "val", "stage1_train", "stage1_test", "stage2_test"]
        assert subset in ["train", "val", "test"]
        dataset_dir = os.path.join(dataset_dir, subset)
        image_ids = next(os.walk(dataset_dir))[1]

        # if subset == "val":
        #     image_ids = next(os.walk(dataset_dir))[1]
        # else:
        #     # Get image ids from directory names
        #     image_ids = next(os.walk(dataset_dir))[1]
        #     if subset == "train":
        #         image_ids = list(set(image_ids) - set(VAL_IMAGE_IDS))
        #         #image_ids=set(image_ids) - set(VAL_IMAGE_IDS)
        
        # Add images
        for image_id in image_ids:
            self.add_image(
                "sci",
                image_id=image_id,
                path=os.path.join(dataset_dir, image_id, "image/{}.png".format(image_id)))
                #path=os.path.join(dataset_dir, image_id))

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        info = self.image_info[image_id]
        # Get mask directory from image path
        mask_dir = os.path.join(os.path.dirname(os.path.dirname(info['path'])), "mask")
        mask_ids=next(os.walk(mask_dir))[2]
        # Read mask files from .png image
        mask = []
        class_ids=[]
        for f in mask_ids:
            if f.endswith(".png"):
                m=skimage.io.imread(os.path.join(mask_dir, f))
               # m = skimage.color.rgb2gray(skimage.io.imread(os.path.join(mask_dir, f)))
               # m=m.reshape(m.shape[0],m.shape[1],1)
                #print('load_mask:',m.shape)
                m=m.astype(np.bool)
               # .astype(np.bool)
                mask.append(m)
                if f.startswith("cell"):
                    class_ids.append(1)
                else:
                    class_ids.append(2)
        mask=np.asarray(mask)
       # print(mask.shape)
        mask = np.stack(mask, axis=-1)
        class_ids=np.asarray(class_ids)
        class_ids = class_ids.astype(int)
        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID, we return an array of ones
        return mask, class_ids

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "sci":
            return info["id"]
        else:
            super(self.__class__, self).image_reference(image_id)


############################################################
#  Training
############################################################

def train(model, dataset_dir, subset):
    """Train the model."""
    # Training dataset.
    dataset_train = SciDataset()
    dataset_train.load_sci(dataset_dir, subset)
    dataset_train.prepare()

    # Validation dataset
    dataset_val = SciDataset()
    dataset_val.load_sci(dataset_dir, "val")
    dataset_val.prepare()

    # Image augmentation
    # http://imgaug.readthedocs.io/en/latest/source/augmenters.html
    augmentation = imgaug.augmenters.Fliplr(0.5)


    # *** This training schedule is an example. Update to your needs ***

    # If starting from imagenet, train heads only for a bit
    # since they have random weights
    print("Train network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=50,
                augmentation=augmentation,
                layers='heads')
    print("Fine tune Resnet stage 4 and up")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=100, ## HERE the epochs are accumulated epochs!
                layers='4+',
                augmentation=augmentation)

    print("Train all layers")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=150,
                augmentation=augmentation,
                layers='all')


############################################################
#  RLE Encoding
############################################################

def rle_encode(mask):
    """Encodes a mask in Run Length Encoding (RLE).
    Returns a string of space-separated values.
    """
    assert mask.ndim == 2, "Mask must be of shape [Height, Width]"
    # Flatten it column wise
    m = mask.T.flatten()
    # Compute gradient. Equals 1 or -1 at transition points
    g = np.diff(np.concatenate([[0], m, [0]]), n=1)
    # 1-based indicies of transition points (where gradient != 0)
    rle = np.where(g != 0)[0].reshape([-1, 2]) + 1
    # Convert second index in each pair to lenth
    rle[:, 1] = rle[:, 1] - rle[:, 0]
    return " ".join(map(str, rle.flatten()))


def rle_decode(rle, shape):
    """Decodes an RLE encoded list of space separated
    numbers and returns a binary mask."""
    rle = list(map(int, rle.split()))
    rle = np.array(rle, dtype=np.int32).reshape([-1, 2])
    rle[:, 1] += rle[:, 0]
    rle -= 1
    mask = np.zeros([shape[0] * shape[1]], np.bool)
    for s, e in rle:
        assert 0 <= s < mask.shape[0]
        assert 1 <= e <= mask.shape[0], "shape: {}  s {}  e {}".format(shape, s, e)
        mask[s:e] = 1
    # Reshape and transpose
    mask = mask.reshape([shape[1], shape[0]]).T
    return mask


def mask_to_rle(image_id, mask, scores):
    "Encodes instance masks to submission format."
    assert mask.ndim == 3, "Mask must be [H, W, count]"
    # If mask is empty, return line with image ID only
    if mask.shape[-1] == 0:
        return "{},".format(image_id)
    # Remove mask overlaps
    # Multiply each instance mask by its score order
    # then take the maximum across the last dimension
    order = np.argsort(scores)[::-1] + 1  # 1-based descending
    mask = np.max(mask * np.reshape(order, [1, 1, -1]), -1)
    # Loop over instance masks
    lines = []
    for o in order:
        m = np.where(mask == o, 1, 0)
        # Skip if empty
        if m.sum() == 0.0:
            continue
        rle = rle_encode(m)
        lines.append("{}, {}".format(image_id, rle))
    return "\n".join(lines)


############################################################
#  Detection
############################################################

def detect(model, dataset_dir, subset, submit_name):
    """Run detection on images in the given directory."""
    print("Running on {}".format(dataset_dir))

    # Create directory
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    #submit_dir = "submit_{:%Y%m%dT%H%M%S}".format(datetime.datetime.now())
    #submit_dir = os.path.join(RESULTS_DIR, submit_dir)
    submit_dir = os.path.join(RESULTS_DIR, submit_name)
    
    if not os.path.exists(submit_dir):
        os.makedirs(submit_dir)
    
    #mask_dir=os.path.join(submit_dir,"masks")
    #os.makedirs(mask_dir)
    #os.system('mkdir '+submit_dir+'/masks')#path to store masks
    # Read dataset
    dataset = SciDataset()
    dataset.load_sci(dataset_dir, subset)
    dataset.prepare()
    # Load over images
    submission = []
    num_cells = []
    for image_id in dataset.image_ids:
        # Load image and run detection
        image = dataset.load_image(image_id)
        # Detect objects
        r = model.detect([image], verbose=0)[0]
        # Encode image to RLE. Returns a string of multiple lines
        source_id = dataset.image_info[image_id]["id"]
        rle = mask_to_rle(source_id, r["masks"], r["scores"])
        submission.append(rle)
        # select the machine with maximum score and cells within the machine
        boxes_all=r['rois']
        class_ids_all=r['class_ids']
        scores_all=r['scores']
        class2_ids=np.where(class_ids_all==2)[0]
        class1_ids=np.where(class_ids_all==1)[0]
        scores2=scores_all[class2_ids]
        index_display=[]
        index=[]##index for cells within machine
        for id1 in class1_ids:
            box1=boxes_all[id1,:]
            #print('box1:',box1)
            is_within_machine = False#cell is within at least one machine
            for id2 in class2_ids:
                box_machine=boxes_all[id2,:]
                #print('box_machine:',box_machine)
                if box1[0] >= box_machine[0] and box1[1] >= box_machine[1]:
                    if box1[2] <= box_machine[2] and box1[3] <= box_machine[3]:
                        is_within_machine=True
                        index_display.append(id2)
            if is_within_machine and scores_all[id1] > 0.5:#if within machine and score > 0.5
                index.append(id1)
            index_display=index_display+index
        num_cells.append("{}, {}".format(source_id,len(index)))
            
       # save masks
       # mask_path=os.path.join(mask_dir,dataset.image_info[image_id]["id"])
       # os.makedirs(mask_path)
       # for i in index:
       #     m=r['masks'][:,:,i]*255
       #     cv2.imwrite(mask_path+'/'+str(i)+'.png',m)
       
       # Save image with masks 
        visualize.display_instances(
            image, r['rois'][index_display,:], r['masks'][:,:,index_display], r['class_ids'][index_display],
            dataset.class_names, r['scores'][index_display],
            show_mask=False,
            title="Predictions")
       # visualize.display_instances(
       #     image, r['rois'], r['masks'], r['class_ids'],
       #     dataset.class_names, r['scores'],
       #     show_mask=False,
       #     title="Predictions")
        plt.savefig("{}/{}.png".format(submit_dir, dataset.image_info[image_id]["id"]))

    # Save to csv file
    #submission = "ImageId,EncodedPixels\n" + "\n".join(submission)
    #file_path = os.path.join(submit_dir, "submit.csv")
    #with open(file_path, "w") as f:
    #    f.write(submission)
    #print("Saved to ", submit_dir)
    
    #save prediction
    num_cells = "ImageId,NumCells\n" + "\n".join(map(str,num_cells))
    file_path = os.path.join(submit_dir, "pred.csv")
    with open(file_path, "w") as f:
        f.write(num_cells)
    print("Saved to ", submit_dir)


############################################################
#  Command Line
############################################################

if __name__ == '__main__':
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Mask R-CNN for nuclei counting and segmentation')
    parser.add_argument("command",
                        metavar="<command>",
        help="'train' or 'detect'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/dataset/",
                        help='Root directory of the dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--subset', required=False,
                        metavar="Dataset sub-directory",
                        help="Subset of dataset to run prediction on")
    parser.add_argument('--submit', required=False,
                        metavar="name of submit",
                        help='Submit folder name')
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "detect":
        assert args.subset, "Provide --subset to run prediction on"
        assert args.submit, "Provide --name of submit folder"

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)
    if args.subset:
        print("Subset: ", args.subset)
    print("Logs: ", args.logs)

    # Configurations
    if args.command == "train":
        config = SciConfig()
    else:
        config = SciInferenceConfig()
    config.display()
    
    ##debug
    backbone_shapes = modellib.compute_backbone_shapes(config, config.IMAGE_SHAPE)
    anchors = utils.generate_pyramid_anchors(config.RPN_ANCHOR_SCALES,
                                             config.RPN_ANCHOR_RATIOS,
                                             backbone_shapes,
                                             config.BACKBONE_STRIDES,
                                             config.RPN_ANCHOR_STRIDE)

    #debug
    num_levels = len(backbone_shapes)
    anchors_per_cell = len(config.RPN_ANCHOR_RATIOS)
    #print("Count: ", anchors.shape[0])
    #print("Scales: ", config.RPN_ANCHOR_SCALES)
    #print("ratios: ", config.RPN_ANCHOR_RATIOS)
    #print("Anchors per Cell: ", anchors_per_cell)
    #print("Levels: ", num_levels)

    # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config,
                                  model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)

    # Select weights file to load
    if args.weights.lower() == "coco":
        weights_path = COCO_WEIGHTS_PATH
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)
    elif args.weights.lower() == "last":
        # Find last trained weights
        weights_path = model.find_last()
    elif args.weights.lower() == "imagenet":
        # Start from ImageNet trained weights
        weights_path = model.get_imagenet_weights()
    else:
        weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # Train or evaluate
    if args.command == "train":
        train(model, args.dataset, args.subset)
    elif args.command == "detect":
        detect(model, args.dataset, args.subset, args.submit)
    else:
        print("'{}' is not recognized. "
              "Use 'train' or 'detect'".format(args.command))

