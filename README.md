# **OCR-opt-code-1**  
## OCR全字段识别项目模型优化核心代码  
### RetinaNet基础网络Resnet添加注意力机制  
CBAMcode文件夹内存放了引入注意力机制的Resnet50，通道注意力和空间注意力机制分别用两个类去表示，并加入HightBlock  
### 边框回归模型  
bbox_regress内存放的是边框回归的代码，是jupyter notebook版本的，一共就6层，主干都在构建网络结构部分（前面的都是一些数据准备的cell）

