
from nicegui import APIRouter, ui
from sqlalchemy import select
from utils import models
from utils import db
import asyncio

session = db.new_session()
pesquisa = APIRouter()


def search_customer(by:str=None, search_criteria:str=None):
    search_result = None
    if not by:
        search_result = session.scalars(select(models.Cliente))
    elif by == "document":        
        search_result = session.scalars(select(models.Cliente).where(models.Cliente.document == search_criteria))
    elif by == "name": 
        search_result = session.scalars(select(models.Cliente).where(models.Cliente.nome.ilike(f'%{search_criteria}%')))            
    return search_result
    

def render_clients(by=None, sc=None):
    
    async def edit_client(row, action:str):
        document = row['document']
        # ui.notify(f"Cliente: {row['nome']} | CPF: {document} - {action}")
        if action == "edit":
            ui.navigate.to(f"/cliente_edicao/{document}")
        elif action == "delete":
            await delete_customer(row)
        elif action == "points":
            ui.notify("ainda em construção...", color='warning')
        return
    

    async def delete_customer(client_data):
        
        result = await dialog
        if result == "Sim":
            try:
                cliente = session.scalar(select(models.Cliente).where(models.Cliente.document == client_data['document']))
                session.delete(cliente)
                ui.notification("Cliente excluído com sucesso!", color='positive')
                session.commit()
                await asyncio.sleep(1.5)
                ui.navigate.to('/cliente_pesquisa')
            except Exception as err:
                session.rollback()
                print(err)
                ui.notification("Não foi possível excluir o cliente", color='negative')
        


    clientes = search_customer(by, sc).fetchall()
    
    if not len(clientes) and by is not None:
        ui.notify("Cliente não econtrado", color="negative")
        
    clients_columns = [
        {'name': 'nome', 'label': 'Nome', 'field': 'nome', 'required': True, 'sortable': True, 'align': 'left'},
        {'name': 'document', 'label': 'CPF', 'field': 'document', 'required': True, 'align': 'center'},
        {'name': 'email', 'label': 'E-mail', 'field': 'email', 'required': True, 'align': 'left'},
        {'name': 'phone', 'label': 'Telefone', 'field': 'phone', 'align': 'left'},
        {'name': 'instagram', 'label': 'Instagram', 'field': 'instagram', 'align': 'left'},
        {'name': 'points', 'label': 'Pontos', 'field': 'points', 'align': 'center'},
        {'name': 'action', 'label': 'Ações', 'field': 'action', 'align': 'center'} 
    ]
    clients_data = []
    for cliente in clientes:
        clients_data.append({
            'nome': cliente.nome, 
            'document': cliente.document, 
            'email': cliente.email,
            'phone': cliente.phone,
            'instagram': cliente.instagram,
            'points': cliente.points,            
        })
    
    with ui.table(columns=clients_columns, rows=clients_data, row_key='nome', pagination={'rowsPerPage': 10, 'sortBy': 'nome'}).classes("w-5/6") as table:
        table.add_slot('body-cell-points', '''
            <q-td key="points" :props="props">
                <q-badge :color="props.value < 1 ? 'pink-5' : 'teal-5'">
                    {{ props.value }}
                </q-badge>
            </q-td>
        ''')
        table.add_slot(f'body-cell-action', """
            <q-td :props="props">
                <q-btn @click="$parent.$emit('edit', props)" icon="account_circle" flat color='cyan-5'>
                    <q-tooltip anchor="top left" :offset="[10, 10]">
                    Editar
                    </q-tooltip>
                </q-btn>
                <q-btn @click="$parent.$emit('points', props)" icon="change_circle" flat color='teal-5'>
                    <q-tooltip anchor="top middle" :offset="[20, 20]">
                    Resgatar pontos
                    </q-tooltip>
                </q-btn>
                <q-btn @click="$parent.$emit('delete', props)" icon="delete" flat color='red-5' alt='Editar'>
                    <q-tooltip anchor="top right" :offset="[10, 10]">
                    Remover
                    </q-tooltip>
                </q-btn>
            </q-td>
        """)
        table.on('edit', lambda msg: edit_client(msg.args['row'], action='edit'))
        table.on('points', lambda msg: edit_client(msg.args['row'], action='points'))
        table.on('delete', lambda msg: edit_client(msg.args['row'], action='delete'))
    with ui.dialog() as dialog, ui.card():
        ui.label("Tem certeza que quer excluir o cliente?")
        with ui.row():
            ui.button('Sim', on_click=lambda: dialog.submit('Sim'))
            ui.button('Não', on_click=lambda: dialog.submit('Não'))


@pesquisa.page('/cliente_pesquisa')
def customer_search_form(tipo=None, termo=None) -> None:
    
    ui.colors(primary='#06b6d4')    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Relação de Clientes").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Fazer Pedido', on_click=lambda: ui.navigate.to('/pedido_cadastro'))    
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full"):
            name = ui.input(label="Nome do cliente", placeholder='entre com o nome...', on_change=lambda e: e.value).classes('w-3/5')
            ui.label(" ou ").tailwind('text-center', 'font-bold', 'text-green-600')
            document_id = (ui.input(
                label="CPF",
                placeholder="entre com o cpf...",
                validation={'Entre com 11 digitos para o cpf': lambda value: len(value) == 14}
            ).props('mask="###.###.###-##"').classes('w-1/3'))        

           
    def get_action_return(mode='list_all'):
        if mode == 'search':
            mandatory_values = [
                name.value == '',             
                document_id.value == ''
            ]
            if all(mandatory_values):
                ui.notify("Entre com ao menos um critério de pesquisa", color="negative")
                return
            
            if mandatory_values[0]:
                ui.navigate.to(f'/cliente_pesquisa/?tipo=document&termo={document_id.value}')
            else:
                ui.navigate.to(f'/cliente_pesquisa/?tipo=name&termo={name.value}')
        elif mode == 'list_all':
            ui.navigate.to(f'/cliente_lista/{None}')
        

    with ui.row():
        ui.button("Buscar", on_click=lambda: get_action_return(mode='search')).props('color="green"')
        ui.button("Limpar", on_click=lambda: ui.navigate.to('/cliente_pesquisa')).props('color="grey"')

    render_clients(tipo, termo)
