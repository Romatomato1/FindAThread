import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/FindAThread.ico')
def findAThreadLogo():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'FindAThread.ico', mimetype='image/FindAThreadLogo.jpg')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
   
@app.route('/signup', methods=['POST'])
def signup():

       return render_template('signup.html')

# @app.route('/acctcomplete', methods=['POST'])
# def signup():

#        return render_template('signup.html')


if __name__ == '__main__':
   app.run()
