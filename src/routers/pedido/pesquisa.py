from nicegui import APIRouter, ui
from utils import models
from utils import db
from utils.utils import validate_type
import asyncio
from sqlalchemy import func
from datetime import datetime

session = db.new_session()
pesquisa = APIRouter()

@pesquisa.page('/pedido_pesquisa')
def request_search_form(termos=None) -> None:

    def render_requests(sc=None):
        async def edit_request(e, action:str):
            id_req = e.args['row']['id']
            
            if action == "edit":
                ui.navigate.to(f"/pedido_edicao/{id_req}")
            elif action == "delete":
                await delete_request(e.args['row'])        
            return
        

        async def delete_request(row:dict) -> None:
            # Modal para confirmar exclusao
            with ui.dialog() as dialog_delete, ui.card():
                _dtPedido = datetime.strptime(row['data'], '%Y-%m-%dT%H:%M:%S')
                ui.label("Tem certeza que deseja apagar o Pedido abaixo?")
                ui.html(f"<h3>Cliente: <b>{row['cliente']}</b> &nbsp;&nbsp;&nbsp;&nbsp; Mesa: <b>{row['mesa']}</b> <br> Data do Pedido: <b>{_dtPedido.strftime('%d/%m/%Y as %H:%M')}</b></h3>")
                with ui.row():
                    ui.button('Sim', on_click=lambda: dialog_delete.submit('Sim'), color='warning')
                    ui.button('Não', on_click=lambda: dialog_delete.submit('Não'), color='warning')
            
            result = await dialog_delete
            if result == "Sim":
                try:
                    request_to_delete = session.query(models.Pedido).filter(models.Pedido.id == int(row['id'])).one_or_none()
                    session.delete(request_to_delete)
                    session.commit()
                    ui.notify("Pedido excluído com sucesso!", color="positive")
                    pedidos_data[:] = [r for r in pedidos_data if r['id'] != row['id']]
                    tabela_pedidos.update()
                except Exception as err:
                    session.rollback()
                    print(err.__repr__())
                    ui.notify("Não foi possível excluir o pedido", color='negative')
                

        
        sc = eval(sc) if sc else None
        
        if sc and validate_type(sc, dict):            
            filter_expression = []
            if sc['cliente'] != '':
                documento = sc['cliente'].split(" - ")[-1]        
                client_request = session.query(models.Cliente).filter(func.lower(models.Cliente.document) == documento.lower()).one_or_none()
                
                if client_request:
                    # Cliente cadastrado                        
                    filter_expression.append(models.Pedido.client == client_request)
                else:
                    # Cliente não cadastrado
                    filter_expression.append(func.lower(models.Pedido.casual_client) == sc['cliente'].lower())                
            if sc['mesa'] and validate_type(sc['mesa'], int):
                filter_expression.append(models.Pedido.table_number == int(sc['mesa']))
            if sc['data'] != '':
                # Trata a data de aniversario
                try:
                    dt_pedido = datetime.strptime(sc['data'], "%d/%m/%Y").date()
                    filter_expression.append(func.DATE(models.Pedido.created_at) == dt_pedido)
                except Exception as err:
                    print(f"Erro ao tentar buscar pela data do pedido: {err.__repr__()}")
                
            if len(filter_expression):
                requests = session.query(models.Pedido).filter(*filter_expression).all()
            else:
                requests = session.query(models.Pedido).all()
           
            if not len(requests):
                ui.notify("Pedido não econtrado", color="negative")
        else:
            requests = session.query(models.Pedido).all()

        pedidos_columns = [
            {'name': 'nome', 'label': 'Cliente', 'field': 'cliente', 'required': True, 'sortable': True, 'align': 'left'},
            {'name': 'mesa', 'label': 'Mesa', 'field': 'mesa', 'required': True, 'align': 'right'},
            {'name': 'data', 'label': 'Data do Pedido', 'field': 'data', 'required': True, 'align': 'left', ':format': 'value => value.substr(8,2) + "/" + value.substr(5,2) + "/" + value.substr(0,4) + " " + value.substr(11,5)'},
            {'name': 'vtotal', 'label': 'Valor Total', 'field': 'vtotal', 'required': True, 'align': 'right', ':format': 'value => "R$ " + value.toFixed(2)'},
            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},            
            {'name': 'action', 'label': 'Ações', 'field': 'action', 'align': 'center'} 
        ]
        pedidos_data = []
        for pedido in requests:        
            pedidos_data.append({
                'id':       pedido.id,
                'cliente':  pedido.client.name if pedido.client else pedido.casual_client, 
                'mesa':     pedido.table_number,
                'data':     pedido.created_at,
                'vtotal':   pedido.total_value, 
                'status':   pedido.status  
            })
        with ui.table(columns=pedidos_columns, rows=pedidos_data, row_key='cliente', pagination={'rowsPerPage': 20, 'sortBy': 'cliente'}).classes("w-5/6") as tabela_pedidos:            
            tabela_pedidos.add_slot('body-cell-status', '''
                <q-td key="points" :props="props">
                    <q-badge :color="props.value < 1 ? 'pink-5' : 'teal-5'">
                        <span v-if="props.value === 1">Aberto</span>
                        <span v-else>Fechado</span>
                    </q-badge>
                </q-td>
            ''')
            tabela_pedidos.add_slot(f'body-cell-action', """
            <q-td :props="props">
                <q-btn @click="$parent.$emit('edit', props)" icon="edit_note" flat color='warning'>
                    <q-tooltip anchor="top left" :offset="[10, 10]">
                    Editar
                    </q-tooltip>
                </q-btn>
                <q-btn @click="$parent.$emit('delete', props)" icon="shopping_cart_checkout" flat color='positive' alt='Concluir'>
                    <q-tooltip anchor="top right" :offset="[20, 20]">
                    Concluir o pedido
                    </q-tooltip>
                </q-btn>        
                <q-btn @click="$parent.$emit('delete', props)" icon="delete" flat color='red-5' alt='Apagar'>
                    <q-tooltip anchor="top right" :offset="[10, 10]">
                    Apagar
                    </q-tooltip>
                </q-btn>
            </q-td>
        """)
        tabela_pedidos.on('delete', lambda msg: edit_request(msg, action='delete'))

     

    def get_action_return() -> None:
        mandatory_values = [
            cliente.value == '',             
            mesa.value is None,
            data_pedido.value == ''
        ]
        
        if all(mandatory_values):
            ui.notify("Entre com ao menos um critério de pesquisa", color="negative")
            return
        criterios = {"cliente": cliente.value, "mesa": mesa.value, "data": data_pedido.value}
        ui.navigate.to(f'/pedido_pesquisa/?termos={criterios}')
        


    ui.colors(primary='#06b6d4')    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Relação de Pedidos").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Gerar Pedido', on_click=lambda: ui.navigate.to('/pedido_cadastro'))           
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full items-center"):
            clients = session.query(models.Cliente).all()
            client_options = [f'{i.name} - {i.document}' for i in clients]
            cliente = ui.input(label="Cliente", placeholder='Nome do cliente', autocomplete=client_options, on_change=lambda e: e.value).classes('w-3/5')
            ui.label(" ou ").tailwind('text-center', 'font-bold', 'text-green-600')
            mesa = (ui.number(
                label="Nº da Mesa", 
                min=0, 
                precision=0,                 
                validation={
                                'Entre com valor inteiro': lambda v: validate_type(v, int),
                                'Entre com valor positivo': lambda v: v >= 0,
                            },
                )).props('input-class="text-right"')    
        with ui.row().classes("w-full"):
            with ui.input('Data do Pedido') as data_pedido:
                with data_pedido.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: menu.open()).classes('cursor-pointer w-3/5')
                with ui.menu() as menu:
                    ui.date().bind_value(data_pedido).props('mask="DD/MM/YYYY"')
            ui.label("").classes('w-80')
    with ui.row():
        ui.button("Buscar", on_click=lambda: get_action_return()).props('color="green"')
        ui.button("Limpar", on_click=lambda: ui.navigate.to('/pedido_pesquisa')).props('color="grey"')

    render_requests(termos)