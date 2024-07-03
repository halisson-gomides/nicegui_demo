from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, registry, mapped_column
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, relationship
from datetime import datetime
from typing import Optional, List

table_registry = registry()


# Define a tabela de clientes
@table_registry.mapped_as_dataclass
class Cliente():
    __tablename__ = 'tab_clients'
    
    id: Mapped[int]               = mapped_column(init=False, autoincrement=True, primary_key=True)
    name: Mapped[str]             = mapped_column(nullable=False)
    email: Mapped[str]            = mapped_column(nullable=False, unique=True)
    document: Mapped[str]         = mapped_column(nullable=False, unique=True)
    birthdate: Mapped[datetime]   = mapped_column(nullable=True)
    phone: Mapped[str]            = mapped_column(nullable=True)
    instagram: Mapped[str]        = mapped_column(nullable=True)
    points: Mapped[int]           = mapped_column(init=False, nullable=False, default=0)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())
    
    requests: Mapped[List["Pedido"]] = relationship(back_populates="client", init=False)

    def __repr__(self):
        return f"Client(id={self.id}, name={self.name})"
    

# Definição da tabela Categoria do produto
@table_registry.mapped_as_dataclass
class ProdCategoria():
    __tablename__ = 'tab_prod_categories'

    id:         Mapped[int]     = mapped_column(init=False, primary_key=True, autoincrement=True) 
    description:Mapped[str]     = mapped_column(nullable=False, unique=True)
    flag_active:Mapped[int]     = mapped_column(init=False, default=1)
    created_at: Mapped[datetime]= mapped_column(init=False, server_default=func.now())

    products:   Mapped[List["Produto"]]= relationship(back_populates='category', default_factory=list, init=False)
    
    def __repr__(self):
        return f"ProdCategoria(id={self.id}, nome={self.description})"
    

# Definição da tabela Metrica de venda do produto
@table_registry.mapped_as_dataclass
class ProdMedida():
    __tablename__ = 'tab_prod_measure'

    id:         Mapped[int]       = mapped_column(init=False, primary_key=True, autoincrement=True) 
    description:Mapped[str]       = mapped_column(nullable=False, unique=True)
    flag_active:Mapped[int]       = mapped_column(init=False, default=1)
    created_at: Mapped[datetime]  = mapped_column(init=False, server_default=func.now())

    products:   Mapped[List["Produto"]]= relationship(back_populates='measure', default_factory=list, init=False)
    
    def __repr__(self):
        return f"ProdMedida(id={self.id}, nome={self.description})"
    

# Definição da tabela associativa Pedido_Produto
@table_registry.mapped_as_dataclass
class PedidoProdutos():
    __tablename__ = "tab_request_products"

    request_id:     Mapped[int]     = mapped_column(ForeignKey("tab_requests.id"), primary_key=True, init=False)
    product_id:     Mapped[int]     = mapped_column(ForeignKey("tab_products.id"), primary_key=True)
    product_amount: Mapped[int]     = mapped_column(nullable=False)
    unit_price:     Mapped[float]   = mapped_column(nullable=False)
    discount_value: Mapped[float]   = mapped_column(nullable=True, default=0)
    created_at:     Mapped[datetime]= mapped_column(init=False, server_default=func.now())

    request:        Mapped["Pedido"]    = relationship(back_populates="itens", init=False)
    product:        Mapped["Produto"]   = relationship(back_populates="requests", init=False)


# Definição da tabela Pedido
@table_registry.mapped_as_dataclass
class Pedido():
    __tablename__ = 'tab_requests'

    id:             Mapped[int]           = mapped_column(init=False, primary_key=True, autoincrement=True)
    client_id:      Mapped[Optional[int]] = mapped_column(ForeignKey('tab_clients.id'), nullable=True, init=False)
    casual_client:  Mapped[Optional[str]] = mapped_column(nullable=True)
    table_number:   Mapped[int]           = mapped_column(nullable=False)        
    total_value:    Mapped[float]         = mapped_column(nullable=False)
    points:         Mapped[int]           = mapped_column(nullable=False, init=False, default=0) # 5% do valor do pedido é convertido em pontos    
    status:         Mapped[int]           = mapped_column(nullable=False, init=False, default=1)
    created_at:     Mapped[datetime]      = mapped_column(init=False, server_default=func.now())

    client:         Mapped[Optional["Cliente"]]    = relationship("Cliente", back_populates="requests", init=False)
    itens:          Mapped[List["PedidoProdutos"]] = relationship(back_populates="request", cascade="all, delete-orphan", default_factory=list, init=False)
    
    def __post_init__(self):
        self.points = int(self.total_value * 0.05)  # 5% do valor do pedido

    @classmethod
    def create(cls, client=None, casual_client=None, table_number=None, total_value=None):
        if client:
            pedido = cls(casual_client=None, table_number=table_number, total_value=total_value)
            pedido.client = client
            return pedido
        elif casual_client:
            return cls(casual_client=casual_client, table_number=table_number, total_value=total_value)
        else:
            raise ValueError("Deve fornecer um cliente ou um nome de cliente casual")
    

# Definição da tabela Produto
@table_registry.mapped_as_dataclass
class Produto():
    __tablename__ = 'tab_products'

    id:          Mapped[int]             = mapped_column(init=False, primary_key=True, autoincrement=True)    
    description: Mapped[str]             = mapped_column(nullable=False, unique=True)
    category_id: Mapped[int]             = mapped_column(ForeignKey('tab_prod_categories.id'), nullable=False)    
    measure_id:  Mapped[int]             = mapped_column(ForeignKey('tab_prod_measure.id'), nullable=False)    
    price_val:   Mapped[float]           = mapped_column(nullable=False)
    picture:     Mapped[str]             = mapped_column(nullable=True)
    created_at:  Mapped[datetime]        = mapped_column(init=False, server_default=   func.now())

    category:    Mapped["ProdCategoria"]        = relationship(back_populates='products', init=False)
    measure:     Mapped["ProdMedida"]           = relationship(back_populates='products', init=False)
    requests:    Mapped[List["PedidoProdutos"]] = relationship(back_populates="product", init=False)
    
    def __repr__(self):
        return f"Produto(id={self.id}, nome={self.description})"