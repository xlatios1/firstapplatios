from flask import Flask, current_app, request, session, Response
from flask import render_template, url_for, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import flash
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'super duper ultra secret key'
app.config['UPLOADED_PHOTOS_DEST'] = 'FLASKINTRODUCTION'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    photo_data = db.Column(db.String(200), default=None)

    def __repr__(self):
        return f'<Task {self.id}>'

class UploadForm(FlaskForm):
    photo = FileField(
        validators =[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField('Upload')

@app.route('/upload_image/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/upload_image/<int:id>', methods=['Get', 'Post'])
def upload_image(id):
    task = Todo.query.get_or_404(id)
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)    
        task.photo_data = url_for('get_file', filename=filename)
        db.session.commit()
        current_app.logger.info(f"Added new item (id={task.id}, photo={task.photo_data})!")
    return render_template('upload_image.html', form=form, id=id, photo_data=task.photo_data)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("this time:" + request.form['btn'])
        if request.form['btn'] == 'Add Task':
            task_content = request.form['content']
            new_task = Todo(content=task_content)
            if task_content != "":
                db.session.add(new_task)
                db.session.commit()
                current_app.logger.info(f"Added new task (id={new_task.id})!")
                return redirect('/')
            else:
                flash('Fields are empty! Unable to add!')
        elif request.form['btn'] == 'New Function':
            flash('Testing')
        else:
            ...    
    try:
        tasks = Todo.query.order_by(Todo.date_created).all()
    except:
        current_app.logger.info(f"Databased Updated, Data has been reset!")
        db.drop_all()
        db.create_all()
        tasks = Todo.query.order_by(Todo.date_created).all()
    
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
@app.route('/delete/<int:id>/<photo_data>')
def delete(id, photo_data=None):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        if photo_data==None:
            current_app.logger.info(f"Deleted item (id={id})!")
            db.session.delete(task_to_delete)
        else:
            current_app.logger.info(f"Deleted photo (id={id}, photo={task_to_delete.photo_data})!")
            task_to_delete.photo_data = None
        db.session.commit()
        
        return redirect('/')
    except:
        session['error_msg'] = "Error in deletion, pls try again!"
        return redirect('/error_page')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        try:
            if request.form['content'] != "":
                task.content = request.form['content']
                db.session.commit()
                current_app.logger.info(f"Updated item (id={id}, content={task.content})!")
                return redirect('/')
            else:
                flash('Fields are empty! Unable to update!')
        except:
            session['error_msg'] = f"Invalid parameters! { request.form['content'] }"
            return redirect('/error_page')

    return render_template('update.html', task=task)

@app.route('/error_page', methods=['GET', 'POST'])
def error_page():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template('error.html', error_msg = session['error_msg'])
    

if __name__ == "__main__":
    app.run(debug=True)
