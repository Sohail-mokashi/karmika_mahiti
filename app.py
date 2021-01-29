import mysql.connector
import folium
from flask import Flask,request,render_template,session
from opencage.geocoder import OpenCageGeocode
key = 'fc2e8bb5ba6b46da8357e8df2e25e6e9'
geocoder = OpenCageGeocode(key)



mydb=mysql.connector.connect(
    host="localhost",
    db="karmika",
    user="root",
    passwd="sohail"
)
mycursor=mydb.cursor()

app = Flask(__name__)
app.secret_key = "any random string"




@app.route('/')
def home1():
    return render_template("HOME EDIT.html")


@app.route('/find_page')
def find_page():
    return render_template("find.html")


@app.route('/register_page')
def register_page():
    return render_template("REGISTER EDIT.html")


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST' and 'name' in request.form and 'profession' in request.form and 'gender' in request.form and 'phone' in request.form and 'password' in request.form and 'address' in request.form and 'place' in request.form and 'zip' in request.form:
        name1=request.form['name']
        profession1=request.form['profession']
        gender1=request.form['gender']
        phone1=request.form['phone']
        address1=request.form['address']
        place1=request.form['place']
        password1=request.form['password']
        lat1=request.form['lat']
        lan1=request.form['lan']
        zip1=request.form['zip']
        mycursor.execute("SELECT * FROM user_detail WHERE phone_no=%s",(phone1,))
        account = mycursor.fetchone()
        if account:
            info="Account already exist"
        else:
            if lat1=="" or lan1=="" or lat1==0 or lan1==0:
                location=request.form['address']+" "+request.form['place']+" karnataka"+" india "+request.form['zip']
                results = geocoder.geocode(location)
                lat1=results[0]['geometry']['lat']
                lan1=results[0]['geometry']['lng']
            sqlformula="INSERT INTO user_detail (phone_no,full_name,profession,gender,place,address,password,lat,lan,zip) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            mycursor.execute(sqlformula,(phone1,name1,profession1,gender1,place1,address1,password1,lat1,lan1,zip1))
            mydb.commit()
            info="Successfully Registered!"
    elif request.method == 'POST':
        print()
        info="Please fill out the form "
    return render_template("HOME EDIT.html",info=info)

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST' and 'phone' in request.form and 'password' in request.form:
        phone1 = request.form['phone']
        password1= request.form['password']
        mycursor.execute('SELECT * FROM user_detail WHERE phone_no = %s AND password = %s', (phone1, password1,))
        account = mycursor.fetchone()
        if account:
            session['loggedin'] = True
            session['phone'] = account[0]
            return render_template("DISPLAY EDIT.html",account=account)
        else:
            return render_template("HOME EDIT.html",info="INCORRECT PHONE OR PASSWORD")

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('phone', None)
    return render_template("HOME EDIT.html",info="logged out successfully ")


@app.route('/find', methods =['GET', 'POST'])
def find():
    if request.method == 'POST' and 'lat' in request.form and 'lan' in request.form and 'address' in request.form and 'profession' in request.form:
        lat1=request.form['lat']
        lan1=request.form['lan']
        address1=request.form['address']
        profession1=request.form['profession']
        place1=request.form['place']
        if lat1==lan1:
            results1 = geocoder.geocode(address1)
            lat1=results1[0]['geometry']['lat']
            lan1=results1[0]['geometry']['lng']

    mycursor.execute('select full_name,phone_no,lat,lan from user_detail where profession=%s and place=%s',(profession1,place1))
    temp=mycursor.fetchall()
    m = folium.Map(location=[lat1,lan1],width=1250,height=550,zoom_start=14)
    for i in temp:
        name=i[0]
        phone=i[1]
        lat=i[2]
        lan=i[3]
        folium.Marker([lat,lan], popup='name:'+name+'\nphone:'+phone).add_to(m)
    folium.Circle([lat1, lan1],
                  radius=3500
                  ).add_to(m)
    m=m._repr_html_()
    return render_template('map.html',m=m)

@app.route('/update_page',methods =['GET', 'POST'])
def update():
    phone1=request.form['phone']
    mycursor.execute('SELECT * FROM user_detail WHERE phone_no = %s', (phone1,))
    account = mycursor.fetchone()
    return render_template('UPDATE EDIT.html',account=account)


@app.route('/update_profile',methods =['GET', 'POST'])
def profile():
    name1=request.form['name']
    address1=request.form['address']
    place1=request.form['place']
    zip1=request.form['zip']
    password1=request.form['password']
    phone1=request.form['phone']
    mycursor.execute('SELECT address FROM user_detail WHERE phone_no = %s', (phone1,))
    address = mycursor.fetchone()
    if address!=address1:
        address2=address1+" "+place1+" karnataka"+" india "+zip1
        results1 = geocoder.geocode(address2)
        lat1=results1[0]['geometry']['lat']
        lan1=results1[0]['geometry']['lng']
    sql='UPDATE user_detail SET full_name=%s,place=%s,zip=%s,password=%s,address=%s,lat=%s,lan=%s WHERE phone_no=%s'
    mycursor.execute(sql,(name1,place1,zip1,password1,address1,lat1,lan1,phone1,))
    mydb.commit()
    mycursor.execute('SELECT * FROM user_detail WHERE phone_no = %s', (phone1,))
    account = mycursor.fetchone()
    return render_template('DISPLAY EDIT.html',account=account)

@app.route('/delete_profile',methods =['GET', 'POST'])
def delete():
    phone1=request.form['phone']
    sql='DELETE FROM user_detail WHERE phone_no =%s'
    mycursor.execute(sql,(phone1,))
    mydb.commit()
    return render_template('HOME EDIT.html',info="Account Deleted Successfully")




if __name__ == '__main__':
    app.run()