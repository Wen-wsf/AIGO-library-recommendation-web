from plistlib import UID
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pyodbc
import os
from xmlrpc.client import Server
import pandas as pd
import pyodbc
import cv2 as cv2
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
pd.set_option("display.width", 500)
pd.set_option("display.max_row", 200)
x = []
#A116325
app = Flask(__name__, template_folder='templates')
conn = pyodbc.connect('Driver={SQL Server};' 'Server=MSI\MSSQLSERVER01;'
                      'Database=ai_lib;' 'Trusted_connection=yes;')
cursor = conn.cursor()
sql = """SELECT [題名],[作者] FROM [book_inventory]where [barcode] = '' """
cursor.execute(sql)
row = cursor.fetchone()
def lover(uid):  # 最愛推薦
    SQL = """
    SELECT * FROM [rec_data] where [User] = '%s'
    """ % (uid)
    user_pd = pd.read_sql(SQL,
                          conn,
                          parse_dates=["date_column"])
    user_reclist = list(user_pd.iloc[0][1:13])
    book_list = pd.DataFrame(columns=['題名', '作者'])

    for bar in user_reclist:

        SQL2 = f"SELECT top(1)* FROM [book_inventory] where [barcode] = '{str(bar)}'" 

        book_pd = pd.read_sql(SQL2,
                              conn,
                              parse_dates=["date_column"])
        book_list = pd.concat([book_list, book_pd[['題名', '作者']]])
        # print(book_pd[['題名','作者','publisher','索書號']])

    book_list = book_list.reset_index()
    del book_list['index']

    return book_list


def writer(uid):  # 作者
    SQL = """
    SELECT * FROM [author_rec] where [User] = '%s'
    """ % (uid)

    user_pd = pd.read_sql(SQL,
                          conn,
                          parse_dates=["date_column"])
    user_reclist = list(user_pd.iloc[0][1:11])
    book_list = pd.DataFrame(columns=['題名', '作者'])

    for bar in user_reclist:

        SQL2 = f"SELECT top(1)* FROM [book_inventory] where [barcode] = '{str(bar)}'" 

        book_pd = pd.read_sql(SQL2,
                              conn,
                              parse_dates=["date_column"])
        book_list = pd.concat([book_list, book_pd[['題名', '作者']]])
    book_list = book_list.reset_index()
    del book_list['index']
    return book_list
def classbook(uid):  # 類別推薦

    SQL = """
    SELECT * FROM [class_rec] where [User] = '%s'
    """ % (uid)

    user_pd = pd.read_sql(SQL,
                          conn,
                          parse_dates=["date_column"])
    user_reclist = list(user_pd.iloc[0][1:11])
    book_list = pd.DataFrame(columns=['題名', '作者'])

    for bar in user_reclist:
        SQL2 = f"SELECT top(1)* FROM [book_inventory] where [barcode] = '{str(bar)}'" 

        book_pd = pd.read_sql(SQL2,
                              conn,
                              parse_dates=["date_column"])
        book_list = pd.concat(
            [book_list, book_pd[['題名', '作者']]])
        # print(book_pd[['題名','作者','publisher','索書號']])

    book_list = book_list.reset_index()
    del book_list['index']
    return book_list
def Popularity(uid):# 流行推薦
   SQL = """
   SELECT [使用者] FROM [user_recommend]  
   """

   userlist_pd = pd.read_sql(SQL,
               conn,
               parse_dates=["date_column"])
   user_list = list(set(userlist_pd["使用者"]))
# print(user_list)
   if uid not in user_list:
      uid2 = random.choice(user_list)
   else:
      uid2 = uid

