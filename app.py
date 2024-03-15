from flask import Flask, request, render_template, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)

upload_folder = os.path.join('static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = upload_folder

app.secret_key = 'ynna'  # Set secret key untuk session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Periksa apakah username dan password sesuai dengan yang diharapkan
        if username == 'ynna-community' and password == 'shiro-ynna':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    instagram_account = request.form['instagram_account']
    photo1 = request.files['photo1']
    
    photo1_filename = secure_filename(photo1.filename)

    photo1_path = os.path.join(upload_folder, photo1_filename)
    photo1.save(photo1_path)
    
    with open('user_data.txt', 'a') as file:
        file.write(f'{name},{instagram_account},{photo1_filename}\n')
    
    return redirect(url_for('thank_you'))

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    users = []
    try:
        with open('user_data.txt', 'r') as file:
            for line in file:
                # Sesuaikan di sini untuk hanya membaca tiga bagian data
                name, instagram_account, photo1_filename = line.strip().split(',', 2)
                photo1_url = url_for('static', filename='uploads/' + photo1_filename).replace('\\', '/')
                users.append({
                    'name': name, 
                    'instagram_account': instagram_account, 
                    'photo1_url': photo1_url
                })
    except FileNotFoundError:
        pass

    return render_template('admin_dashboard.html', users=users)


@app.route('/admin/reset', methods=['POST'])
def reset_data():
    open('user_data.txt', 'w').close()

    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
