from http.cookies import BaseCookie
from xmlrpc.client import Server
import pandas as pd
import math
import pyodbc
#192.168.42.147
# 連結資料庫
#conn = pymssql.connect('192.168.42.147', user='test2', password='Aa123456789', database='ai_lib')
conn =pyodbc.connect('Driver={SQL Server};' 'Server=MSI\MSSQLSERVER01;'
                            'Database=ai_lib;' 'Trusted_connection=yes;')
pd.set_option("display.width", 500)
pd.set_option("display.max_row", 200)
# 設定sql語法查詢"喜好推薦"資料
# 改成接收網頁回傳的uid
uid = '4ySX6/jgQjsVH/Mjd9EqrA=='

# 最愛推薦
def Popularity(uid):# 流行推薦
    SQL = """
    SELECT * FROM [user_recommend] where [使用者] = '%s'
    """%(uid)


    user_pd = pd.read_sql(SQL,
                conn,
                parse_dates=["date_column"])
    # print(user_pd)
    user_reclist = list(user_pd['書籍'])
    book_list = pd.DataFrame(columns=['題名','作者'])

    for bar in user_reclist:
            
        SQL2 = """
        SELECT top(1)* FROM [book_inventory] where [題名] = '%s'
        """%(bar)
        
        book_pd = pd.read_sql(SQL2,
                    conn,
                    parse_dates=["date_column"])
        book_list = pd.concat([book_list, book_pd[['題名','作者']]])
        # print(book_pd[['題名','作者','publisher','索書號']])

    book_list = book_list.reset_index()
    del book_list['index']
    return book_list
# book_list.to_csv('推薦清單/' + user_ID + '最愛推薦.csv', encoding="utf-8-sig")
# 作者推薦
Popularity(uid)
