# **OCR-opt-code-1**  
## OCR全字段识别项目模型优化核心代码  
### 1.RetinaNet基础网络Resnet添加注意力机制  
CBAMcode文件夹内存放了引入注意力机制的Resnet50，通道注意力和空间注意力机制分别用两个类去表示，并加入HightBlock  
### 2.阿里和百度测试接口代码和结果
baidu_ali_test_code_and_result文件夹内code内存放的是调用百度和阿里OCR能力接口的代码，result是最近测试的两次数据的结果，第二次测试的仅包含百度和阿里结果（不含地址字段）
#### 第一次测试（113张）：

![test1_result](https://github.com/liuan0803/OCR-opt-code-1/blob/master/baidu_ali_test_code_and_result/result/1.png)

#### 第二次测试（102张）：

![test2_result](https://github.com/liuan0803/OCR-opt-code-1/blob/master/baidu_ali_test_code_and_result/result/2.png)


### 3.边框回归模型  
bbox_regress内存放的是边框回归的代码，是jupyter notebook版本的，一共就6层，主干都在构建网络结构部分（前面的都是一些数据准备的cell）

