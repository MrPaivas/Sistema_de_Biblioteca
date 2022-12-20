import config
class Livro():
    """Classe para representar livros"""
    def __init__(self, nome="", autor="", codigo="", edicao="", quantidade="", quant_disponivel=""):
        self.nome_livro = nome
        self.autor = autor
        self.codigo = codigo
        self.edicao = edicao
        self.quantidade = quantidade
        self.acervo = []
        self.quant_disponivel = quant_disponivel
        self.livro_disponivel = False

    def enviar_dados(self):
        """Adiciona dados de livros ao nosso banco de dados"""
        cursor = config.cnx.cursor()
        novo_livro = ("INSERT INTO banco_biblioteca.acervo"
                           "(nome_do_livro, autor, codigo, quantidade, edicao, quantidade_disp)"
                           "VALUES (%s, %s, %s, %s, %s, %s)")
        data_livro = (self.nome_livro, self.autor, self.codigo, self.quantidade, self.edicao, self.quant_disponivel)

        cursor.execute(novo_livro, data_livro)
        config.cnx.commit()
        cursor.close()

    def checa_livro(self):
        """Faz uma verificação no banco se o livro desejado esta disponivel"""
        cursor = config.cnx.cursor()
        query = "SELECT codigo, quantidade FROM banco_biblioteca.acervo WHERE codigo = %s OR quantidade = %s"
        data_busca = (self.codigo, self.quantidade)
        cursor.execute(query, data_busca)
        for (codigo, quantidade) in cursor:
            if codigo == self.codigo and quantidade != 0:
                self.livro_disponivel = True
            else:
                self.livro_disponivel = False
            return

        cursor.close()

