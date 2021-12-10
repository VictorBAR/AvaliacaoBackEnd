from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

#define a conexao com o DB
engine = create_engine('sqlite:///cadastroUsuario.db', convert_unicode=True)

#inicia sessão com o DB
db_session = scoped_session(sessionmaker(autocommit=False, bind=engine))

# padrão para instanciar a base e permitir as queries com o orm
Base = declarative_base()
Base.query = db_session.query_property()

class Usuario(Base):
    __tablename__ = 'pessoas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), index=True)
    idade = Column(Integer)
    email = Column(String(50))
    senha = Column(String(50))

    def to_json(self): 
        return {'id': self.id, 'nome': self.nome, 'idade': self.idade, 'email': self.email, 'senha': self.senha}

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()    
    

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()