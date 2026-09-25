from datetime import datetime, timezone
from typing import Optional, List
from app import db
from app.models.models import User, Post


# ==========================================================
# FUNÇÕES DE AUTENTICAÇÃO E USUÁRIO (Páginas 3 e 5)
# ==========================================================

def validate_user_password(username: str, password: str) -> Optional[User]:
    """
    Verifica se o usuário existe e se a senha fornecida confere.
    Retorna o objeto User se autenticado com sucesso, ou None caso contrário.
    """
    # Consulta o usuário pelo username (usando SQLAlchemy 2.0 select)
    query = db.select(User).where(User.username == username)
    user = db.session.scalars(query).first()
    
    # Validação da senha conforme indicado na apostila
    if user and user.password == password:
        return user
    else:
        return None


def user_exists(username: str) -> Optional[User]:
    """
    Verifica se já existe algum usuário cadastrado com o username informado.
    Retorna o objeto User existente ou None caso o nome esteja livre.
    """
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
    """
    Instancia e cadastra um novo usuário no banco de dados.
    Incorpora os campos adicionais de foto e bio exigidos na Seção 3.
    Retorna o novo objeto User persistido.
    """
    if last_login is None:
        last_login = datetime.now(timezone.utc)

    # Criação da instância do modelo
    new_user = User(
        username=username,
        password=password,
        foto=foto if foto else None,
        bio=bio if bio else None,
        last_login=last_login
    )

    try:
        # Adiciona e confirma a transação no banco SQLite
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        # Em caso de erro (ex.: username duplicado), desfaz a operação pendente
        db.session.rollback()
        raise e


# ==========================================================
# FUNÇÕES DE MANIPULAÇÃO DE POSTS (Página 8)
# ==========================================================

def create_post(body: str, author: User) -> Post:
    """
    Cria uma nova publicação vinculada diretamente ao autor informado.
    Graças ao relationship 'author', o ORM preenche automaticamente a FK 'user_id'.
    """
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
    """
    Retorna as publicações mais recentes ordenadas de forma decrescente por data.
    Por padrão, limita aos 5 posts mais recentes para exibição no feed.
    """
    query = db.select(Post).order_by(Post.timestamp.desc()).limit(limit)
    posts = db.session.scalars(query).all()
    return list(posts)