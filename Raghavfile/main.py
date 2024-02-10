from flask import Flask
from flask import render_template , request,redirect,url_for, jsonify
import sqlite3 as sql
import operator
import json
import random
global EMAIL_ID
global uitem
app = Flask(__name__,template_folder="templates")
log = sql.connect('Auction.db')

log.execute('create table if not exists user_login (email text, password text)')
log.execute('create table if not exists admin_bidding(id text  primary key, name text, rating integer, min_bidding integer, description text, start_date date, end_date date)')
log.execute('create table if not exists user_bidding(id text,user_name text,item_name text, amount integer)')
emails = ""
@app.route("/")
def main():
    return render_template('first.html')
  
@app.route('/showuserloginpage/')
def cshowloginpage():
   return render_template("signIn.html")

@app.route('/userlogin', methods=["GET","POST"])
def userlogin():
  flag=False
  if request.method == 'POST':
      useremail = request.form['useremail']
      userpassword = request.form['userpassword']
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        cur2 = con.cursor()
        cur.execute('select * from admin_bidding')
        biddings = cur.fetchall()
        cur2.execute('Select email, password from user_login')
        # rows=cur.fetchall()
        # global rows_2
        rows = []
        for i in range(0,len(biddings)):
          rows.append(biddings[i])
        rows_2 = cur2.fetchall()
        for row in rows_2:
           dbemail=row[0]
           dbPass=row[1]
           if dbemail == useremail and dbPass == userpassword:
              flag=True 
              global EMAIL_ID
              EMAIL_ID=dbemail
              break
           else:
              flag=False
  con.commit()
  if(flag==True):
      return render_template('User_bidding_view_page.html', rows=rows)
  else:
      return "<script>alert('User not found!!')</script>"

@app.route('/showNewUserPage')
def userregistration():
  return render_template('User_registration.html')

@app.route('/usersignup', methods=["GET", "POST"])
def usersignup():
  flag = False
  try:
   if request.method == "POST":
    useremail = request.form["useremail"]
    userpassword = request.form["userpassword"]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      cur.execute('Select email from user_login')
      rows = cur.fetchall()
      # return rows
      if len(rows) == 0:
        cur.execute('insert into user_login (email,password) values (?,?)', (useremail, userpassword))
        flag = True
        con.commit()
      else: 
       for i in rows:
        if i != "":
           for j in i:
            if j != useremail:
             cur.execute('insert into user_login (email,password) values (?,?)', (useremail, userpassword))
             flag = True
             con.commit()
            else:
             return "<script>alert('User already exists')</script>"
             break
        else:
          cur.execute('insert into user_login (email,password) values (?,?)', (useremail, userpassword))
          flag = True
          con.commit()
  except:
    con.rollback()
  if flag == True:
    return "<script>alert('User created successfully')</script>"
  else:
    return "Some Error Occured"
      
@app.route('/userforgotpassword')
def userforgotpassword():
  return render_template('User_forgot_password.html')
  
@app.route('/user_forgot_pass', methods=["GET", "POST"])
def userresetpassword():
  flag = False
  global emails
  try:
   if request.method == "POST":
    uemail = request.form["uemail"]
    upass = request.form["upass"]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      cur.execute('Select email from user_login')
      rows = cur.fetchall()
      if(upass != "" or uemail != ""):
       for i in rows:
        for j in i:
          if j == uemail:
            cur.execute("update user_login set password = ? where email = ?", (upass,j))
            flag = True
            con.commit()
            break
      else:
        return "<script>alert('Please enter all the details')</script>"
  except:
    con.rollback()
  if flag == True:
    return "Password updated successfully"
  else:
    return "Email Not found"

@app.route('/user_bidding_add', methods=["GET","POST"])
def user_bidding():
  rows_2 = []
  try:
   if request.method == "POST":
    uid = request.form["id"]
    uitem = request.form["uitem"]
    uitem = uitem[2:-3]
    amount = request.form["amount"]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      cur_2 = con.cursor()
      cur_2.execute('select name from admin_bidding')
      rows_2 = cur_2.fetchall()
      cur.execute('insert into user_bidding (id,user_name,item_name, amount) values (?,?,?,?)', (uid,EMAIL_ID,uitem,amount))
      con.commit()
  except NameError:
    return "Placing Bids not permitted"
  return render_template('User_participate_form.html', rows_2 = rows_2)
@app.route('/display_winner')
@app.route('/display_winner_list_page')
def display_winner_list_page():
  rows = []
  with sql.connect('Auction.db') as con:
    cur = con.cursor()
    cur.execute('select distinct(item_name) from user_bidding')
    rows = cur.fetchall()
  return render_template('Display_Winner.html', rows=rows)

@app.route('/display_winner', methods=["GET", "POST"])
def display_winner():
  if request.method == "POST":
    winner = request.form["winner"]
    x = winner[2:-3]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      cur.execute('select * from user_bidding where item_name = ? order by amount desc', (x,))
      rows = cur.fetchall()
      return render_template('User_bidding.html', rows=rows)
  return "None"

