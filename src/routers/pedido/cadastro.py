from nicegui import APIRouter, ui
from sqlalchemy import exc, select
from utils import models, db
from utils.utils import validate_type
import asyncio

session = db.new_session()
cadastro = APIRouter()

@cadastro.page('/pedido_cadastro')
def new_request_page(tipo=None, termo=None):

    def get_prod_idx(value, products):
        id = (value.split(" - ")[0]
                                .lstrip("0")
                                .rstrip(" "))
        lst_pos = [p.id == int(id) for p in products]
        idx = lst_pos.index(max(lst_pos))
        return idx
    
    
    def set_prod_price(e, products):
        if e.value:     
            idx = get_prod_idx(e.value, products)
            amount.value = 1
            valor.value = products[idx].price_val


    def change_price(e, products):
        if produto.value and amount.value:            
            idx = get_prod_idx(produto.value, products)
            return products[idx].price_val * int(e)
        return 0.0



    ui.colors(primary='#06b6d4')    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Gerar Pedido").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))        
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))     
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):    
        with ui.row().classes("w-full"):
            clients = session.scalars(select(models.Cliente)).all()
            client_options = [f'{i.nome} - {i.document}' for i in clients]
            cliente = ui.input(label="Cliente", placeholder='Nome do cliente', autocomplete=client_options).classes('w-3/5')
            desk = ui.input(label="Nº da Mesa").classes('right')
        with ui.row().classes("w-full items-center"):
            products = session.scalars(select(models.Produto)).all()
            prod_descriptions = [f'{i.id:02} - {i.description}' for i in products]            
            produto = ui.select(prod_descriptions, with_input=True, label="Selecione o Produto", on_change=lambda e, p=products: set_prod_price(e, p)).props('clearable').classes('w-80')
            amount = ui.number(label="Quantidade", 
                               precision=0, 
                            #    on_change=lambda e: valor.set_value(e.value), 
                               format='%.0f', 
                               validation={
                                            'Entre com valor inteiro': lambda v: validate_type(v, int),
                                            'Entre com valor positivo': lambda v: v > 0,
                                        },
                                min=1).props('input-class="text-right"')
            valor = (ui.number(label="Valor total", prefix="R$ ", format='%.2f')
                     .bind_value_from(target_object=amount, backward=lambda e, p=products: change_price(e, p))
                     .props('input-class="text-right" outlined readonly'))
            ui.button(icon='add_circle', on_click=lambda: ui.notify("adicionar ao pedido"), color='positive')