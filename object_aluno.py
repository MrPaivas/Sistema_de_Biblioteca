import config


class Aluno():
    """Classe que recebe os atributos de Alunos"""

    def __init__(self, nome_aluno="", telefone="", email="", matricula="", livros_emprestados=""):

        self.nome_aluno = nome_aluno
        self.telefone = telefone
        self.email = email
        self.matricula = matricula
        self.aluno_elegivel = False
        self.livros_emprestados = livros_emprestados
    def enviar_dados(self):
        self.cursor = config.cnx.cursor()
        self.novo_livro = ("INSERT INTO banco_biblioteca.alunos"
                           "(nome, telefone, email, matricula)"
                           "VALUES (%s, %s, %s, %s)")
        self.data_livro = (self.nome_aluno, self.telefone, self.email, self.matricula,)

        self.cursor.execute(self.novo_livro, self.data_livro)
        config.cnx.commit()
        self.cursor.close()

    def checa_aluno(self):
        cursor = config.cnx.cursor()
        query = "SELECT livros_emprestados, matricula FROM banco_biblioteca.alunos WHERE livros_emprestados LIKE (%s) OR matricula LIKE (%s)"

        data_busca = (self.livros_emprestados, self.matricula,)
        cursor.execute(query, data_busca)
        for (livros_emprestados, matricula) in cursor:
            if matricula == self.matricula and livros_emprestados <= 5:
                self.aluno_elegivel = True
            else:
                self.aluno_elegivel = False
            return

        cursor.close()
