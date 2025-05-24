import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret-key-default')

# --- Configuración mejorada de PostgreSQL con SSL ---
DATABASE_URL = os.getenv('DATABASE_URL')

# Corregir URL si empieza con "postgres://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Añadir parámetros SSL obligatorios
if DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'sslmode': 'require',
        'sslrootcert': 'cert.pem'  # Opcional para SSL estricto
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelos ---
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    posts = db.relationship('Post', backref='category', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

# --- Verificador de conexión ---
def check_db_connection():
    try:
        db.session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")
        return False

# --- Middleware para verificar conexión ---
@app.before_request
def before_request():
    if not check_db_connection():
        flash("Error de conexión con la base de datos. Intenta más tarde.", "danger")
        return render_template("error.html"), 500

# --- Rutas principales ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/posts')
def list_posts():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        
        if not title or not content:
            flash("Título y contenido son obligatorios", "danger")
            return redirect(url_for('add_post'))

        try:
            new_post = Post(title=title, content=content, category_id=category_id)
            db.session.add(new_post)
            db.session.commit()
            flash("Post creado exitosamente", "success")
            return redirect(url_for('list_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear post: {str(e)}", "danger")

    categories = Category.query.all()
    return render_template('add_post.html', categories=categories)

# ... (Agrega aquí el resto de tus rutas: update_post, delete_post, etc.)

# --- Inicialización de la base de datos ---
def init_db():
    with app.app_context():
        try:
            if check_db_connection():
                db.create_all()
                print("✅ Tablas creadas correctamente")
                
                # Datos iniciales de prueba
                if Category.query.count() == 0:
                    categories = ['Tecnología', 'Deportes', 'Política', 'Entretenimiento']
                    for name in categories:
                        db.session.add(Category(name=name))
                    db.session.commit()
                    print("✅ Datos de prueba insertados")
        except Exception as e:
            print(f"❌ Error al iniciar DB: {str(e)}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)