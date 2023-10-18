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
SQL = """
SELECT * FROM [rec_data] where [User] = '%s'
"""%(uid)


user_pd = pd.read_sql(SQL,
            conn,
            parse_dates=["date_column"])
user_reclist = list(user_pd.iloc[0][1:11])
book_list = pd.DataFrame(columns=['題名','作者','publisher','索書號'])

for bar in user_reclist:
        
    SQL2 = """
    SELECT * FROM [book_inventory] where [barcode] = '%s'
    """%(bar)
    
    book_pd = pd.read_sql(SQL2,
                conn,
                parse_dates=["date_column"])
    book_list = pd.concat([book_list, book_pd[['題名','作者','publisher','索書號']]])
    # print(book_pd[['題名','作者','publisher','索書號']])

book_list = book_list.reset_index()
del book_list['index']
del book_list['publisher']
print(book_list)
# book_list.to_csv('推薦清單/' + user_ID + '最愛推薦.csv', encoding="utf-8-sig")
# 作者推薦
SQL = """
SELECT * FROM [author_rec] where [User] = '%s'
"""%(uid)


user_pd = pd.read_sql(SQL,
            conn,
            parse_dates=["date_column"])
user_reclist = list(user_pd.iloc[0][1:11])
book_list = pd.DataFrame(columns=['題名','作者','publisher','索書號'])

for bar in user_reclist:
        
    SQL2 = """
    SELECT * FROM [book_inventory] where [barcode] = '%s'
    """%(bar)
    
    book_pd = pd.read_sql(SQL2,
                conn,
                parse_dates=["date_column"])
    book_list = pd.concat([book_list, book_pd[['題名','作者','publisher','索書號']]])
    # print(book_pd[['題名','作者','publisher','索書號']])

book_list = book_list.reset_index()
del book_list['index']
print(book_list)
# book_list.to_csv('推薦清單/' + user_ID + '作者推薦.csv', encoding="utf-8-sig")
# 類別推薦
SQL = """
SELECT * FROM [class_rec] where [User] = '%s'
"""%(uid)


user_pd = pd.read_sql(SQL,
            conn,
            parse_dates=["date_column"])
user_reclist = list(user_pd.iloc[0][1:11])
book_list = pd.DataFrame(columns=['題名','作者','publisher','索書號'])

for bar in user_reclist:
        
    SQL2 = """
    SELECT * FROM [book_inventory] where [barcode] = '%s'
    """%(bar)
    
    book_pd = pd.read_sql(SQL2,
                conn,
                parse_dates=["date_column"])
    book_list = pd.concat([book_list, book_pd[['題名','作者','publisher','索書號']]])
    # print(book_pd[['題名','作者','publisher','索書號']])

book_list = book_list.reset_index()
del book_list['index']
print(book_list)
# book_list.to_csv('推薦清單/' + user_ID + '類別推薦.csv', encoding="utf-8-sig")
# 流行推薦(會先做uid確認)

# 若uid不在1000個使用者內，隨機取一個使用者
import random
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
book_list = pd.DataFrame(columns=['題名','作者','publisher','索書號'])

for bar in user_reclist:
        
    SQL2 = """
    SELECT top(1)* FROM [book_inventory] where [題名] = '%s'
    """%(bar)
    
    book_pd = pd.read_sql(SQL2,
                conn,
                parse_dates=["date_column"])
    book_list = pd.concat([book_list, book_pd[['題名','作者','publisher','索書號']]])
    # print(book_pd[['題名','作者','publisher','索書號']])

book_list = book_list.reset_index()
del book_list['index']
print(book_list)
# book_list.to_csv('推薦清單/' + user_ID + '流行推薦.csv', encoding="utf-8-sig")