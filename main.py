import mysql.connector
import csv
import datetime
import pandas as pd

HOST = "localhost"
USER = "root"
PASSWD = "PASSWORD"
DATABASE = "templedonations"

def createDB():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD
    )

    cursor = db.cursor()
    cursor.execute("CREATE DATABASE templedonations")

def createTables():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    cursor.execute("CREATE TABLE Bank_transactions (date DATE, ref_no VARCHAR(6), type VARCHAR(20), member_no FLOAT, memo VARCHAR(500), payment VARCHAR(5), deposit FLOAT)")
    cursor.execute("CREATE TABLE Member_transactions (sr_no INT, events VARCHAR(50), date DATE, member_no FLOAT, amount FLOAT, paid VARCHAR(5), comments VARCHAR(500))")

def populateBankTransactions():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    sqlCommand = "INSERT INTO Bank_transactions(date, ref_no, type, member_no, memo, payment, deposit) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    with open('Bank Transactions - Sheet1.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        next(csv_reader)


        for line in csv_reader:
            dateSplit = line[0].split("/")
            date = datetime.date(int(dateSplit[2]), int(dateSplit[0]), int(dateSplit[1]))
            try:
                memberNum = int(line[3])
            except: 
                memberNum = None
            entry = (date, line[1], line[2], memberNum, line[4], line[5], float(line[6].replace(",", "")))
            cursor.execute(sqlCommand, entry)
    db.commit()

def populateMemberTransactions():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    sqlCommand = "INSERT INTO Member_transactions(sr_no, events, date, member_no, amount, paid, comments) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    with open('Member Transactions - Sheet1.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        next(csv_reader)


        for line in csv_reader:
            dateSplit = line[2].split("/")
            date = datetime.date(int(dateSplit[2]), int(dateSplit[0]), int(dateSplit[1]))
            try:
                memberNum = int(line[3])
            except: 
                memberNum = None

            try:
                sr_no = int(line[0])
            except:
                sr_no = None    
            entry = (sr_no, line[1], date, memberNum, float(line[4].replace(",", "").replace("$", "")), line[5], line[6])
            cursor.execute(sqlCommand, entry)
    db.commit()

def searchMemberTransactions(memeberID):
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    sqlCommand = "SELECT * FROM Bank_transactions WHERE member_no = MEMBERID;"
    cursor.execute(sqlCommand.replace("MEMBERID", str(memeberID)))
    bankTableResult = cursor.fetchall()

    sqlCommand = "SELECT * FROM Member_transactions WHERE member_no = MEMBERID;"
    cursor.execute(sqlCommand.replace("MEMBERID", str(memeberID)))
    memberTableResult = cursor.fetchall()

    df1 = pd.DataFrame()
    for x in bankTableResult:
        df1a = pd.DataFrame(list(x)).T
        df1 = pd.concat([df1, df1a])

    df2 = pd.DataFrame()
    for x in memberTableResult:
        df2a = pd.DataFrame(list(x)).T
        df2 = pd.concat([df2, df2a])

    return [df1, df2]

def viewBankTransactions():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    sqlCommand = "SELECT * FROM Bank_transactions;"
    cursor.execute(sqlCommand)
    tableResult = cursor.fetchall()

    df1 = pd.DataFrame()
    for x in tableResult:
        df1a = pd.DataFrame(list(x)).T
        df1 = pd.concat([df1, df1a])
    
    return df1

def viewMemberTransactions():
    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    sqlCommand = "SELECT * FROM Member_transactions;"
    cursor.execute(sqlCommand)
    tableResult = cursor.fetchall()

    df1 = pd.DataFrame()
    for x in tableResult:
        df1a = pd.DataFrame(list(x)).T
        df1 = pd.concat([df1, df1a])
    
    return df1

def viewTables():
    bT = viewBankTransactions()
    mT = viewMemberTransactions()

    with open("templates/view_tables.html", "w") as _file:
            _file.write("Bank Transactions Data \n" + 
                        bT.to_html() +
                        "\n\n\n" +
                        "Member Transactions Data \n" +
                        mT.to_html())

def updateMemberTable(df1, df2):
    memberID = df2[0]['3']

    db = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWD,
        database=DATABASE
    )

    cursor = db.cursor()

    comment = []

    for i in range(len(df1)):
        getDate = df1[i]['0'].replace(",", "").split(" ")
        getDateSliced = " ".join(getDate[1:4])
        date = datetime.datetime.strptime(getDateSliced, "%d %b %Y").strftime('%d/%m/%Y')

        getAmount = df1[i]['6']

        strCom = "Date: ",date, " (Amount: ", str(getAmount),")"

        comment.append("".join(strCom))
    finalcomment = " -- ".join(comment)

    sqlCommand = "UPDATE Member_transactions SET comments = %s, paid = %s WHERE sr_no = %s AND events = %s AND date = %s AND  member_no = %s AND amount = %s;"

    for i in range(len(df2)):
        getDate = df2[i]['2'].replace(",", "").split(" ")
        getDateSliced = " ".join(getDate[1:4])
        date = datetime.datetime.strptime(getDateSliced, "%d %b %Y").strftime('%Y-%m-%d')
        pay = "Yes"

        if len(df2[i]['6'])>6:
            print("need to append")
            appendedfinalcomment = "{} -- {}".format(df2[i]['6'], finalcomment)
            row = (appendedfinalcomment, "Yes" , int(df2[i]['0']), df2[i]['1'], date, int(memberID), df2[i]['4'])
        else:
            row = (finalcomment, "Yes" , int(df2[i]['0']), df2[i]['1'], date, int(memberID), df2[i]['4'])

        cursor.execute(sqlCommand, row)

    db.commit()

    df = searchMemberTransactions(memberID)

    return [memberID, df[0], df[1]]


    
