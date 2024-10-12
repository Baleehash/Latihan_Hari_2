from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId

app = Flask(__name__)

# Konfigurasi MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost:27017/user_management'  # Sesuaikan dengan konfigurasi MongoDB Anda
app.config['SECRET_KEY'] = 'secretkey'  # Dibutuhkan untuk session

# Setup MongoDB, bcrypt, dan login manager
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Rute untuk halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Mengambil data pengguna dari database
@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data is not None:
        return User(user_data)  # Kembalikan instance dari kelas User
    return None  # Jika tidak ditemukan, kembalikan None


# Kelas User untuk Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.name = user_data["name"]
        self.role = user_data["role"]

# Route untuk registrasi pengguna
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        role = 'user'  # Default role untuk user baru
        
        # Menyimpan data pengguna ke MongoDB
        mongo.db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role
        })
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):
            user_obj = User(user)  # Pastikan ini adalah instance dari User
            login_user(user_obj)
            flash('Login berhasil!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login gagal. Coba lagi.', 'danger')
    
    return render_template('login.html')



# Route untuk logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda berhasil logout.', 'success')
    return redirect(url_for('login'))

# Route untuk halaman profil
@app.route('/profile')
@login_required
def profile():
    user = mongo.db.users.find_one({"email": current_user.email})
    return render_template('profile.html', name=user['name'])


# Route untuk menampilkan semua pengguna (admin only)
@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('profile'))
    
    users = mongo.db.users.find()
    return render_template('users.html', users=users)

# Route untuk edit pengguna (admin only)
@app.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mengedit pengguna.', 'danger')
        return redirect(url_for('profile'))

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    if request.method == 'POST':
        mongo.db.users.update_one({"_id": ObjectId(user_id)}, {
            "$set": {
                "name": request.form['name'],
                "email": request.form['email'],
                "role": request.form['role']
            }
        })
        flash('Pengguna berhasil diperbarui.', 'success')
        return redirect(url_for('users'))

    return render_template('edit_user.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
