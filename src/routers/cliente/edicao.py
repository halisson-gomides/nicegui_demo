from nicegui import APIRouter, ui
from sqlalchemy import select
from utils import db
from utils.models import Cliente
from datetime import datetime
import asyncio

session = db.new_session()
edicao = APIRouter()

@edicao.page('/cliente_edicao/{document}')
def customer_edit_page(document: str):
    
    async def delete_customer():
        result = await dialog
        if result == "Sim":
            try:
                session.delete(cliente)
                ui.notification("Cliente excluído com sucesso!")
                session.commit()
                await asyncio.sleep(2)
                ui.navigate.to('/cliente_pesquisa')
            except Exception as err:
                session.rollback()
                print(err)
                ui.notification("Não foi possível excluir o cliente", color='red')


    def update_customer():
        mandatory_values = [
            name.value,            
            email.value,
            birthdate.value,
            document_id.value
        ]

        if '' in mandatory_values:
            ui.notify("Entre com os dados necessários", color='red')
            return

        # Trata a data de aniversario
        try:
            dt_birth = datetime.strptime(birthdate.value, "%d/%m/%Y")
        except Exception:
            dt_birth = None            

        cliente.nome        = name.value        
        cliente.email       = email.value
        cliente.document    = document_id.value
        cliente.birthdate   = dt_birth
        cliente.phone       = phone.value        
        cliente.instagram   = instagram.value
        cliente.points      = points.value
        session.commit()
        ui.notification("Alteração realizada com sucesso!", color='positive')


    
    cliente = session.scalar(
        select(Cliente).where(Cliente.document == document)
    )
    try:
        dt_birth = cliente.birthdate.date().strftime("%d/%m/%Y")
    except Exception:
        dt_birth = None

    ui.colors(primary='#06b6d4')
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():
            ui.label("Edite os dados do Cliente").classes("text-xl font-medium text-wrap text-stone-500")            
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Fazer Pedido', on_click=lambda: ui.navigate.to('/'))
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full"):
            name = ui.input(value=cliente.nome, label="Nome Completo", placeholder='entre com o nome...', on_change=lambda e: e.value).classes('w-3/5')
            document_id = (ui.input(
                value=cliente.document,
                label="CPF",
                placeholder="entre com o cpf...",
                validation={'Entre com 11 digitos para o cpf': lambda value: len(value) == 14}
            ).props('mask="###.###.###-##"').classes('w-1/3'))
        with ui.row().classes("w-full"):
            with ui.input('Aniversário', value=dt_birth) as birthdate:
                with birthdate.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: menu.open()).classes('cursor-pointer w-3/5')
                with ui.menu() as menu:
                    ui.date().bind_value(birthdate).props('mask="DD/MM/YYYY"')
            ui.label("").classes('w-80')      
            phone = (ui.input(
                value=cliente.phone,
                label="Telefone (WhatsApp)",
                placeholder="entre com o telefone...",
                validation={'Entre com 11 digitos para o telefone': lambda value: len(value) == 18}
            ).props('mask="+55(##)#.####-####"').classes('w-1/3'))    
        with ui.row().classes("w-full"):
            email = ui.input(value=cliente.email, label="E-mail", placeholder="entre com o e-mail...", on_change=lambda e: e.value).classes("w-3/5")
            instagram = ui.input(value=cliente.instagram, label="Instagram", placeholder="entre com o @ do instagram...", on_change=lambda e: e.value).classes("w-1/3")
        with ui.row().classes("w-full"):
            points = ui.input(label='Pontos',
                      placeholder='entre com a quantidade de pontos...',
                      on_change=lambda e: e.value,
                      value=cliente.points).props('mask="####"').classes("w-1/6")
        with ui.row():
            ui.button("Voltar", on_click=lambda: ui.navigate.to('/cliente_pesquisa'), color='grey')
            ui.button("Salvar", on_click=update_customer, color='green')
            ui.button("Excluir", on_click=delete_customer, color='red')

    with ui.dialog() as dialog, ui.card():
        ui.label(f"Tem certeza que quer excluir o cliente: {name.value}?")
        with ui.row():
            ui.button('Sim', on_click=lambda: dialog.submit('Sim'))
            ui.button('Não', on_click=lambda: dialog.submit('Não'))
    
