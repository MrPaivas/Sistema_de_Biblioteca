import config


class Users():
    def __init__(self, email, senha):
        self.email = email
        self.senha = senha
        self.autenticacao = False

    def autenticar(self, login, credencial):
        """Acessa o banco e confere se os valores estao corretos"""
        self.login = login
        self.credencial = credencial
        self.cursor = config.cnx.cursor()
        self.query = ("SELECT email, senha FROM banco_biblioteca.colaboradores")
        self.cursor.execute(self.query)
        for (email, senha) in self.cursor:
            if email == self.login and senha == self.credencial:
                self.autenticacao = True
                return
            else:
                self.autenticacao = False
                return
        self.cursor.close()

