import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configuración de la base de datos
db_uri = os.getenv('DATABASE_URL')
if db_uri and db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    posts = db.relationship('Post', backref='category', lazy=True, cascade='all, delete-orphan')

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

# Rutas principales
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

# Rutas para Posts
@app.route('/posts')
def list_posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        try:
            title = request.form['title'].strip()
            content = request.form['content'].strip()
            category_id = request.form.get('category_id')
            
            if not title or not content:
                flash('Título y contenido son requeridos', 'error')
                return redirect(url_for('add_post'))
                
            new_post = Post(title=title, content=content, category_id=category_id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post creado exitosamente', 'success')
            return redirect(url_for('list_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el post: {str(e)}', 'error')

    categories = Category.query.order_by(Category.name).all()
    return render_template('add_post.html', categories=categories)

@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        try:
            post.title = request.form['title'].strip()
            post.content = request.form['content'].strip()
            post.category_id = request.form.get('category_id')
            db.session.commit()
            flash('Post actualizado exitosamente', 'success')
            return redirect(url_for('list_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el post: {str(e)}', 'error')

    categories = Category.query.order_by(Category.name).all()
    return render_template('update_post.html', post=post, categories=categories)

@app.route('/post/delete/<int:id>')
def delete_post(id):
    try:
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        flash('Post eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el post: {str(e)}', 'error')
    return redirect(url_for('list_posts'))

# Rutas para Categorías
@app.route('/categories')
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        try:
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
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la categoría: {str(e)}', 'error')

    return render_template('add_category.html')

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
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
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la categoría: {str(e)}', 'error')

    return render_template('edit_category.html', category=category)

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    try:
        category = Category.query.get_or_404(id)
        
        # Verificar si hay posts asociados
        if Post.query.filter_by(category_id=id).count() > 0:
            flash('No se puede eliminar: hay posts asociados a esta categoría', 'error')
            return redirect(url_for('list_categories'))
            
        db.session.delete(category)
        db.session.commit()
        flash('Categoría eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la categoría: {str(e)}', 'error')
    return redirect(url_for('list_categories'))

# Inicialización de la base de datos
def init_db():
    with app.app_context():
        db.create_all()
        # Crear algunas categorías por defecto si no existen
        if Category.query.count() == 0:
            default_categories = ['Noticias', 'Tecnología', 'Deportes', 'Entretenimiento']
            for cat_name in default_categories:
                db.session.add(Category(name=cat_name))
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)