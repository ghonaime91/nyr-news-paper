from datetime import datetime
from app import db

class Role(db.Model):
    __tablename__ = 'role'
    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(50), nullable=False, default="user", unique=True)
    users     = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'user'
    id          = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.String(30), nullable=False)
    last_name   = db.Column(db.String(30), nullable=False)
    email       = db.Column(db.String(255), unique=True, nullable=False)
    password    = db.Column(db.String(255), nullable=False)
    role_id     = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_active   = db.Column(db.Boolean, default=False)
    
    # Comments should remain even if the user is deleted
    comments    = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    
    # Articles should remain even if the user is deleted
    articles    = db.relationship('Article', backref='author', lazy=True, cascade='all, delete-orphan', passive_deletes=True)

class Category(db.Model):
    __tablename__ = 'category'
    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.String(255), nullable=False)
    
    # Articles should remain even if the category is deleted
    articles = db.relationship('Article', backref='category', lazy=True, cascade='all, delete-orphan', passive_deletes=True)

class Article(db.Model):
    __tablename__ = 'article'
    id          = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.Boolean, default=False)
    title       = db.Column(db.Text, nullable=False)
    content     = db.Column(db.Text, nullable=False)
    
    # This column can be NULL if the category or user is deleted
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True) 
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)  
    
    image       = db.Column(db.String(255), nullable=True, default='none')
    audio       = db.Column(db.String(255), nullable=True, default='none')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Comments will be deleted if the article is deleted
    comments = db.relationship('Comment', backref='article', cascade='delete', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comment'
    id          = db.Column(db.Integer, primary_key=True)
    
    # If the user is deleted, set the user_id to NULL instead of deleting the comment
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    
    # If the article is deleted, set the article_id to NULL instead of deleting the comment
    article_id  = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    
    content     = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
