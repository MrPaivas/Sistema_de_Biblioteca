import config


class Emprestimo:
    def __init__(self, idempret, nome_obj, id_obj, nome_user, id_user, data):
        """Classe para mostrar historico de emprestimos"""
        self.idemprest = idempret
        self.nome_obj = nome_obj
        self.id_obj = id_obj
        self.nome_user = nome_user
        self.id_user = id_user
        self.data = data


class Devolucoes:
    def __init__(self, codigo, matricula_aluno, data_emp, data_dev):
        self.codigo = codigo
        self.matricula_aluno = matricula_aluno
        self.data_emp = data_emp
        self.data_dev = data_dev


class Emprestar:
    """Classe para receber os atributos de emprestimos, e checar no Banco de Dados"""

    def __init__(self, id_obj, id_user):
        self.id_obj = id_obj
        self.id_user = id_user
        self.objeto_disponivel = False
        self.user_elegivel = False
        self.emprestimos = []  # lista para receber emprestimos

    def checa_obj(self):
        """Checa se temos o numero suficiente de objetos para emprestimo"""
        cursor = config.cnx.cursor()
        query_objeto = "(SELECT quantidade_disp FROM banco_biblioteca.acervo WHERE codigo = %s)"
        id_objeto = (self.id_obj,)
        cursor.execute(query_objeto, id_objeto)

        for (quantidade_disp,) in cursor:
            if quantidade_disp > 0:
                self.objeto_disponivel = True
                return
        cursor.close()

    def checa_user(self):
        """Checa se o user tem menos de 5 emprestimos anteriores"""
        cursor = config.cnx.cursor()
        query_users = "(SELECT livros_emprestados FROM banco_biblioteca.alunos WHERE matricula = %s)"
        query_id = (self.id_user,)
        cursor.execute(query_users, query_id, )

        for (livros_emprestados,) in cursor:
            if livros_emprestados <= 5:
                self.user_elegivel = True
        cursor.close()

    def completa_obj(self):
        """coleta dados relacionados ao id do objeto e adiciona em um LISTA"""
        cursor = config.cnx.cursor()
        query_obj_emp = "(SELECT codigo, nome_do_livro FROM banco_biblioteca.acervo WHERE codigo = %s)"
        id_objeto = (self.id_obj,)

        cursor.execute(query_obj_emp, id_objeto)

        for (codigo, nome_do_livro) in cursor:
            self.emprestimos.append(codigo)
            self.emprestimos.append(nome_do_livro)
        cursor.close()

    def completa_user(self):
        """coleta dados relacionados ao usuario e adiciona em um LISTA"""

        cursor = config.cnx.cursor()
        query_users_emp = "(SELECT matricula, nome FROM banco_biblioteca.alunos WHERE matricula = %s)"
        id_user = (self.id_user,)

        cursor.execute(query_users_emp, id_user)
        for (matricula, nome,) in cursor:
            self.emprestimos.append(matricula)
            self.emprestimos.append(nome)
        cursor.close()

    def envia_emprestimo(self):
        """Envia dados da lista para o DB"""
        self.id_obj = self.emprestimos[0]
        self.nome_obj = self.emprestimos[1]
        self.id_user = self.emprestimos[2]
        self.nome_user = self.emprestimos[3]

        cursor = config.cnx.cursor()
        novo_emprestimo = ("INSERT INTO banco_biblioteca.emprestimos "
                           "(codigo_livro, nome_livro, matricula_aluno, nome_aluno)"
                           "VALUES (%s, %s, %s, %s)")
        data_emprestimo = (self.id_obj, self.nome_obj, self.id_user, self.nome_user)

        cursor.execute(novo_emprestimo, data_emprestimo)

        config.cnx.commit()
        cursor.close()

    def anota_user(self):
        """Soma mais 1 ao compo de emprestimo de usuario"""
        db = config.cnx.cursor()
        update1 = "UPDATE banco_biblioteca.alunos SET livros_emprestados = livros_emprestados +1 WHERE matricula = %s"
        data_usr = (self.id_user,)
        db.execute(update1, data_usr)
        config.cnx.commit()
        db.close()
        return

    def anota_obj(self):
        """subtrai 1 a quantidade de objetos"""
        db = config.cnx.cursor()
        update2 = "UPDATE banco_biblioteca.acervo SET quantidade_disp = quantidade_disp -1 WHERE codigo = %s"
        data_obj = (self.id_obj,)
        db.execute(update2, data_obj)
        config.cnx.commit()
        db.close()
        return


class Devolucao(Emprestar):
    def __init__(self, id_obj, id_user):
        self.data = None
        self.mat = None
        self.cod = None
        self.lista_dev = []
        super().__init__(id_obj, id_user)

    def repor_obj(self):
        """metodo para aumentar quantidade de livros disponiveis no acervo"""
        db = config.cnx.cursor()
        update2 = "UPDATE banco_biblioteca.acervo SET quantidade_disp = quantidade_disp +1 WHERE codigo = %s"
        data_obj = (self.id_obj,)
        db.execute(update2, data_obj)
        config.cnx.commit()
        db.close()
        return

    def repor_user(self):
        """metodo para devolver livro na coluna de emprestimo de usuarios"""
        db = config.cnx.cursor()
        update1 = "UPDATE banco_biblioteca.alunos SET livros_emprestados = livros_emprestados -1 WHERE matricula = %s"
        data_usr = (self.id_user,)
        db.execute(update1, data_usr)
        config.cnx.commit()
        db.close()
        return

    def salva_dev_em_lista(self):
        """metodo copia os dados da table empretimos e passa para table devolucoes"""
        db = config.cnx.cursor()
        leitura = "SELECT codigo_livro, matricula_aluno, data_emprestimo FROM banco_biblioteca.emprestimos WHERE codigo_livro = %s and matricula_aluno = %s"
        busca = (self.id_obj, self.id_user,)
        db.execute(leitura, busca)
        for (codigo_livro, matricula_aluno, data_emprestimo) in db:
            self.lista_dev.append(codigo_livro)
            self.lista_dev.append(matricula_aluno)
            self.lista_dev.append(data_emprestimo)
        db.close()

    def envia_dev(self):
        """Envia Devolucao para DB"""
        db = config.cnx.cursor()
        self.cod = self.lista_dev[0]
        self.mat = self.lista_dev[1]
        self.data = self.lista_dev[2]

        novo_dev = ("INSERT INTO banco_biblioteca.devolucoes "
                    "(codigo, matricula_aluno, data_emp)"
                    "VALUES (%s, %s, %s)")

        val_dev = (self.cod, self.mat, self.data,)
        db.execute(novo_dev, val_dev)
        config.cnx.commit()
        db.close()

    def deleta_emp(self):
        """Deleta emprestimo da tabela de emprestimo"""
        db = config.cnx.cursor()
        db.execute("DELETE FROM banco_biblioteca.emprestimos WHERE codigo_livro = %s and matricula_aluno = %s",
                   (self.id_obj, self.id_user))
        config.cnx.commit()
        db.close()
