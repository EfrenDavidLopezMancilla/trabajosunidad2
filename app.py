import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)

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
    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories)

# Ruta para crear un nuevo post
@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        # Obtener los datos del formulario
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')

        # Crear un nuevo post
        new_post = Post(title=title, content=content, category_id=category_id)
        db.session.add(new_post)
        db.session.commit()

        # Redirigir a la página principal
        return redirect(url_for('index'))

    # Si es una solicitud GET, mostrar el formulario para crear un post
    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

# Ruta para actualizar un post
@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)  # Obtener el post o devolver un error 404 si no existe
    if request.method == 'POST':
        # Actualizar los datos del post con los valores del formulario
        post.title = request.form['title']
        post.content = request.form['content']
        post.category_id = request.form.get('category_id')
        db.session.commit()
        return redirect(url_for('index'))

    # Si es una solicitud GET, mostrar el formulario de actualización
    categories = Category.query.all()
    return render_template('update_post.html', post=post, categories=categories)

# Ruta para eliminar un post
@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)  # Obtener el post o devolver un error 404 si no existe
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas en la base de datos (si no existen)
    app.run(debug=True)