from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from utils.models import table_registry
from utils.models import ProdCategoria, ProdMetrica

def connect(pathdbfile="data"):
    conn_uri = f'sqlite:///{pathdbfile}/appdatabase.db'
    return create_engine(conn_uri)


def new_session():
    engine = connect()
    table_registry.metadata.create_all(engine)
    return Session(engine)


@event.listens_for(ProdCategoria.__table__, 'after_create')
def prd_cat_initial_inserts(target, connection, **kw):
    session = Session(connection)
    categories = ['Bebidas', 'Lanches', 'Refeições', 'Salgados', 'Sobremesas']
    for item in categories:
        session.add(ProdCategoria(description=item))    
    session.commit()


@event.listens_for(ProdMetrica.__table__, 'after_create')
def prd_metr_initial_inserts(target, connection, **kw):
    session = Session(connection)
    metrics = ['un', 'kg', 'porção']
    for item in metrics:
        session.add(ProdMetrica(description=item))    
    session.commit()