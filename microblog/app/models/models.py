from datetime import datetime, timezone
from typing import List, Optional
from flask_login import UserMixin
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db, login



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    
    foto: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  

    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)         
    
    
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    
    
    posts: Mapped[List['Post']] = relationship(back_populates='author', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<User {self.username}>'



class Post(db.Model):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        index=True, 
        default=lambda: datetime.now(timezone.utc)
    )
    
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

   
    author: Mapped['User'] = relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {self.id}: {self.body[:20]}...>'



@login.user_loader
def load_user(id: str):
    """
    Função utilizada internamente pelo Flask-Login para recarregar
    o objeto de usuário a partir do ID salvo no cookie de sessão.
    """
    return db.session.get(User, int(id))