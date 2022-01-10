from flask import Flask, render_template, url_for, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import cv2
import os
import os
import numpy as np
# создаем базу через терминал --  python `` from app1 import db ``from app1 import db
# >>> db.create_all()
# >>> exit()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True) # праймари кей означает что поле уникально
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id # указали что при выборе объекта из класса будет выдаваться объект и id


camera = cv2.VideoCapture(0)

def gen_frames():
    # while True:                   ВЫВОД НА САЙТ
    #     success, frame = camera.read()  # read the camera frame
    #
    #     if not success:
    #         break
    #     else:
    #         ret, buffer = cv2.imencode('.jpg', frame)
    #         frame = buffer.tobytes()
    #         yield (b'--frame\r\n'
    #                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    # Motiondetection
    vName = str(datetime.utcnow())
    vName = vName.replace(':', '_')
    vName = 'Cam ' + vName[:19]
    video = camera

    ret, frame1 = video.read()
    ret, frame2 = video.read()
    heigh, width = frame1.shape[:2]
    # image_size = (width, heigh)
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    size = (frame_width, frame_height)
    # fps = 15
    print(heigh, width)

    result = cv2.VideoWriter(vName + '.avi', cv2.VideoWriter_fourcc(*'MJPG'), 24, size)  # write vid
    while video.isOpened():

        result.write(frame1)
        difference = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, threshold = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilate = cv2.dilate(threshold, None, iterations=3)
        contour, _ = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame1, contour, -1, (0, 0, 255), 2)
        cv2.imshow("image", frame1)
        if len(contour) != 0:
            print('movement') # проверка на движение
        # give filename

        # print('movement at ' + vName)

        frame1 = frame2
        ret, frame2 = video.read()
        if cv2.waitKey(40) == ord('q'):
            break

        # просто вывод изображения на страницу сайта
        ret, buffer = cv2.imencode('.jpg', frame1)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # print('page open')


    result.release()
    LName = str(datetime.utcnow())
    LName = vName.replace(':', '_')
    LName = 'Cam ' + vName[:19] + '.avi'
    os.rename('V.avi', LName)

    # Define the codec and create VideoWriter object
    # fourcc = cv2.cv.CV_FOURCC(*'DIVX')
    # out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))





@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cameras')
def about():
    return render_template('cameras.html')

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article) #добавляем объект
            db.session.commit()     #сохраняем объект
            return redirect('/posts')
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template('create_article.html')


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()     #query pozvoliaet obratitsja 4erez model # k baze dannih\ first or all
    return render_template('posts.html', articles=articles)          #articles=articles это для доступа к объекту
                                                            # артиклс по исмени артиклес (первое)

@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)     #query pozvoliaet obratitsja 4erez model # k baze dannih\ first or all
    return render_template('post_detail.html', article=article)


@app.route('/posts/<int:id>/del')
def post_delete(id):
    article = Article.query.get_or_404(id)     #если айди не найден то вылезает ошибка 404

    try:
        db.session.delete(article) # удаляем объект
        db.session.commit()  # сохраняем объект
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()     #сохраняем объект
            return redirect('/posts')
        except:
            return "При добавлении статьи произошла ошибка"
    else:

        return render_template('post_update.html', article=article)


if __name__ == '__main__': #вот это не очень понятно< то-то там для отладки на компе
    app.run()


#@app1.route('/user/<string:name>/<int:id>')

#def user(name, id):
#    return 'user page = ' + name + ', id = ' + str(id)






