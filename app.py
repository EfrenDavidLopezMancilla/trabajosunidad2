import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'una-clave-secreta-muy-segura'

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crear instancia de SQLAlchemy
db = SQLAlchemy(app)

# Modelo Categoría
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# Modelo Post
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

# Ruta para ver todos los posts
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# Ruta para crear un nuevo post
@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        
        if not title or not content:
            flash('Título y contenido son requeridos', 'error')
            return redirect(url_for('add_post'))
            
        new_post = Post(title=title, content=content, category_id=category_id if category_id else None)
        db.session.add(new_post)
        db.session.commit()
        flash('Post creado exitosamente', 'success')
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

# Ruta para actualizar un post
@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.category_id = request.form.get('category_id')
        db.session.commit()
        flash('Post actualizado exitosamente', 'success')
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('update_post.html', post=post, categories=categories)

# Ruta para eliminar un post
@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post eliminado exitosamente', 'success')
    return redirect(url_for('index'))

# Crear tablas al inicio
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)