from app import app, db
from app.models.models import User, Post

@app.shell_context_processor
def make_shell_context():
    """
    Registra instâncias no comando 'flask shell' para você
    testar consultas e comandos no terminal sem precisar
    importar 'db', 'User' e 'Post' manualmente toda vez.
    """
    return {
        'db': db,
        'User': User,
        'Post': Post
    }

if __name__ == '__main__':
    app.run()