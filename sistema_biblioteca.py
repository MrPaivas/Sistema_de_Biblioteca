from flask import Flask, render_template, request, redirect

import config
import object_livro
import object_aluno
import object_user
import object_emprest

lista_acervo = []  # lista para receber o conteudo de nossos acervos de livros
lista_aluno = []  # lista para receber as classes de alunos
lista_emprestimos = []  # Lista para receber emprestimos
lista_devolucoes = []  # lista para receber valores de devolucoes
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Página de login"""
    return render_template('index.html', )


@app.route("/login", methods=["GET", "POST"])
def checa_login():
    """checa se o login e a senha estao corretos"""
    email = request.form['email']
    senha = request.form['senha']
    login_attempt = object_user.Users(email, senha)
    login_attempt.autenticar(email, senha)
    if login_attempt.autenticacao == True:
        return redirect('/home')
    else:
        return redirect('/erro')


@app.route("/erro")
def erro():
    """renderiza uma pagina para login incorreto"""
    return render_template('error.html')


@app.route("/home")
def home():
    """Renderiza a pagina principal do sistema"""
    cursor = config.cnx.cursor()
    query = (
        "SELECT nome_do_livro, autor, codigo, edicao, quantidade, quantidade_disp edicao FROM banco_biblioteca.acervo")
    cursor.execute(query)

    for (nome_do_livro, autor, codigo, quantidade, edicao, quantidade_disp) in cursor:
        tabela_acervo = object_livro.Livro(nome=nome_do_livro, autor=autor, codigo=codigo, edicao=edicao,
                                           quantidade=quantidade, quant_disponivel=quantidade_disp)
        lista_acervo.append(tabela_acervo)
    cursor.close()
    return render_template('home.html', livros=lista_acervo)


@app.route("/cadastro_acervo", methods=['GET', 'POST'])
def cadastro_livro():
    """renderiza uma pagina de formulario, que adiciona novos livros"""
    return render_template('cadastro_acervo.html')


@app.route("/cadastrar_acervo", methods=['GET', 'POST'])
def cadastrar_acervo():
    """Recebe Datos de um formulario e chama metodo que os envia para o banco de dados"""
    nome_livro = request.form['nome_do_livro']
    autor = request.form['autor']
    codigo = request.form['codigo']
    edicao = request.form['edicao']
    quantidade = request.form['quantidade']
    quant_disponivel = request.form['quantidade']
    livro_novo = object_livro.Livro(
        nome=nome_livro, autor=autor, codigo=codigo, edicao=edicao,
        quantidade=quantidade, quant_disponivel=quant_disponivel)
    livro_novo.enviar_dados()

    return redirect('/cadastro_acervo')


@app.route("/cadastro_alunos", methods=['GET', 'POST'])
def cadastro_alunos():
    """Renderiza uma pagina que mostra os usuarios e que tem um formulario para se adicionar novos usuarios"""
    cursor = config.cnx.cursor()
    query = ("SELECT nome, telefone, email, matricula, livros_emprestados FROM banco_biblioteca.alunos")
    cursor.execute(query)

    for (nome, telefone, email, matricula, livros_emprestados,) in cursor:
        tabela_alunos = object_aluno.Aluno(nome, telefone, email, matricula, livros_emprestados, )
        lista_aluno.append(tabela_alunos)

    cursor.close()

    return render_template('cadastro_alunos.html', listas=lista_aluno)


@app.route("/cadastrar_aluno", methods=['GET', 'POST'])
def cadastrar_aluno():
    """Pagina recebe dados de um formulario, armazena em uma lista, e redireciona para outra pagina"""
    nome_aluno = request.form['nome1']
    telefone = request.form['fone_number1']
    email = request.form['email1']
    matricula = request.form['matricula1']
    aluno01 = object_aluno.Aluno(nome_aluno, telefone, email, matricula)
    aluno01.enviar_dados()
    return redirect('/cadastro_alunos')


@app.route("/emprestar_livros", methods=['POST', 'GET'])
def emprestar_livros():
    """Renderiza uma pagina com um formulario de emprestimo e uma tabela com historioco de emprestimos"""
    cursor = config.cnx.cursor()
    query = "SELECT num_emp, codigo_livro, nome_livro, matricula_aluno, nome_aluno, data_emprestimo FROM banco_biblioteca.emprestimos"
    cursor.execute(query)
    for (num_emp, codigo_livro, matricula_aluno, nome_livro, data_emprestimo, nome_aluno) in cursor:
        tabela_emprestimo = object_emprest.Emprestimo(
            num_emp, nome_livro, codigo_livro, nome_aluno, matricula_aluno, data_emprestimo)
        lista_emprestimos.append(tabela_emprestimo)
    cursor.close()
    return render_template('emprestar_livros.html', listas=lista_emprestimos)


@app.route("/emprestar", methods=['POST', 'GET'])
def emprestar():
    """Receber dados do livro e do aluno e concluir o emprestimo"""
    matricula = request.form['matricula']
    codigo_livro = request.form['codigo']
    emp = object_emprest.Emprestar(codigo_livro, matricula)
    emp.checa_obj()
    emp.checa_user()

    if emp.objeto_disponivel == True and emp.user_elegivel == True:  # fazer emprestimo
        emp.completa_obj()
        emp.completa_user()
        emp.envia_emprestimo()
        emp.anota_obj()
        emp.anota_user()
        return redirect('/emprestar_livros')
    else:
        return redirect('/erro')


@app.route("/devolver_livros", methods=['POST', 'GET'])
def devolver_livros():
    """Renderiza uma pagina com um formulario de devolucao e uma tabela com historico de devolucoes"""
    cursor = config.cnx.cursor()
    query = "SELECT codigo, matricula_aluno, data_emp, data_dev FROM banco_biblioteca.devolucoes"
    cursor.execute(query)
    for (codigo, matricula_aluno, data_emp, data_dev) in cursor:
        tabela_dev = object_emprest.Devolucoes(codigo, matricula_aluno, data_emp, data_dev)
        lista_devolucoes.append(tabela_dev)
    cursor.close()
    return render_template('devolver_livros.html', listas=lista_devolucoes)


@app.route("/devolvendo", methods=['POST', 'GET'])
def devolvendo():
    """Sub-pagina que recebe os dados do formulario e aciona classe para concluir devolucao"""
    codigo = request.form['codigo']  # variavel que veio do formulario
    matricula = request.form['matricula']  # variavel que veio do formulario
    dev = object_emprest.Devolucao(codigo, matricula)
    dev.salva_dev_em_lista()
    dev.envia_dev()
    dev.repor_obj()
    dev.repor_user()
    dev.deleta_emp()
    return redirect('devolver_livros')


if (__name__) == "__main__":
    app.run(debug=True)
