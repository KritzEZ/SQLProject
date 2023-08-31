from flask import Flask, render_template, request, session
from main import *

app = Flask(__name__)
app.secret_key = "27eduCBA09"

@app.route("/")
def index():    
    return render_template("index.html")

@app.route("/create_db", methods=['POST'])
def createDBRoute():
    try:
        createDB()
        return render_template("index.html", success="Database successfully created!")
    except:
        return render_template("index.html", error="Error: Database already exists")

@app.route("/create_tables", methods=['POST'])
def createTableRoute():
    try:
        createTables()
        return render_template("index.html", success="Tables successfully created!")
    except:
        return render_template("index.html", error="Error: Tables already exists")

@app.route("/populate_table", methods=['POST'])
def populateTablesRoute():
    populateBankTransactions()
    populateMemberTransactions()
    return render_template("index.html", success="Tables successfully populated with csv data")

@app.route("/view_tables", methods=['POST'])
def viewTablesRoute():
    bT = viewBankTransactions()
    mT = viewMemberTransactions()

    return render_template("view_tables.html", df1 = bT.to_html(), df2 = mT.to_html())

@app.route("/search_member", methods=['POST', 'GET'])
def searchMemberRoute():
    output = request.form.to_dict()
    memberID = output['memberNum']

    df = searchMemberTransactions(memberID)

    session['df1'] = df[0].to_dict('records')
    session['df2'] = df[1].to_dict('records')
    return render_template("member_tables.html", id=memberID, df1 = df[0], df2 = df[1])

@app.route('/process_selected_rows', methods=['POST'])
def process_selected_rows():
    selected_rows_indices_df1 = request.form.getlist('selected_rows_df1')
    selected_rows_indices_df2 = request.form.getlist('selected_rows_df2')

    selected_rows_df1 = [session['df1'][int(index)-1] for index in selected_rows_indices_df1]
    selected_rows_df2 = [session['df2'][int(index)-1] for index in selected_rows_indices_df2]

    df = updateMemberTable(selected_rows_df1, selected_rows_df2)

    return render_template("member_tables.html", id=df[0], df1 = df[1], df2 = df[2])

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port = 5000)

