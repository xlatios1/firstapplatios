from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
# from flask_uploads import UploadSet, IMAGES, configure_uploads
# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired, FileAllowed
# from wtforms import SubmitField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'super duper ultra secret key'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

# photos = UploadSet('photo', IMAGES)
# configure_uploads(app, photos)

# class UploadForm(FlaskForm):
#     photo = FileField(
#         validators =[
#             FileAllowed(photos, 'Only images are allowed'),
#             FileRequired('File field should not be empty')
#         ]
#     )
#     submit = SubmitField('Upload')

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        
        try:
            if task_content != "":
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            else:
                session['error_msg'] = "Fields are empty! Unable to add!"
                return redirect('/error_page')
        except:
            session['error_msg'] = f"Invalid parameters! { new_task }"
            return redirect('/error_page')

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
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
                return redirect('/')
            else:
                session['error_msg'] = "Fields are empty! Unable to update!"
                return redirect('/error_page')
        except:
            session['error_msg'] = f"Invalid parameters! { request.form['content'] }"
            return redirect('/error_page')

    else:
        return render_template('update.html', task=task)

@app.route('/error_page', methods=['GET', 'POST'])
def error_page():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template('error.html', error_msg = session['error_msg'])
    
    
if __name__ == "__main__":
    app.run(debug=True)
