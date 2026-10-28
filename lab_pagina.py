from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)


# Inicializa o banco de dados com dados de exemplo
def init_db():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()

  # Opcional: Apaga a tabela antiga para garantir que a estrutura nova seja aplicada
  cursor.execute("DROP TABLE IF EXISTS users")

  cursor.execute(
      "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username"
      " TEXT, password TEXT, role TEXT)"
  )

  # Inserindo um usuário administrador e um comum
  cursor.execute(
      "INSERT INTO users (id, username, password, role) VALUES (1, 'admin',"
      " 'admin123', 'Administrador do Sistema')"
  )
  cursor.execute(
      "INSERT INTO users (id, username, password, role) VALUES (2, 'user',"
      " 'user123', 'Usuário Comum')"
  )
  conn.commit()
  conn.close()

# Template da Página de Login (Estilizada)
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Login - Laboratório SQLi</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2f, #2a2a40);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            color: #fff;
        }
        .login-card {
            background: #ffffff;
            color: #333;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            width: 350px;
        }
        h2 {
            margin-top: 0;
            color: #1e1e2f;
            text-align: center;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 14px;
        }
        input[type="submit"] {
            width: 100%;
            background: #4f46e5;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        input[type="submit"]:hover {
            background: #4338ca;
        }
        .error-msg {
            margin-top: 15px;
            color: #dc2626;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>Painel de Acesso</h2>
        <form method="POST">
            <div class="form-group">
                <label>Usuário:</label>
                <input type="text" name="username" required autocomplete="off">
            </div>
            <div class="form-group">
                <label>Senha:</label>
                <input type="password" name="password" required>
            </div>
            <input type="submit" value="Entrar">
        </form>
        {% if message %}
            <div class="error-msg">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

# Template da Página de Dashboard (Após o Login)
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Painel - Bem-vindo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f3f4f6;
            margin: 0;
            padding: 40px;
            color: #1f2937;
        }
        .dashboard-container {
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h1 { color: #4f46e5; margin-top: 0; }
        .badge {
            background: #e0e7ff;
            color: #4f46e5;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }
        .logout-btn {
            display: inline-block;
            margin-top: 20px;
            background: #ef4444;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .logout-btn:hover { background: #dc2626; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h1>Painel Administrativo</h1>
        <p>Login efetuado com sucesso!</p>
        <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;">
        <p><strong>Usuário Identificado:</strong> {{ username }}</p>
        <p><strong>Cargo / Nível:</strong> <span class="badge">{{ role }}</span></p>
        <p style="color: #6b7280; font-size: 13px; margin-top: 20px;"><em>Aviso: Esta página confirma que a autenticação (ou o desvio dela via SQLi) foi processada.</em></p>
        <a href="/" class="logout-btn">Sair / Voltar</a>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():
  message = ""
  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # VULNERABILIDADE MANTIDA: Concatenação direta na query SQL # VULNERABILIDADE CRÍTICA: Concatenação direta de strings na query SQL
    query = (
        "SELECT * FROM users WHERE username = '"
        + username
        + "' AND password = '"
        + password
        + "'"
    )

    print(f"[DEBUG SQLi] {query}")

    try:
      cursor.execute(query)
      user = cursor.fetchone()
      conn.close()

      if user:
        # Renderiza a nova página de dashboard passando os dados recuperados
        return render_template_string(
            DASHBOARD_TEMPLATE, username=user[1], role=user[3]
        )
      else:
        message = "Credenciais inválidas. Tente novamente."
    except Exception as e:
      conn.close()
      message = f"Erro na consulta SQL: {e}"

  return render_template_string(LOGIN_TEMPLATE, message=message)


if __name__ == "__main__":
  init_db()
  app.run(debug=True, port=5000)