import imghdr
from plistlib import UID
from flask import Flask, render_template, request, redirect, url_for, session,send_file
import pyodbc
import os
from xmlrpc.client import Server
import pandas as pd
import pyodbc
import cv2
from io import BytesIO
from matplotlib import pyplot as plt
img=cv2.imread('static/0.jpg')
app = Flask(__name__ ,template_folder='templates')

conn =pyodbc.connect('Driver={SQL Server};' 'Server=MSI\MSSQLSERVER01;'
                            'Database=ai_lib;' 'Trusted_connection=yes;')
cursor =conn.cursor()
sql="""SELECT [題名],[作者] FROM [book_inventory]where [barcode] = '31206001111312' """
cursor.execute(sql)
row =cursor.fetchone()

def serve_cv_image(cvimg):
    _, encoded_img = cv2.imencode('.jpg', cvimg, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    img_io = BytesIO(encoded_img)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpg')
@app.route("/")#首頁
def test():
    return index2()
def index2():
    html=(
'<!DOCTYPE html>'
'<html lang="en">'
'<head>'
  '<meta charset="UTF-8">'
  '<title>Title</title>'
'</head>'
'<body>'
  '<table class="table table-bordered">'
  '<tr>'
    '<th>作者</th>'
    '<th>書名</th></tr>'
f"<img src='/cv0'  width={200} height={100}/>"
  '</table>'
'</body>'
'</html>')
    return html
@app.route('/cv/<name>/<writer>')
def imcv(name,writer):

  return serve_cv_image(img)
if __name__ == "__main__":
    app.run(debug=True)