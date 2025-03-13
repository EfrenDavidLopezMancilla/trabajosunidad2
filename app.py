import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mi_base_de_datos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Para evitar advertencias

# Crear instancia de SQLAlchemy
db = SQLAlchemy(app)

# Definir el modelo de Categoría
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Definir el modelo de Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

# Ruta raíz (página principal)
@app.route('/')
def index():
    posts = Post.query.all()  # Obtener todos los posts
    return render_template('index.html', posts=posts)

# Ruta para actualizar un post
@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get(id)  # Obtener el post por su ID
    if request.method == 'POST':
        # Actualizar los datos del post con los valores del formulario
        post.title = request.form['title']
        post.category_id = request.form['category_id']
        post.content = request.form['content']
        db.session.commit()  # Guardar los cambios en la base de datos
        return redirect(url_for('index'))  # Redirigir a la página principal

    # Si es una solicitud GET, mostrar el formulario de actualización
    categories = Category.query.all()  # Obtener todas las categorías
    return render_template('update_post.html', post=post, categories=categories)

# Ruta para eliminar un post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post = Post.query.get(id)  # Obtener el post por su ID
    if post:
        db.session.delete(post)  # Eliminar el post
        db.session.commit()  # Guardar los cambios en la base de datos
    return redirect(url_for('index'))  # Redirigir a la página principal

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas en la base de datos (si no existen)
    app.run(debug=True)