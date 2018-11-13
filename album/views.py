from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Photo, photoComment
from flask_login import login_required, current_user
from album import db

# viewModule = Blueprint('viewModule', __name__, static_folder='static', static_url_path='static')
viewModule = Blueprint('viewModule', __name__)


@viewModule.route("/vlist")
@login_required
def vlist():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        paginate = Photo.query.filter_by(
            author_id=current_user.userid).order_by(
                Photo.timestamp.desc()).paginate(
                    page=page, per_page=6, error_out=False)
        myphoto = paginate.items
        return render_template(
            'ViewList.html', photos=myphoto, paginate=paginate)
    else:
        return redirect(url_for('user.html'))


    # 分页设置 https://blog.csdn.net/liuredflash/article/details/79672592
@viewModule.route("/upup/<int:photo_id>")
def upup(photo_id):
    photo = Photo.query.filter_by(id=photo_id).first()
    photo.flag = photo.flag + 1
    db.session.commit()
    return str(photo.flag)
    # 点赞 https: // blog.csdn.net / qq_38677814 / article / details / 79342147


@viewModule.route("/vshow")
def vshow():
    return "图片细节"


@viewModule.route("/addComment/", methods=['GET', 'POST'])
def addComment():
    if request.method == 'POST':
        photoid = request.form['photoid']
        comment = request.form['putComment']
        if len(comment) <= 10:
            return "留言失败！"
        comment = photoComment(photoid=photoid, comment=comment)
        db.session.add(comment)
        db.session.commit()
        return "留言成功！"
    return "留言失败！"
