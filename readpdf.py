# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 00:00:36 2020

@author: CJH
"""

import cv2
import sys
import csv

import os

from pdf2image import convert_from_path
import numpy as np
#from fpdf import FPDF
from PIL import Image


import codecs

Image.MAX_IMAGE_PIXELS = 933120000

truex = 0
truey = 0

scroll_w = 16  # 滚动条宽度



def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)
#鼠标事件
def mouse(event, x, y, flags, param):
    global flag, horizontal, vertical, flag_hor, flag_ver, dx, dy, sx, sy, dst, x1, y1, x2, y2, x3, y3, f1, f2
    global zoom, scroll_har, scroll_var, img_w, img_h, img, dst1, win_w, win_h, show_w, show_h, CoordinateX, CoordinateY
    global truex,truey
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        if flag == 0:
            if horizontal and 0 < x < win_w and win_h - scroll_w < y < win_h:
                flag_hor = 1  # 鼠标在水平滚动条上
            elif vertical and win_w - scroll_w < x < win_w and 0 < y < win_h:
                flag_ver = 1  # 鼠标在垂直滚动条上
#            else:  #鼠标在图像上
#                truex = x + dx
#                truey = y + dy
#                truexy = "%d,%d" % (truex, truey)
#                CoordinateX.append(truex)
#                CoordinateY.append(truey)
#                img1 = img[dy:dy + show_h, dx:dx + show_w]  # 截取显示图片
#                cv2.circle(img1, (x, y), 1, (255, 255, 255), thickness=-1)
#                cv2.putText(img1, truexy, (x, y), cv2.FONT_HERSHEY_PLAIN,
#                            1.0, (255, 255, 255), thickness=1)
#                dst = img1.copy()

            if flag_hor or flag_ver:
                flag = 1  # 进行滚动条垂直
                x1, y1, x2, y2, x3, y3 = x, y, dx, dy, sx, sy  # 使鼠标移动距离都是相对于初始滚动条点击位置，而不是相对于上一位置
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        if flag == 1:
            if flag_hor:
                w = (x - x1)/2  # 移动宽度
                dx = x2 + w * f1  # 原图x
                if dx < 0:  # 位置矫正
                    dx = 0
                elif dx > img_w - show_w:
                    dx = img_w - show_w
                sx = x3 + w  # 滚动条x
                if sx < 0:  # 位置矫正
                    sx = 0
                elif sx > win_w - scroll_har:
                    sx = win_w - scroll_har
            if flag_ver:
                h = y - y1  # 移动高度
                dy = y2 + h * f2  # 原图y
                if dy < 0:  # 位置矫正
                    dy = 0
                elif dy > img_h - show_h:
                    dy = img_h - show_h
                sy = y3 + h  # 滚动条y
                if sy < 0: # 位置矫正
                    sy = 0
                elif sy > win_h - scroll_var:
                    sy = win_h - scroll_var
            dx, dy = int(dx), int(dy)
            img1 = img[dy:dy + show_h, dx:dx + show_w]  # 截取显示图片
            dst = img1.copy()
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        flag, flag_hor, flag_ver = 0, 0, 0
        x1, y1, x2, y2, x3, y3 = 0, 0, 0, 0, 0, 0
    elif event == cv2.EVENT_LBUTTONDBLCLK:
        truex = x + dx
        truey = y + dy
        CoordinateX.append(truex)
        CoordinateY.append(truey)
        
    if horizontal and vertical:
        sx, sy = int(sx), int(sy)
        # 对dst1画图而非dst，避免鼠标事件不断刷新使显示图片不断进行填充
        dst1 = cv2.copyMakeBorder(dst, 0, scroll_w, 0, scroll_w, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.rectangle(dst1, (sx, show_h), (int(sx + scroll_har), win_h), (181, 181, 181), -1)  # 画水平滚动条
        cv2.rectangle(dst1, (show_w, sy), (win_w, int(sy + scroll_var)), (181, 181, 181), -1)  # 画垂直滚动条
    elif horizontal == 0 and vertical:
        sx, sy = int(sx), int(sy)
        dst1 = cv2.copyMakeBorder(dst, 0, 0, 0, scroll_w, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.rectangle(dst1, (show_w, sy), (win_w, int(sy + scroll_var)), (181, 181, 181), -1)  # 画垂直滚动条
    elif horizontal and vertical == 0:
        sx, sy = int(sx), int(sy)
        dst1 = cv2.copyMakeBorder(dst, 0, scroll_w, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.rectangle(dst1, (sx, show_h), (int(sx + scroll_har), win_h), (181, 181, 181), -1)  # 画水平滚动条
#    cv2.imshow("img", dst1)
#    cv2.waitKey(1)

def tag_pic(image):
    global flag, horizontal, vertical, flag_hor, flag_ver, dx, dy, sx, sy, dst, x1, y1, x2, y2, x3, y3, f1, f2
    global zoom, scroll_har, scroll_var, img_w, img_h, img, dst1, win_w, win_h, show_w, show_h, CoordinateX, CoordinateY
    global truex,truey
    global listofnum
#    img = cv2.imread("1.jpg")  # 此处需换成大于img_w * img_h的图片
    img = ResizeWithAspectRatio(image, width=1200)
    cv2.namedWindow('img')
    img_h, img_w = img.shape[0:2]  # 原图宽高
    show_h, show_w = 700, 1201   # 显示图片宽高
    horizontal, vertical = 0, 0  # 原图是否超出显示图片
    dx, dy = 0, 0  # 显示图片相对于原图的坐标
#    scroll_w = 16  # 滚动条宽度
    sx, sy = 0, 0  # 滚动块相对于滚动条的坐标
    flag, flag_hor, flag_ver = 0, 0, 0  # 鼠标操作类型，鼠标是否在水平滚动条上，鼠标是否在垂直滚动条上
    x1, y1, x2, y2, x3, y3 = 0, 0, 0, 0, 0, 0  # 中间变量
    win_w, win_h = show_w + scroll_w, show_h + scroll_w  # 窗口宽高
    scroll_har, scroll_var = win_w * show_w / img_w, win_h * show_h / img_h  # 滚动条水平垂直长度
    wheel_step, zoom = 0.05, 1  # 缩放系数， 缩放值
    zoom_w, zoom_h = img_w, img_h  # 缩放图宽高
    f1, f2 = (img_w - show_w) / (win_w - scroll_har), (img_h - show_h) / (win_h - scroll_var)  # 原图可移动部分占滚动条可移动部分的比例
    CoordinateX = []  # 选中点的X坐标集合
    CoordinateY = []  # 选中点的Y坐标集合
    if img_h <= show_h and img_w <= show_w:
        cv2.imshow("img", img)
        cv2.destroyAllWindows()
        print("1")
        sys.exit(0)
    else:
        if img_w > show_w:
            horizontal = 1
        if img_h > show_h:
            vertical = 1
        i = img[dy:dy + show_h, dx:dx + show_w]
        dst = i.copy()
    
    cv2.resizeWindow("img", win_w, win_h)
    cv2.setMouseCallback('img', mouse)
    
    
    mouse(0, 0, 0, 0, 0)
    while(1):
        cv2.imshow("img", dst1)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            break
        elif k >=48 and k <=57:
            img1 = img[dy:dy + show_h, dx:dx + show_w]  # 截取显示图片
            cv2.putText(img1, chr(k) , (truex-dx,truey-dy), cv2.FONT_HERSHEY_SIMPLEX, 
                        2, (0, 0, 255), 10, cv2.LINE_AA)
            listofnum.append(chr(k))
            dst = img1.copy()
            mouse(0, 0, 0, 0, 0)
        elif k == 97:
            cv2.destroyAllWindows()
            image = np.rot90(image)
            img = ResizeWithAspectRatio(image, width=1200)
            cv2.namedWindow('img')
            img_h, img_w = img.shape[0:2]  # 原图宽高
            show_h, show_w = 700, 1201   # 显示图片宽高
            horizontal, vertical = 0, 0  # 原图是否超出显示图片
            dx, dy = 0, 0  # 显示图片相对于原图的坐标
        #    scroll_w = 16  # 滚动条宽度
            sx, sy = 0, 0  # 滚动块相对于滚动条的坐标
            flag, flag_hor, flag_ver = 0, 0, 0  # 鼠标操作类型，鼠标是否在水平滚动条上，鼠标是否在垂直滚动条上
            x1, y1, x2, y2, x3, y3 = 0, 0, 0, 0, 0, 0  # 中间变量
            win_w, win_h = show_w + scroll_w, show_h + scroll_w  # 窗口宽高
            scroll_har, scroll_var = win_w * show_w / img_w, win_h * show_h / img_h  # 滚动条水平垂直长度
            wheel_step, zoom = 0.05, 1  # 缩放系数， 缩放值
            zoom_w, zoom_h = img_w, img_h  # 缩放图宽高
            f1, f2 = (img_w - show_w) / (win_w - scroll_har), (img_h - show_h) / (win_h - scroll_var)  # 原图可移动部分占滚动条可移动部分的比例
            CoordinateX = []  # 选中点的X坐标集合
            CoordinateY = []  # 选中点的Y坐标集合
            if img_h <= show_h and img_w <= show_w:
                cv2.imshow("img", img)
                cv2.destroyAllWindows()
                print("1")
                sys.exit(0)
            else:
                if img_w > show_w:
                    horizontal = 1
                if img_h > show_h:
                    vertical = 1
                i = img[dy:dy + show_h, dx:dx + show_w]
                dst = i.copy()
            
            cv2.resizeWindow("img", win_w, win_h)
            cv2.setMouseCallback('img', mouse)
            mouse(0, 0, 0, 0, 0)
        elif k == 100:
            cv2.destroyAllWindows()
            image = np.rot90(image)
            image = np.rot90(image)
            image = np.rot90(image)
            img = ResizeWithAspectRatio(image, width=1200)
            cv2.namedWindow('img')
            img_h, img_w = img.shape[0:2]  # 原图宽高
            show_h, show_w = 700, 1201   # 显示图片宽高
            horizontal, vertical = 0, 0  # 原图是否超出显示图片
            dx, dy = 0, 0  # 显示图片相对于原图的坐标
        #    scroll_w = 16  # 滚动条宽度
            sx, sy = 0, 0  # 滚动块相对于滚动条的坐标
            flag, flag_hor, flag_ver = 0, 0, 0  # 鼠标操作类型，鼠标是否在水平滚动条上，鼠标是否在垂直滚动条上
            x1, y1, x2, y2, x3, y3 = 0, 0, 0, 0, 0, 0  # 中间变量
            win_w, win_h = show_w + scroll_w, show_h + scroll_w  # 窗口宽高
            scroll_har, scroll_var = win_w * show_w / img_w, win_h * show_h / img_h  # 滚动条水平垂直长度
            wheel_step, zoom = 0.05, 1  # 缩放系数， 缩放值
            zoom_w, zoom_h = img_w, img_h  # 缩放图宽高
            f1, f2 = (img_w - show_w) / (win_w - scroll_har), (img_h - show_h) / (win_h - scroll_var)  # 原图可移动部分占滚动条可移动部分的比例
            CoordinateX = []  # 选中点的X坐标集合
            CoordinateY = []  # 选中点的Y坐标集合
            if img_h <= show_h and img_w <= show_w:
                cv2.imshow("img", img)
                cv2.destroyAllWindows()
                print("1")
                sys.exit(0)
            else:
                if img_w > show_w:
                    horizontal = 1
                if img_h > show_h:
                    vertical = 1
                i = img[dy:dy + show_h, dx:dx + show_w]
                dst = i.copy()
            
            cv2.resizeWindow("img", win_w, win_h)
            cv2.setMouseCallback('img', mouse)
            mouse(0, 0, 0, 0, 0)
        elif k == 13:
    #        print(mouseX,mouseY)
#            cv2.imwrite("2.jpg", img)
            return img
            cv2.destroyAllWindows()
            break
    
listofnums = []
listofnum = []
if __name__ == "__main__":
    # execute only if run as a script
    number = int(input("输入从第几个文件开始："))

    files= os.listdir("./") #得到文件夹下的所有文件名称
    pdfs = []
    for file in files: #遍历文件夹
         if not os.path.isdir(file): #判断是否是文件夹，不是文件夹才打开
              if file[-3:] == "pdf":
                  pdfs.append(file) #每个文件的文本存到list中

    if not os.path.exists("out"):
        os.mkdir("out")
    
    pdfs = pdfs[number-1:]
#    with open('stocks.csv','w') as f:

#        f_csv.writerow(headers)
#        f_csv.writerows(rows)
    
    for pdf in pdfs:
#        f = open('stocks.csv','a+')
        f = codecs.open('./out/table.txt','a+','utf-8')
        print(pdf)
        listofnum = []
        listofnum.append(pdf)
        pages = convert_from_path(pdf, 150)
        new_pages = []
        for image in pages:
            np_img = np.array(image);
            np_img = np_img[...,::-1]
            new_image = Image.fromarray(np.uint8(tag_pic(np_img))[...,::-1])
            new_pages.append(new_image)
        new_pages[0].save("./out/"+pdf[0:-1-3]+".pdf", save_all=True, append_images=new_pages[1:])   
        listofnums.append(listofnum)
#        print(listofnum)
        for item in listofnum:
            f.write("%s," % item)
            
        f.write("\n")
        f.close()
    
#    print(CoordinateX)
#    print(CoordinateY)