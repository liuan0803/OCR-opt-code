#显示图片
def plt_bboxes(img,  ratio, bboxes, figsize=(10,10), linewidth=1.5):
    """Visualize bounding boxes. Largely inspired by SSD-MXNET!
    """
    fig = plt.figure(figsize=figsize)
    plt.imshow(img)
    height = img.shape[0]
    width = img.shape[1]
    colors = dict()
    cls_id = 0
    if cls_id not in colors:
        colors[cls_id] = (random.random(), random.random(), random.random())
        print(colors)
    ymin = int(bboxes[0][0][0] /ratio[0])
    xmin = int(bboxes[0][0][1] /ratio[1])
    ymax = int(bboxes[0][0][2] /ratio[0])
    xmax = int(bboxes[0][0][3] /ratio[1])
    print(ymin, xmin, ymax, xmax)
    rect = plt.Rectangle((xmin, ymin), xmax - xmin,
                                 ymax - ymin, fill=False,
                                 edgecolor=colors[cls_id],
                                 linewidth=linewidth)
    plt.gca().add_patch(rect)
    #plt.gca().text(xmin, ymin - 2,
         #                  '{:s} | {:.3f}'.format(class_name, score),
        #                   bbox=dict(facecolor=colors[cls_id], alpha=0.5),
         #                  fontsize=12, color='white')
    plt.show()

#测试pb
# pb

import tensorflow as tf
import matplotlib.pyplot as plt
import random
import os
import time
import cv2
import numpy as np

# 设置可见GPU
gpu_no = '3' # or '1'
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_no
#定义TensorFlow配置
config = tf.ConfigProto()
#配置GPU内存分配方式
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.3


test_img_path = '/data/liuan/jupyter/root/project/keras-retinanet-master/bbox_fz_zc_006000new/dataset/zc_fz_testdata_from_traindata_199/'
# pb_model_path = '/data/liuan/jupyter/root/project/keras-retinanet-master/bbox_fz_zc_006000new/bbox_pb_model1/ocr_bbox_batch16_epoch_3149_train_acc4.0234375val_acc0.7907986111111112.pb'
# pb_model_path = '/data/liuan/jupyter/root/project/keras-retinanet-master/bbox_fz_zc_006000new/bbox_pb_model1/ocr_bbox_batch16_epoch_3938_train_acc3.7769097222222223val_acc0.7907986111111112.pb'
pb_model_path = '/data/liuan/jupyter/root/project/keras-retinanet-master/bbox_fz_zc_006000new/bbox_pb_model1/ocr_bbox_batch16_epoch_5914_train_acc4.047743055555555val_acc0.7986111111111112.pb'
test_img_list = os.listdir(test_img_path)

h=48
w=192  #归一化的尺寸
c=3   #通道


with tf.Graph().as_default():
    output_graph_def = tf.GraphDef()
    with open(pb_model_path, "rb") as f:
        output_graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(output_graph_def, name="")
    with tf.Session(config=config) as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        input_x = sess.graph.get_tensor_by_name("x:0")
        print(input_x)
        output_coor = sess.graph.get_tensor_by_name("fc/Relu:0")
        print(output_coor)
        prob = sess.graph.get_tensor_by_name("keep_prob:0")
        for image_name in test_img_list:
            image_path = os.path.join(test_img_path,image_name)
            print(image_path)
            start_time = time.time()
            img = cv2.imread(image_path)
            image= cv2.resize(img,(w,h))
     
            np_image = np.asarray(image,np.float32)
            np_image_resize = np.reshape(np_image,(1,h,w,3))
            time_consuming_1 = time.time() - start_time
            start_time_2 =  time.time()
            _output_coor = sess.run([ output_coor], feed_dict={input_x:np_image_resize, prob:0})
            time_consuming_2 = time.time() - start_time_2
            
            ratio = np.array([image.shape[0]/img.shape[0], image.shape[1]/img.shape[1]],np.float32) #height缩放比 ,width 缩放比
            print(ratio)
            plt_bboxes(img,  ratio, _output_coor, figsize=(10,10), linewidth=1.5)
            print(time_consuming_1,time_consuming_2)