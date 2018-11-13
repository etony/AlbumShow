# https://github.com/greyli/albumy

from flask import redirect, url_for, flash
from album.login import loginModule
from album.views import viewModule
from album import app

app.register_blueprint(loginModule, url_prefix='/loginModule')
app.register_blueprint(viewModule, url_prefix='/viewModule')


@app.route('/')
def hello_world():
    return redirect(url_for('loginModule.login'))


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('loginModule.login'))


# @app.errorhandler(413)
# def request_entity_too_large(error):
#     flash('文件太大了')
#     return redirect(url_for('loginModule.upload'))

if __name__ == '__main__':
    app.run()
