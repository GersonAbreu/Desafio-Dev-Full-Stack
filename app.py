from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados
db = SQLAlchemy(app)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('cadastro.html')

# Rota para registrar um usuário
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Usuário já existe."}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

# Rota para listar usuários
@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users_list), 200

# Rota para a página de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para a página de login
@app.route('/login')
def login():
    return render_template('login.html')

# Rota para a página de listagem
@app.route('/listagem')
def listagem():
    return render_template('listar_usuarios.html')

# Rota para login de usuário
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['username'] = username  # Armazena o nome do usuário na sessão
        return jsonify({"redirect": url_for('user_area')}), 200  # Redireciona para a área do usuário
    return jsonify({"message": "Usuário ou senha inválidos."}), 401

# Rota para a área do usuário
@app.route('/user_area')
def user_area():
    username = session.get('username')
    if username:
        return render_template('user_area.html', username=username)
    return redirect(url_for('login'))

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()  # Cria o banco de dados e as tabelas, se não existirem
    app.run(debug=True)  # Inicia o servidor Flask