# 流行推薦
   SQL = """
   SELECT * FROM [user_recommend] where [使用者] = '%s'
   """%(uid2)


   user_pd = pd.read_sql(SQL,
               conn,
               parse_dates=["date_column"])
   # print(user_pd)
   user_reclist = list(user_pd['書籍'])
   book_list = pd.DataFrame(columns=['題名','作者'])

   for bar in user_reclist:
         
      SQL2 = f"SELECT top(1)* FROM [book_inventory] where [題名] = '{str(bar)}'" 
      
      book_pd = pd.read_sql(SQL2,
                  conn,
                  parse_dates=["date_column"])
      book_list = pd.concat([book_list, book_pd[['題名','作者']]])
      # print(book_pd[['題名','作者','publisher','索書號']])

   book_list = book_list.reset_index()
   del book_list['index']
   return book_list

def data_clean(data):
    re_data = []
    for a in data:
        temp = re.sub('[a-zA-Z]', '', a)
        temp = re.sub(':', '', temp)
        temp = re.sub('[0-9]', '', temp)
        temp = re.sub('[.]', '', temp)
        temp = re.sub('[,]', '', temp)
        temp = re.sub('[/]', '', temp)
        temp = re.sub('[ ]', '', temp)
        temp = re.sub('[-]', '', temp)
        temp = re.sub('[!]', '', temp)
        temp = re.sub('[?]', '', temp)
        re_data.append(temp)
    return re_data

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

