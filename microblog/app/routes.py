from flask import render_template, redirect, url_for, request, flash
from flask_login import (
    current_user, 
    login_user, 
    logout_user, 
    login_required
)

from app import app
from app import alquimias



@app.route('/')
def index():
    posts = []
    if current_user.is_authenticated:
        posts = alquimias.get_timeline(limit=5)
        
    return render_template(
        'index.html', 
        user=current_user if current_user.is_authenticated else None,
        posts=posts
    )



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip().lower()
        remember = True if request.form.get('remember') == 'on' else False

        
        user = alquimias.validate_user_password(username, password)

        if user:
            print(f"\n[INFO] Login bem-sucedido para o usuário: {user.username}\n")
            login_user(user, remember=remember)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            print("\n[ERRO] Usuário ou senha inválidos\n")
            flash('Usuário ou senha inválidos. Tente novamente.', 'danger')
            return redirect(url_for('login'))

   
    return render_template('login.html')



@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip().lower()
        
        
        foto = request.form.get('foto', '').strip()
        bio = request.form.get('bio', '').strip()
        remember = True if request.form.get('remember') == 'on' else False

        
        if alquimias.user_exists(username):
            print(f"\n[AVISO] Tentativa de cadastro duplicado: {username}\n")
            flash('Este nome de usuário já está em uso. Por favor, escolha outro.', 'warning')
            return redirect(url_for('cadastro'))

        
        new_user = alquimias.create_user(
            username=username,
            password=password,
            foto=foto if foto else None,
            bio=bio if bio else None,
            remember=remember
        )

        
        login_user(new_user, remember=remember)
        flash('Cadastro concluído com sucesso! Bem-vindo(a)!', 'success')
        return redirect(url_for('index'))

    
    return render_template('cadastro.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))



@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        body = request.form.get('body', '').strip()

        if not body:
            flash('O conteúdo da publicação não pode estar vazio.', 'warning')
            return redirect(url_for('post'))

       
        alquimias.create_post(body=body, author=current_user)
        flash('Publicação enviada com sucesso!', 'success')
        return redirect(url_for('index'))

   
    return render_template('post.html')
