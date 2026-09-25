from datetime import datetime, timezone
from typing import Optional, List
from app import db
from app.models.models import User, Post



def validate_user_password(username: str, password: str) -> Optional[User]:
    query = db.select(User).where(User.username == username)
    user = db.session.scalars(query).first()
    

    if user and user.password == password:
        return user
    else:
        return None


def user_exists(username: str) -> Optional[User]:
    query = db.select(User).where(User.username == username)
    user = db.session.scalars(query).first()
    return user


def create_user(
    username: str, 
    password: str, 
    foto: Optional[str] = None, 
    bio: Optional[str] = None, 
    remember: bool = False, 
    last_login: Optional[datetime] = None
) -> User:
    if last_login is None:
        last_login = datetime.now(timezone.utc)


    new_user = User(
        username=username,
        password=password,
        foto=foto if foto else None,
        bio=bio if bio else None,
        last_login=last_login
    )

    try:

        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:

        db.session.rollback()
        raise e


def create_post(body: str, author: User) -> Post:
    new_post = Post(
        body=body,
        author=author,
        timestamp=datetime.now(timezone.utc)
    )

    try:
        db.session.add(new_post)
        db.session.commit()
        return new_post
    except Exception as e:
        db.session.rollback()
        raise e


def get_timeline(limit: int = 5) -> List[Post]:
    query = db.select(Post).order_by(Post.timestamp.desc()).limit(limit)
    posts = db.session.scalars(query).all()
    return list(posts)
