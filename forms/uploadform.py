from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from wtforms import SubmitField
from album import app
import os

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.root_path,
                                                  'static/upload')
#app.config['UPLOADED_PHOTOS_DEST'] = 'static/upload'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, size=None)


class uploadForm(FlaskForm):
    photo = FileField(
        u'图片上传',
        validators=[FileAllowed(photos, u'只能上传图片！'),
                    FileRequired(u'文件未选择！')])
    submit = SubmitField('上 传', render_kw={'class': "btn btn-default"})
