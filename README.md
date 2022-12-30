# PDF-caption

# PDF阅卷小助手

由于疫情的影响，越来越多的考试在家进行。学生把自己的试卷做完后拍照放在pdf或word里发给老师，老师就有了很重的阅卷任务。

阅卷的过程种需要不断重复打开、关闭PDF，再添加标签如得分等，因此我制作这个小工具免去了重复打开的繁琐过程。

软件自动依次打开文件夹下所有PDF，我们只需要专注于批阅，双击想要插入数字的位置，输入数字即可完成得分的标记。

所有文件标记完成后，还会自动生成一个得分的csv文件，以便后续的成绩处理。

这个脚本有些类似制作训练集的数据标注过程。

## 创建虚拟环境 && 安装依赖

没有什么版本要求

测试版本为`python 3.8.10`, 老版本也用过，具体忘记了

- opencv-python
- pdf2image
- numpy
- pillow

Cygwin && zsh 创建并加载python虚拟环境
```bash
# Cygwin && zsh
# A little difference for other shells (bash or cmd)
python -m venv venv
source venv/Scripts/activate
```

Windows cmd 创建并加载python虚拟环境
```bash
# Windows cmd
# A little difference for other shells (bash or cmd)
python -m venv venv
venv\Scripts\activate.bat
```

```bash
git clone https://github.com/cjhonlyone/PDF-caption.git
cd PDF-caption
# Remember to upgrade your pip, or opencv-python may install failed
# python -m pip install --upgrade pip
pip install -r requirements.txt
```


## 特点

- 自动依次打开当前目录下所有pdf
- 双击鼠标左键，敲键盘输入一位数字
- 数字会被标记，并且在out子目录下重新生成一个新的pdf
- 同时数字会写入一个txt，可以改名为csv然后用表格打开
- 不必批阅一份卷子就在腾讯文档上输入分数

## 操作说明

```
$ python readpdf.py
输入从第几个文件开始：
```

输入想要开始打分的pdf序号，序号按名称排列

- 从第1个开始，输入1，回车
- 从第10个开始，输入10，回车

标记过程中

- 鼠标**双击**标记位置，输入**一位**数字标记小分
- 鼠标**双击**总分位置，按q标记总分
- 回车->下一页
- a->逆时针旋转图片
- d->顺时针旋转图片
- ESC->退出当前标记

## 注意

1. **键入数字的顺序和写入txt的顺序一样，需要按题号先后标数字**

1. 没有考虑两位数得分，处理方法：

    - 分值最大为两位数的，一律依次标注两个数字
    - 如得分7，输入0，再输入7
    - 如得分18，输入1，再输入8
    - 之后用表格合并一下这两列再转换为数字

1. 程序需要放在pdf所在的目录下

1. 中途输错了可以ESC退出，不影响之前的标记

1. 由于有些pdf比较大，打开需要数秒，耐心等待


## 存在问题

PDF需要缩放为宽1200的图片，此时如果高小于700，则不能填满一阵个绘图窗口，因此会报错并退出。

暂时还无法解决，万幸出现的概率比较低。