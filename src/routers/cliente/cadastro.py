from datetime import datetime
from nicegui import APIRouter, ui
from sqlalchemy import exc
from utils import models
from utils import db

session = db.new_session()
cadastro = APIRouter()

@cadastro.page('/cliente_cadastro')
def new_customer_page():
    
    ui.colors(primary='#06b6d4')    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Cadastro de Cliente").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Gerar Pedido', on_click=lambda: ui.navigate.to('/pedido_cadastro'))
        ui.button('Pedidos', on_click=lambda: ui.navigate.to('/pedido_pesquisa'))
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full"):
            name = ui.input(label="Nome Completo", placeholder='entre com o nome...', on_change=lambda e: e.value).classes('w-3/5')
            document_id = (ui.input(
                label="CPF",
                placeholder="entre com o cpf...",
                validation={'Entre com 11 digitos para o cpf': lambda value: len(value) == 14}
            ).props('mask="###.###.###-##"').classes('w-1/3'))
        with ui.row().classes("w-full"):
            with ui.input('Aniversário') as birthdate:
                with birthdate.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: menu.open()).classes('cursor-pointer w-3/5')
                with ui.menu() as menu:
                    ui.date().bind_value(birthdate).props('mask="DD/MM/YYYY"')
            ui.label("").classes('w-80')      
            phone = (ui.input(
                label="Telefone (WhatsApp)",
                placeholder="entre com o telefone...",
                validation={'Entre com 11 digitos para o telefone': lambda value: len(value) == 18}
            ).props('mask="+55(##)#.####-####"').classes('w-1/3'))    
        with ui.row().classes("w-full"):
            email = ui.input(label="E-mail", placeholder="entre com o e-mail...", on_change=lambda e: e.value).classes("w-3/5")
            instagram = ui.input(label="Instagram", placeholder="entre com o @ do instagram...", on_change=lambda e: e.value).classes("w-1/3")


    def get_action_return():
        mandatory_values = [
            name.value, 
            email.value, 
            document_id.value
        ]
        if '' in mandatory_values:
            ui.notify("Entre com os dados necessários", color="red")
            return

        # Trata a data de aniversario
        try:
            dt_birth = datetime.strptime(birthdate.value, "%d/%m/%Y")
        except Exception:
            dt_birth = None
        
        cliente = models.Cliente(
            name=name.value,
            email=email.value,
            document=document_id.value,
            birthdate=dt_birth,
            phone=phone.value,
            instagram=instagram.value
        )
        # Tenta inserir no banco
        try:
            session.add(cliente)
            session.commit()
            ui.notify("Cadastro realizado com sucesso!", color="green")
        except exc.IntegrityError:            
            session.rollback()
            ui.notify("Já existe Cliente cadastrado com o CPF informado", color="red")
        except Exception as e:
            session.rollback()
            print("Erro ao tentar cadastrar o cliente:", e.__repr__())
            ui.notify("Entre com os dados necessários", color="red")            
        

    with ui.row():
        ui.button("Cadastrar", on_click=get_action_return).props('color="green"')
        ui.button("Limpar", on_click=lambda: ui.navigate.to('/cliente_cadastro')).props('color="grey"')   