def ch_word(img, str, x, y):
    imgPIL = Image.fromarray(cv2.cvtColor(img[128:, :], cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(imgPIL)
    font = ImageFont.truetype('C:\\Windows\\Fonts\\mingliu.ttc')
    draw.text((x, y), str, fill=(0, 1, 255), font=font)
    img2 = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
    img[128:, :] = img2
    return img

def pic(img_path, name, writer):
    back_w = np.full([200, 128, 3],255, "uint8")
    img = cv_imread(img_path)
    img = img[:, :, ::-1]
    img = cv2.resize(img, (128, 128))
    back_w[:128, :] = img
    book_wr = "作者"+writer
    book_n = "書名:"+name
    x1, y1 = 10, 10
    x2, y2 = 10, 40
    back_w = ch_word(back_w, book_n, x1, y1)
    back_w = ch_word(back_w, book_wr, x2, y2)
    return back_w

def serve_cv_image(cvimg):
    _, encoded_img = cv2.imencode(
        '.jpg', cvimg, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    img_io = BytesIO(encoded_img)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpg')

def pic_random(path):
    num = random.randint(0, 39)
    path_a = path + str(num)+'.jpg'
    return path_a

def html(uid):
    lover_book_list = lover(uid)
    book_names = list(lover_book_list['題名'])
    book_writers = list(lover_book_list['作者'])

    writer_book_list = writer(uid)
    book_names2 = list(writer_book_list['題名'])
    book_writers2 = list(writer_book_list['作者'])

    classbook_book_list = classbook(uid)
    book_names3 = list(classbook_book_list['題名'])
    book_writers3 = list(classbook_book_list['作者'])

    Popularity_book_list = Popularity(uid)
    book_names4 = list(Popularity_book_list['題名'])
    book_writers4 = list(Popularity_book_list['作者'])

    html = ("""<!DOCTYPE html>
<html lang="en">

<head>
   <!-- basic -->
   <meta charset="utf-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <!-- mobile metas -->
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <meta name="viewport" content="initial-scale=1, maximum-scale=1">
   <!-- site metas -->
   <title>屏東縣公共圖書館推薦系統</title>
   <meta name="keywords" content="">
   <meta name="description" content="">
   <meta name="author" content="">
   <!-- bootstrap css -->
   <link rel="stylesheet" type="text/css" href="../static/css/bootstrap.min.css">
   <!-- style css -->
   <link rel="stylesheet" type="text/css" href="../static/css/style.css">
   <!-- Responsive-->
   <link rel="stylesheet" href="../static/css/responsive.css">
   <!-- fevicon -->
   <link rel="icon" href="../static/images/fevicon.png" type="image/gif" />
   <!-- Scrollbar Custom CSS -->
   <link rel="stylesheet" href="../static/css/jquery.mCustomScrollbar.min.css">
   <!-- Tweaks for older IEs-->
   <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css">
   <!-- owl stylesheets -->
   <link rel="stylesheet" href="../static/css/owl.carousel.min.css">
   <link rel="stylesheet" href="../static/css/owl.theme.default.min.css">
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/jquery.fancybox.min.css"
      media="screen">
   <link href="https://unpkg.com/gijgo@1.9.13/css/gijgo.min.css" rel="stylesheet" type="text/css" />

   <!-- 功能 -->
   <script src="https://cdn.bootcss.com/jquery/1.10.2/jquery.min.js"></script>
   <script>
      var cot = 0;//設置一個計數器，初始值為0；作用是用來監聽點擊切換的時候哪一個圖片應該隱藏或者顯示
      function nex() {
         if (cot <= 4) {
            $('.imgs img').eq(cot).animate({ 'margin-left': '-400px' }, 500);
            cot++;
         }
      }
      function pre() {
         if (cot > 0) {
            cot--;
            $('.imgs img').eq(cot).animate({ 'margin-left': '0' }, 500);
         }
      }
      var cot1 = 0;
      function nex1() {//新書
         if (cot1 <= 4) {
            $('.imgs1 img').eq(cot1).animate({ 'margin-left': '-305px' }, 500);
            cot1++;
         }
      }
      function pre1() {
         if (cot1 > 0) {
            cot1--;
            $('.imgs1 img').eq(cot1).animate({ 'margin-left': '0' }, 500);
         }
      }
      var cot2 = 0;
      function nex2() {//分類
         if (cot2 <= 4) {
            $('.imgs2 img').eq(cot2).animate({ 'margin-left': '-305px' }, 500);
            cot2++;
         }
      }
      function pre2() {
         if (cot2 > 0) {
            cot2--;
            $('.imgs2 img').eq(cot2).animate({ 'margin-left': '0' }, 500);
         }
      }
      var cot3= 0;
      function nex3() {//流行
         if (cot3 <= 4) {
            $('.imgs3 img').eq(cot3).animate({ 'margin-left': '-305px' }, 500);
            cot3++;
         }
      }
      function pre3() {
         if (cot3 > 0) {
            cot3--;
            $('.imgs3 img').eq(cot3).animate({ 'margin-left': '0' }, 500);
         }
      }
      var cot4 = 0;
      function nex4() {//作者
         if (cot4 <= 4) {
            $('.imgs4 img').eq(cot4).animate({ 'margin-left': '-305px' }, 500);
            cot4++;
         }
      }
      function pre4() {
         if (cot4 > 0) {
            cot4--;
            $('.imgs4 img').eq(cot4).animate({ 'margin-left': '0' }, 500);
         }
      }
   </script>
</head>

<body>
   <!-- header section start -->
   <div class="header_section">
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
         <a class="logo" href="index.html"><img src="../static/images/logo.png"></a>
         <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
         </button>
         <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
               <li class="nav-item active">
                  <a class="nav-link" href="index.html">主頁</a>
               </li>
			  <li class="nav-item active">
                  <a class="nav-link" href="https://app.powerbi.com/view?r=eyJrIjoiM2MzZDVmM2QtZWU2NS00ZDE0LWExMTktNjcxNmNhZmQ3NTI1IiwidCI6IjQ4NDM4ZDUzLTM5MWEtNDA4My05OTdlLTYzZTcwNTMzOGFmZCIsImMiOjEwfQ%3D%3D">借閱分析</a>
               </li>
            </ul>
            <div class="search_icon"><a href="index.html"><img src="../static/images/user-icon.png"><span
                     class="padding_left_15">登出</span></a></div>
         </div>
      </nav>
   </div>
   <!-- header section end -->
   <!-- banner section end -->
   <div class="banner_section layout_padding">
      <div class="container">
         <div class="row">
            <div class="col-md-6">
               <div class="banner_taital">屏東縣公共圖書館<br>圖書推薦</div>
               <p class="banner_text">您貼心的尋書指南 </p>
               <!-- <div class="see_bt"><a href="#">See More</a></div> -->
            </div>
         </div>
      </div>
   </div>
   <!-- banner section end -->

   <!-- books section start -->
   <div class="movies_section layout_padding">
      <div class="container">
         <div class="movies_menu">
            <ul>
               <li class="active"><a href="#R1">最愛推薦</a></li>
               <li><a href="#R3">分類推薦</a></li>
               <li><a href="#R4">流行推薦</a></li>
               <li><a href="#R5">作者推薦</a></li>
               <li><a href="#R2">新品推薦</a></li>

            </ul>
         </div>

         <div class="movies_section_2 layout_padding" style="width:900px;margin:auto;overflow:hidden">
            <h2 class="letest_text" id="R1" style="width:50000px;">最愛推薦</h2>
            <!--<div class="seemore_bt"><a href="BOOKRS.html">更多推薦</a></div>-->
            <div>
               <!--<div onclick="pre()" style="float:left;cursor:pointer">上一頁</div>-->
               <!--<div onclick="nex()" style="float:right;cursor:pointer">下一頁</div>-->
            </div>
            <div class="movies_main">
               <div class="iamge_movies_main">
                  <div style="width:900px;margin:auto;overflow:hidden">""")
    html2 = ('<div class="imgs" style="width:50000px;">'
             f"<img src='/cv/{book_names[0]}/{book_writers[0]} '/>"
             f"<img src='/cv/{book_names[1]}/{book_writers[1]}'/>"
             f"<img src='/cv/{book_names[2]}/{book_writers[2]}'/>"
             f"<img src='/cv/{book_names[3]}/{book_writers[3]}'/>"
             f"<img src='/cv/{book_names[4]}/{book_writers[4]}'/>"
             f"<img src='/cv/{book_names[5]}/{book_writers[5]}'/>"
             f"<img src='/cv/{book_names[6]}/{book_writers[6]}'/>"
             f"<img src='/cv/{book_names[7]}/{book_writers[7]}'/>"
             f"<img src='/cv/{book_names[8]}/{book_writers[8]}'/>"
             f"<img src='/cv/{book_names[9]}/{book_writers[9]}'/>"
             f"<img src='/cv/{book_names[10]}/{book_writers[10]}'/>"
             f"<img src='/cv/{book_names[11]}/{book_writers[11]}'/>"

             '</div>')

    html3 = ("""<div>
                         <div onclick="pre()" style="float:left;cursor:pointer">上一本</div>
                         <div onclick="nex()" style="float:right;cursor:pointer">下一本</div>
                     </div>
                 </div>
               </div>
            </div>
         </div>
         
         <div class="movies_section_2 layout_padding" style="width:900px;margin:auto;overflow:hidden">
            <h2 class="letest_text" id="R3" style="width:50000px;">分類推薦</h2>
            <div class="movies_main">
               <div class="iamge_movies_main">
                  <div style="width:900px;margin:auto;overflow:hidden">
                  """
                    ' <div class="imgs2" style="width:50000px;">'
                        f"<img src='/cv/{book_names2[0]}/{book_writers2[0]}'/>"
                        f"<img src='/cv/{book_names2[1]}/{book_writers2[1]}'/>"
                        f"<img src='/cv/{book_names2[2]}/{book_writers2[2]}'/>"
                        f"<img src='/cv/{book_names2[3]}/{book_writers2[3]}'/>"
                        f"<img src='/cv/{book_names2[4]}/{book_writers2[4]}'/>"
                        f"<img src='/cv/{book_names2[5]}/{book_writers2[5]}'/>"
                        f"<img src='/cv/{book_names2[6]}/{book_writers2[6]}'/>"
                        f"<img src='/cv/{book_names2[7]}/{book_writers2[7]}'/>"
                        f"<img src='/cv/{book_names2[8]}/{book_writers2[8]}'/>"
                        f"<img src='/cv/{book_names2[9]}/{book_writers2[9]}'/>"
                        '<!--這個div的作用是讓所有的圖片都排在同一水平上，這樣子切換的時候效果會更好-->'
                     '</div>'

                     """<div>
                         <div onclick="pre2()" style="float:left;cursor:pointer">上一本</div>
                         <div onclick="nex2()" style="float:right;cursor:pointer">下一本</div>
                     </div>
                 </div>
               </div>
            </div>
         </div>
         <div class="movies_section_2 layout_padding" style="width:900px;margin:auto;overflow:hidden">
               <h2 class="letest_text" id="R4" style="width:50000px;">流行推薦</h2>
               <!--<div class="seemore_bt"><a href="BOOKRS.html">更多推薦</a></div>-->
               <div>
                  <!--<div onclick="pre()" style="float:left;cursor:pointer">上一本</div>-->
                  <!--<div onclick="nex()" style="float:right;cursor:pointer">下一本</div>-->
               </div>
               <div class="movies_main">
                  <div class="iamge_movies_main">
                     <div style="width:900px;margin:auto;overflow:hidden">

                        <div class="imgs3" style="width:50000px;">"""
                           f"<img src='/cv/{book_names3[0]}/{book_writers3[0]}'/>"
                           f"<img src='/cv/{book_names3[1]}/{book_writers3[1]}'/>"
                           f"<img src='/cv/{book_names3[2]}/{book_writers3[2]}'/>"
                           f"<img src='/cv/{book_names3[3]}/{book_writers3[3]}'/>"
                           f"<img src='/cv/{book_names3[4]}/{book_writers3[4]}'/>"
                           f"<img src='/cv/{book_names3[5]}/{book_writers3[5]}'/>"
                           f"<img src='/cv/{book_names3[6]}/{book_writers3[6]}'/>"
                           f"<img src='/cv/{book_names3[7]}/{book_writers3[7]}'/>"
                           f"<img src='/cv/{book_names3[8]}/{book_writers3[8]}'/>"
                           f"<img src='/cv/{book_names3[9]}/{book_writers3[9]}'/>"
                        """</div>
                        <div>
                            <div onclick="pre3()" style="float:left;cursor:pointer">上一本</div>
                            <div onclick="nex3()" style="float:right;cursor:pointer">下一本</div>
                        </div>
                    </div>
                  </div>
               </div>
         </div>   
         <div class="movies_section_2 layout_padding" style="width:900px;margin:auto;overflow:hidden">
               <h2 class="letest_text" id="R5" style="width:50000px;">作者推薦</h2>
               <!--<div class="seemore_bt"><a href="BOOKRS.html">更多推薦</a></div>-->
               <div>
                  <!--<div onclick="pre()" style="float:left;cursor:pointer">上一本</div>-->
                  <!--<div onclick="nex()" style="float:right;cursor:pointer">下一本</div>-->
               </div>
               <div class="movies_main">
                  <div class="iamge_movies_main">
                     <div style="width:900px;margin:auto;overflow:hidden">"""
              
                       ' <div class="imgs4" style="width:50000px;">'
                           f"<img src='/cv/{book_names4[0]}/{book_writers4[0]}'/>"
                           f"<img src='/cv/{book_names4[1]}/{book_writers4[1]}'/>"
                           f"<img src='/cv/{book_names4[2]}/{book_writers4[2]}'/>"
                           f"<img src='/cv/{book_names4[3]}/{book_writers4[3]}'/>"
                           f"<img src='/cv/{book_names4[4]}/{book_writers4[4]}'/>"
                           f"<img src='/cv/{book_names4[5]}/{book_writers4[5]}'/>"
                           f"<img src='/cv/{book_names4[6]}/{book_writers4[6]}'/>"
                           f"<img src='/cv/{book_names4[7]}/{book_writers4[7]}'/>"
                           f"<img src='/cv/{book_names4[8]}/{book_writers4[8]}'/>"
                           f"<img src='/cv/{book_names4[9]}/{book_writers4[9]}'/>"
                           
                       """ </div>
                        <div>
                            <div onclick="pre4()" style="float:left;cursor:pointer">上一本</div>
                            <div onclick="nex4()" style="float:right;cursor:pointer">下一本</div>
                        </div>
                    </div>
                  </div>
               </div>
         </div>
         <div class="movies_section_2 layout_padding" style="width:900px;margin:auto;overflow:hidden">
            <h2 class="letest_text" id="R2" style="width:50000px;">新品推薦</h2>
            <!--<div class="seemore_bt"><a href="BOOKRS.html">更多推薦</a></div>-->
            <div>
               <!--<div onclick="pre()" style="float:left;cursor:pointer">上一本</div>-->
               <!--<div onclick="nex()" style="float:right;cursor:pointer">下一本</div>-->
            </div>
            <div class="movies_main">
               <div class="iamge_movies_main">
                  <div style="width:900px;margin:auto;overflow:hidden">
                     <!-- 這個最外圍的容器div寬度為900px，每張圖寬為300px，所以只顯示3張，剩下的圖超出容器隱藏起來 -->
                     <div class="imgs1" style="width:50000px;">
                         <!--這個div的作用是讓所有的圖片都排在同一水平上，這樣子切換的時候效果會更好-->
                         <img src="../static/newbook_recommend/0.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/1.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/2.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/3.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/4.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/5.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/6.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/7.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/8.jpg"  width="200" height="100"/>
                         <img src="../static/newbook_recommend/9.jpg"  width="200" height="100"/>
                     </div>
                     <div>
                         <div onclick="pre1()" style="float:left;cursor:pointer">上一本</div>
                         <div onclick="nex1()" style="float:right;cursor:pointer">下一本</div>
                     </div>
                 </div>
               </div>
            </div>
         </div>
      
   </div>         
      
   </div>
</div>
</div>

<div class="footer_section layout_padding">
      <div class="container">
         <div class="footer_menu">
            <ul>
               <li class="active"><a href="#R1">最愛推薦</a></li>
               <li><a href="#R3">分類推薦</a></li>
               <li><a href="#R4">流行推薦</a></li>
               <li><a href="#R5">作者推薦</a></li>
               <li><a href="#R2">新品推薦</a></li>
            </ul>
         </div>
         <div class="social_icon">
            <ul>
               <li><a href="https://zh-tw.facebook.com/ptclib/"><img src="../static/images/fb-icon.png"></a></li>
               <li><a href="https://mobile.twitter.com/hashtag/%E5%B1%8F%E6%9D%B1%E5%9C%96%E6%9B%B8%E9%A4%A8"><img
                        src="../static/images/twitter-icon.png"></a></li>
               <li><a href="#"><img src="../static/images/linkedin-icon.png"></a></li>
               <li><a href="#"><img src="../static/images/instagram-icon.png"></a></li>
            </ul>
         </div>
      </div>
   </div>
   <!-- footer  section end -->
   <!-- copyright section start -->
   <div class="copyright_section">
      <div class="container">
         <div class="copyright_text">Copyright 2022 All Right Reserved By <a href="https://html.design">AIGO</a></div>
      </div>
   </div>
   <!-- copyright section end -->
   <!-- Javascript files-->
   <script src="../static/js/jquery.min.js"></script>
   <script src="../static/js/popper.min.js"></script>
   <script src="../static/js/bootstrap.bundle.min.js"></script>
   <script src="../static/js/jquery-3.0.0.min.js"></script>
   <!-- sidebar -->
   <script src="../static/js/jquery.mCustomScrollbar.concat.min.js"></script>
   <script src="../static/js/custom.js"></script>
   <!-- javascript -->
   <script src="../static/js/owl.carousel.js"></script>
   <script src="https:cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/jquery.fancybox.min.js"></script>
   <script src="https://unpkg.com/gijgo@1.9.13/js/gijgo.min.js" type="text/javascript"></script>
   <script>
      $('#datepicker').datepicker({
         uiLibrary: 'bootstrap4'
      });
   </script>
</body>

</html>""")
    html = html+html2+html3
    x.clear()
    return html


@app.route('/cv/<name>/<writer>')
def imcv(name, writer):
    path = 'static/'
    while True:
      path_a = pic_random(path)
      if path_a not in x:
         x.append(path_a)
         break
    img = pic(path_a, name, writer)
    
    return serve_cv_image(img)


@app.route("/")  # 首頁
def index1():
    return render_template("index.html")
@app.route("/index.html")  # 首頁
def index2():
    return render_template("index.html")
# user1


@app.route("/test.html", methods=['POST'])  # 登入頁面
def test():
    if request.method == 'POST':
        # Create variables for easy access創建變量以便於訪問
        loginname = request.form['name2']
        loginpwd = request.form['pwd3']
        cursor.execute(
            """SELECT uid,user_id,user_password FROM [ai_lib].[dbo].[userAccount] WHERE user_id = ? AND user_password = ?""", (loginname, loginpwd))
        row = cursor.fetchone()
        if row:
            if row[0]=='BMwbIPrGYc0WAY5h9arA7A==':#A117606
               return render_template("test1.html")
            if row[0]=='4ySX6/jgQjuJgSqX6GEwtA==':#A112558
               return render_template("test2.html")
            if row[0]=='BMwbIPrGYc0YdTFObGEffA==':#A114720
               return render_template("test3.html")
            #"A112558"
            #"A114720","BMwbIPrGYc0WAY5h9arA7A=="
            return html(row[0])
         
        return("/")
        # return render_template("test.html")#使用者頁面
        # Fetch one record and return result獲取一條記錄並返回結果


@app.route("/login.html", methods=['GET', 'POST'])  # 登入頁面
def login1():
    return render_template("login.html")


# user2
@app.route("/test2.html", methods=['GET', 'POST'])  # 登入頁面
def test2():
    if request.method == 'POST':
        # Create variables for easy access創建變量以便於訪問
        loginname = request.form['name3']
        loginpwd = request.form['pwd4']
        cursor.execute(
            """SELECT uid,user_id,user_password FROM [ai_lib].[dbo].[userAccount] WHERE user_id = ? AND user_password = ?""", (loginname, loginpwd))
        row = cursor.fetchone()
        if row:
            return render_template("test2.html")
        # Fetch one record and return result獲取一條記錄並返回結果





# user3
@app.route("/test3.html", methods=['GET', 'POST'])  # 登入頁面
def test3():
    if request.method == 'POST':
        # Create variables for easy access創建變量以便於訪問
        loginname = request.form['name5']
        loginpwd = request.form['pwd6']
        cursor.execute(
            """SELECT uid,user_id,user_password FROM [ai_lib].[dbo].[userAccount] WHERE user_id = ? AND user_password = ?""", (loginname, loginpwd))
        row = cursor.fetchone()
        if row:
            return render_template("test3.html")
        # Fetch one record and return result獲取一條記錄並返回結果




@app.route("/noimage.html", methods=['GET', 'POST'])  # 圖片
def images():
    IMG_LIST = os.listdir('static/images')
    IMG_LIST = ['images/'+i for i in IMG_LIST]
    return render_template("noimage.html", mimetype=IMG_LIST)


# print(lover("BMwbIPrGYc3GCqc+dCV2bw=="))
if __name__ == "__main__":

    app.run(debug=True)