@app.route('/placebid', methods=["GET", "POST"])
def placebid():
  with sql.connect('Auction.db') as con:
    cur = con.cursor()
    rows_2 = []
    cur.execute('select name from admin_bidding')
    rows_2 = cur.fetchall()
  return render_template('User_participate_form.html', rows_2 = rows_2)
    







# Admin code
@app.route('/showadminpage')
def adminpage():
  return render_template('Admin_login.html')
@app.route('/admin_display_options', methods=["GET", "POST"])
def admin_display_options():
  if request.method == "POST":
    aname = request.form["aname"]
    apass = request.form["apass"]
    if(aname == "Admin" and apass == "admin"):
      return render_template("Admin_dashboard_page.html")
    else:
      return "<script>alert('Admin not found!!')</script>"
  return "Done"
@app.route('/admin_bidding_add_page')
def admin_bidding_add_page():
  return render_template('Admin_bidding_add_page.html')
@app.route('/admin_bidding_add', methods=["GET", "POST"])
def admin_bidding_add():
  if request.method == "POST":
    id = request.form["id"]
    name = request.form["name"]
    rate = request.form["rate"]
    bid = request.form["bid"]
    description = request.form["description"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      # cur.execute('insert into user_bidding (id, item_name) values (?,?)',(id,name))
      cur.execute('insert into admin_bidding (id,name,rating,min_bidding,description, start_date, end_date) values (?,?,?,?,?,?,?)', (id, name, rate, bid, description,start_date, end_date))
      con.commit()
  return "<script>alert('Bidding details added successfully')</script>"
@app.route('/admin_bidding_view')
def admin_bidding_view_page():
  with sql.connect('Auction.db') as con:
    cur = con.cursor()
    cur_2 = con.cursor()
    cur_2.execute('select name from admin_bidding')
    rows_2 = cur_2.fetchall()
    cur.execute('select*from admin_bidding')
    biddings = cur.fetchall()
    rows = []
    for i in range(0,len(biddings)):
      rows.append(biddings[i])
    return render_template('Admin_bidding_view_page.html', rows=rows)

@app.route('/admin_bidding_delete_page')
def admin_bidding_delete_page():
  with sql.connect('Auction.db') as con:
    cur = con.cursor()
    cur.execute('select name from admin_bidding')
    rows = cur.fetchall()
  return render_template('Admin_bidding_delete_page.html', rows=rows)

@app.route('/admin_bidding_remove', methods=["GET", "POST"])
def admin_bidding_remove():
  if request.method == "POST":
    remove = request.form['remove']
    remove = remove[2:-3]
    with sql.connect('Auction.db') as con:
      cur = con.cursor()
      cur.execute('delete from admin_bidding where name = ?', (remove,))
      cur.execute('delete from user_bidding where item_name = ?', (remove,))
      con.commit()
  return "<script>alert('Deleted Successfully')</script>"

@app.route('/admin_bidding_update_page')
def admin_bidding_update_page():
  item_names = ["rating", "min_bidding", "description", "start_date", "end_date"]
  # ids = []
  with sql.connect('Auction.db') as con:
    cur = con.cursor()
    cur.execute('select id from admin_bidding')
    ids = cur.fetchall()
    con.commit()
  return render_template('User_bidding_update_page.html', item_names = item_names, ids=ids)

@app.route('/admin_bidding_update', methods=["GET", "POST"])
def admin_bidding_update():
  if request.method == "POST":
    item_name = request.form["item_name"]
    x = request.form["x"]
    id = request.form["id"]
    id = id[2:-3]
    if item_name == "rating":
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        # cur.execute('update user_bidding set item_name = ? where id = ?', (x,id))
        cur.execute('update admin_bidding set rating = ? where id = ?', (x,id))
        con.commit()
      return "<script>alert('Rating has been updated')</script>"
    if item_name == "min_bidding":
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        # cur.execute('update user_bidding set item_name = ? where id = ?', (x,id))
        cur.execute('update admin_bidding set min_bidding = ? where id = ?', (x,id))
        con.commit()
      return "<script>alert('Minimum Bidding price has been updated')</script>"
    if item_name == "description":
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        # cur.execute('update user_bidding set item_name = ? where id = ?', (x,id))
        cur.execute('update admin_bidding set description = ? where id = ?', (x,id))
        con.commit()
      return "<script>alert('Description has been updated')</script>"
    if item_name == "start_date":
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        # cur.execute('update user_bidding set item_name = ? where id = ?', (x,id))
        cur.execute('update admin_bidding set start_date = ? where id = ?', (x,id))
        con.commit()
      return "<script>alert('Start date has been updated')</script>"
    if item_name == "end_date":
      with sql.connect('Auction.db') as con:
        cur = con.cursor()
        # cur.execute('update user_bidding set item_name = ? where id = ?', (x,id))
        cur.execute('update admin_bidding set end_date = ? where id = ?', (x,id))
        con.commit()
      return "<script>alert('End date has been updated')</script>"
  return "None"
      
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)