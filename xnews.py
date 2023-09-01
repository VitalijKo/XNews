from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Vitaly'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db'

db = SQLAlchemy(app)


class Category(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    news_list = db.relationship('News', back_populates='category')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Category {self.c_id}: ({self.name})'


class News(db.Model):
    n_id = db.Column(db.Integer, primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey('category.c_id'), nullable=False)
    category = db.relationship('Category', back_populates='news_list')
    title = db.Column(db.String(255), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'News {self.n_id}: ({self.title[:20]}...)'


class Review(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    text = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())


class NewsForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            ),
            Length(
                max=255,
                message='Title is too big!'
            )
        ]
    )
    text = TextAreaField(
        'Text',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            )
        ]
    )
    category = QuerySelectField(
        'Category',
        query_factory=lambda: Category.query.all(),
        validators=[
            DataRequired(
                message='This field can not be empty!'
            )
        ]
    )
    submit = SubmitField('Publish')


class ReviewForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            ),
            Length(
                max=64,
                message='Name is too big!'
            )
        ]
    )
    text = TextAreaField(
        'Text',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            )
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            ),
            Length(
                max=64,
                message='Email is too big!'
            )
        ]
    )
    rating = IntegerField(
        'Rating (1-10)',
        validators=[
            DataRequired(
                message='This field can not be empty!'
            ),
            NumberRange(
                min=0,
                max=10,
                message='Rating should be from 0 to 10!'
            )
        ]
    )
    submit = SubmitField('Make request')


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    news_list = News.query.all()

    context = {'news_list': news_list}

    return render_template('home.html', **context)


@app.route('/category/<int:c_id>')
def get_category(c_id):
    category = Category.query.get(c_id)
    news_list = News.query.filter_by(c_id=c_id).all()

    context = {
        'category': category,
        'news_list': news_list
    }

    return render_template('category.html', **context)


@app.route('/<int:n_id>')
def get_news(n_id):
    news = News.query.get(n_id)

    context = {'news': news}

    return render_template('news.html', **context)


@app.route('/create-news', methods=['GET', 'POST'])
def create_news():
    form = NewsForm()

    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            text=form.text.data,
            c_id=form.data['category'].c_id
        )


        db.session.add(news)
        db.session.commit()

        return redirect(url_for('get_news', n_id=news.n_id))

    context = {'form': form}

    return render_template('create.html', **context)


@app.route('/create-review', methods=['GET', 'POST'])
def create_review():
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            name=form.name.data,
            text=form.text.data,
            email=form.email.data,
            rating=form.rating.data
        )

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('create_review'))

    context = {'form': form}

    return render_template('review.html', **context)


app.run(debug=True)
