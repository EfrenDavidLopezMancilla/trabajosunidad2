import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'una-clave-secreta-muy-segura'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crear instancia de SQLAlchemy
db = SQLAlchemy(app)

# Modelos
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    posts = db.relationship('Post', backref='category_ref', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('post_ref', lazy=True))

# Rutas principales
@app.route('/')
def home():
    return render_template('home.html')

# Rutas para Posts
@app.route('/posts')
def list_posts():
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories)

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
        return redirect(url_for('list_posts'))

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.category_id = request.form.get('category_id')
        db.session.commit()
        flash('Post actualizado exitosamente', 'success')
        return redirect(url_for('list_posts'))

    categories = Category.query.all()
    return render_template('update_post.html', post=post, categories=categories)

@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post eliminado exitosamente', 'success')
    return redirect(url_for('list_posts'))

# Rutas para Categorías
@app.route('/categories')
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name'].strip()
        
        if not name:
            flash('El nombre de la categoría es requerido', 'error')
            return redirect(url_for('add_category'))
            
        if Category.query.filter_by(name=name).first():
            flash('Esta categoría ya existe', 'error')
            return redirect(url_for('add_category'))
            
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('list_categories'))

    return render_template('add_category.html')

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        
        if not name:
            flash('El nombre de la categoría es requerido', 'error')
            return redirect(url_for('edit_category', id=id))
            
        existing = Category.query.filter(Category.id != id, Category.name == name).first()
        if existing:
            flash('Esta categoría ya existe', 'error')
            return redirect(url_for('edit_category', id=id))
            
        category.name = name
        db.session.commit()
        flash('Categoría actualizada exitosamente', 'success')
        return redirect(url_for('list_categories'))

    return render_template('edit_category.html', category=category)

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Verificar si hay posts asociados
    if category.post_ref:
        flash('No se puede eliminar: hay posts asociados a esta categoría', 'error')
        return redirect(url_for('list_categories'))
        
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada exitosamente', 'success')
    return redirect(url_for('list_categories'))

# Inicialización
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)