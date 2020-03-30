from pybackup import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Settings.query.get(int(user_id))


class Settings(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    main_dir = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Settings({self.main_dir}, {self.username}, {self.password})"
