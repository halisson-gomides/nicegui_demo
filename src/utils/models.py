from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, registry, mapped_column
from datetime import datetime


table_registry = registry()

# Define a tabela de clientes
@table_registry.mapped_as_dataclass
class Cliente:
    __tablename__ = 'tab_clientes'
    
    id: Mapped[int]               = mapped_column(init=False, autoincrement=True, primary_key=True)
    nome: Mapped[str]             = mapped_column(nullable=False)
    email: Mapped[str]            = mapped_column(nullable=False, unique=True)
    document: Mapped[str]         = mapped_column(nullable=False, unique=True)
    birthdate: Mapped[datetime]   = mapped_column(nullable=True)
    phone: Mapped[str]            = mapped_column(nullable=True)
    instagram: Mapped[str]        = mapped_column(nullable=True)
    points: Mapped[int]           = mapped_column(init=False, nullable=False, default=0)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    

    def __repr__(self):
        return f"Cliente(id={self.id}, nome={self.nome})"


# Definição da tabela Produto
@table_registry.mapped_as_dataclass
class Produto:
    __tablename__ = 'tab_produtos'

    id: Mapped[int]             = mapped_column(init=False, primary_key=True, autoincrement=True)    
    category_id: Mapped[int]    = mapped_column(ForeignKey('tab_prod_categorias.id'), nullable=False)
    description: Mapped[str]    = mapped_column(nullable=False, unique=True)
    picture: Mapped[str]        = mapped_column(nullable=True)
    price_val: Mapped[float]    = mapped_column(nullable=False)
    metric_id: Mapped[int]      = mapped_column(ForeignKey('tab_prod_metricas.id'), nullable=False)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    
    def __repr__(self):
        return f"Produto(id={self.id}, nome={self.description})"


# Definição da tabela Pedido
@table_registry.mapped_as_dataclass
class Pedido:
    __tablename__ = 'tab_pedidos'

    id: Mapped[int]             = mapped_column(init=False, primary_key=True, autoincrement=True)
    req_date: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    table: Mapped[int]          = mapped_column(nullable=False)
    product_id: Mapped[int]     = mapped_column(ForeignKey('tab_produtos.id'), nullable=False)
    total_amount: Mapped[int]   = mapped_column(nullable=False)
    total_value: Mapped[float]  = mapped_column(nullable=False)
    cliente_id: Mapped[int]     = mapped_column(ForeignKey('tab_clientes.id'), nullable=False)
    
    def __repr__(self):
        return f"Pedido(id={self.id}, mesa={self.table})"
    

# Definição da tabela Categoria
@table_registry.mapped_as_dataclass
class ProdCategoria:
    __tablename__ = 'tab_prod_categorias'

    id: Mapped[int]             = mapped_column(init=False, primary_key=True, autoincrement=True) 
    description: Mapped[str]    = mapped_column(nullable=False, unique=True)
    flag_active: Mapped[int]    = mapped_column(init=False, default=1)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    
    def __repr__(self):
        return f"ProdCategoria(id={self.id}, nome={self.description})"
    

# Definição da tabela Metrica
@table_registry.mapped_as_dataclass
class ProdMetrica:
    __tablename__ = 'tab_prod_metricas'

    id: Mapped[int]             = mapped_column(init=False, primary_key=True, autoincrement=True) 
    description: Mapped[str]    = mapped_column(nullable=False, unique=True)
    flag_active: Mapped[int]    = mapped_column(init=False, default=1)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    
    def __repr__(self):
        return f"ProdMetrica(id={self.id}, nome={self.description})"