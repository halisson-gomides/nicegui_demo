from nicegui import APIRouter, ui, events
from sqlalchemy import exc, select, func
from sqlalchemy.orm import joinedload
from utils import models, db
from utils.utils import validate_type, comma_num
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


    class TotalCalc:
        def __init__(self) -> None:            
            self.total_value = 0

        def update(self, data):            
            valor_pedido = 0
            for p in data:
                valor_pedido += p['vtotal']
            self.total_value = valor_pedido



    def add_product():        
        idx = get_prod_idx(produto.value, products)        
        _checklist = [p['id'] == products[idx].id for p in prods_data]
        if any(_checklist):
            ui.notify('Produto já incluído', color='warning')
            return
        
        prods_data.append({
            'id':        products[idx].id, 
            'descricao': products[idx].description,
            'categoria': products[idx].category.description,
            'quantidade':amount.value,
            'preco':     products[idx].price_val,
            'vdesconto': valor_desconto.value,
            'vtotal':    valor.value - valor_desconto.value
        })
        tabela_produtos.update()
        totalPedido.update(prods_data)


    def changevalue(e: events.GenericEventArguments) -> None:        
        for row in prods_data:
            if row['id'] == e.args['id']:
                e.args['vtotal'] = (e.args['quantidade'] * e.args['preco']) - e.args['vdesconto']
                row.update(e.args)
        # ui.notify(f'Updated rows to: {tabela_produtos.rows}')
        tabela_produtos.update()
        totalPedido.update(prods_data)


    def delete(e: events.GenericEventArguments) -> None:        
        prods_data[:] = [row for row in prods_data if row['id'] != e.args['id']]
        # ui.notify(f'Deleted row with ID {e.args["id"]}')
        tabela_produtos.update()

        
    def total_value_calc(p):
        ui.notify(f'Updated rows to: {tabela_produtos.rows}')
        return f"Total do pedido: {p}"


    async def get_action_return():        
        mandatory_values = [
            not len(prods_data), 
            cliente.value == '',
            mesa.value is None,            
        ]
        if any(mandatory_values):
            ui.notify("Entre com os dados necessários", color="negative")
            return  

        # Verifica se existe pedido ativo pra mesa informada
        pedidos_mesa = session.query(models.Pedido).filter(models.Pedido.table_number == int(mesa.value)).all()        
        if len(pedidos_mesa):
            documento = cliente.value.split(" - ")[-1]            
            cli_pedido = session.query(models.Cliente).filter(func.lower(models.Cliente.document) == documento.lower()).one_or_none()
            if cli_pedido:
                reqs = [p.client_id for p in pedidos_mesa]
            else:
                reqs = [p.casual_client.lower() for p in pedidos_mesa]

            if ((cli_pedido and cli_pedido.id in reqs) or 
                (cliente.value.strip().lower() in reqs)):
                nome_cliente = cli_pedido.name.upper() if cli_pedido else cliente.value.strip().upper()
                ui.notify(f"Já existe um pedido aberto para o cliente {nome_cliente}, da mesa {mesa.value:.0f}", color="negative")
                return
        
        documento = cliente.value.split(" - ")[-1]        
        client_request = session.query(models.Cliente).filter(func.lower(models.Cliente.document) == documento.lower()).one_or_none()
        if client_request:
            # Cliente cadastrado
            new_request = models.Pedido.create(
                client          = client_request,                
                table_number    = mesa.value,
                total_value     = totalPedido.total_value,             
            )
        else: # Cliente casual
            new_request = models.Pedido.create(                
                casual_client   = cliente.value,
                table_number    = mesa.value,
                total_value     = totalPedido.total_value,                
            )
        # Adiciona produtos ao pedido
        for p in prods_data:                       
            item = models.PedidoProdutos(                
                product_id      = p['id'],
                product_amount  = p['quantidade'],
                unit_price      = p['preco'],
                discount_value  = p['vdesconto']
            )
            new_request.itens.append(item)
            
        try:
            session.add(new_request)
            session.commit()
            ui.notify("Pedido gerado com sucesso!", color="positive")
            await asyncio.sleep(1.5)
            ui.navigate.to("/pedido_pesquisa")
        except Exception as e:
            session.rollback()
            print("Erro ao tentar gerar o pedido:", e.__repr__())
            ui.notify("Entre com os dados necessários", color="negative")


    
    ui.colors(primary='#06b6d4')
    prods_data = []
    totalPedido = TotalCalc()    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Gerar Pedido").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Pedidos', on_click=lambda: ui.navigate.to('/pedido_pesquisa'))        
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))     
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):    
        with ui.row().classes("w-full"):
            clients = session.scalars(select(models.Cliente)).all()
            client_options = [f'{i.name} - {i.document}' for i in clients]
            cliente = ui.input(label="Cliente", placeholder='Nome do cliente', autocomplete=client_options).classes('w-3/5')
            mesa = (ui.number(
                label="Nº da Mesa", 
                min=0, 
                precision=0,                 
                validation={
                                'Entre com valor inteiro': lambda v: validate_type(v, int),
                                'Entre com valor positivo': lambda v: v >= 0,
                            },
                )).props('input-class="text-right"') 
            #ui.input(label="Nº da Mesa").classes('right')
        with ui.row().classes("w-full items-center"):
            products = session.query(models.Produto).options(joinedload(models.Produto.category)).all() #session.scalars(select(models.Produto)).all()
            prod_descriptions = [f'{i.id:02} - {i.description}' for i in products]            
            produto = ui.select(prod_descriptions, with_input=True, label="Selecione o Produto", on_change=lambda e, p=products: set_prod_price(e, p)).props('clearable').classes('w-80')
            amount = ui.number(label="Quantidade", 
                               precision=0,                             
                               validation={
                                            'Entre com valor inteiro': lambda v: validate_type(v, int),
                                            'Entre com valor positivo': lambda v: v > 0,
                                        },
                                min=1).props('input-class="text-right"')
            
            valor = (ui.number(label="Valor total", prefix="R$ ", format='%.2f')
                    .bind_value_from(target_object=amount, backward=lambda e, p=products: change_price(e, p))
                    .props('input-class="text-right" outlined readonly'))
            valor_desconto = (ui.number(label="Valor de desconto", prefix="R$ ", format='%.2f', min=0.0, precision=2, value=0.0 )
                              .props('input-class="text-right" outlined'))
            
            (ui.button(icon='add_circle', on_click=add_product, color='positive')
            .bind_enabled_from(target_object=produto, target_name='value')
            .tooltip('Adcionar produto').classes('bg-green'))
            
            (ui.button("Fazer Pedido", on_click=get_action_return)
             .bind_visibility_from(target_object=totalPedido, target_name='total_value')
             .props('color="cyan"'))

            (ui.html()
            .bind_content_from(totalPedido, 'total_value', backward=lambda v: f'Total do Pedido: <b>R${comma_num(v, ":.2f")}</b>')
            .classes('q-ml-xl text-stone-500'))
    
    
    prods_columns = [
        {'name': 'descricao', 'label': 'Descrição', 'field': 'descricao', 'required': True, 'align': 'left'},
        {'name': 'categoria', 'label': 'Categoria', 'field': 'categoria', 'required': True, 'align': 'left'},
        {'name': 'quantidade', 'label': 'Qtd.', 'field': 'quantidade', 'required': True, 'align': 'left'},
        {'name': 'preco', 'label': 'Preço Unit.', 'field': 'preco', 'required': True, 'align': 'right', ':format': 'value => "R$ " + value.toFixed(2)'},
        {'name': 'vdesconto', 'label': 'Valor Desconto', 'field': 'vdesconto', 'required': True, 'align': 'right', ':format': 'value => "R$ " + value.toFixed(2)'},
        {'name': 'vtotal', 'label': 'Valor Total', 'field': 'vtotal', 'required': True, 'align': 'right', ':format': 'value => "R$ " + value.toFixed(2)'},
    ]
    
    tabela_produtos = ui.table(columns=prods_columns, rows=prods_data, row_key='descricao', pagination={'rowsPerPage': 10}).classes("w-5/6")
    tabela_produtos.add_slot('header', r'''
        <q-tr :props="props">
            <q-th auto-width />
            <q-th v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.label }}
            </q-th>
        </q-tr>
    ''')
    tabela_produtos.add_slot('body', r'''
        <q-tr :props="props">
            <q-td auto-width >
                <q-btn size="sm" color="warning" round dense icon="delete"
                    @click="() => $parent.$emit('delete', props.row)"
                />
            </q-td>
            <q-td key="descricao" :props="props">
                {{ props.row.descricao }}                
            </q-td>
            <q-td key="categoria" :props="props">
                {{ props.row.categoria }}                
            </q-td>
            <q-td key="quantidade" :props="props">
                {{ props.row.quantidade }}
                <q-popup-edit v-model="props.row.quantidade" v-slot="scope"
                    @update:model-value="() => $parent.$emit('rename', props.row)"
                >
                    <q-input v-model.number="scope.value" type="number" min="1" reverse-fill-mask input-class="text-right" dense autofocus counter @keyup.enter="scope.set" />
                </q-popup-edit>
            </q-td>
            <q-td key="preco" :props="props">
                R${{ props.row.preco.toFixed(2) }}   
            </q-td>
            <q-td key="vdesconto" :props="props">
                R${{ props.row.vdesconto.toFixed(2) }}
                <q-popup-edit v-model="props.row.vdesconto" v-slot="scope"
                    @update:model-value="() => $parent.$emit('rename', props.row)"
                >
                    <q-input v-model.number="scope.value" type="number" min="0.0" reverse-fill-mask prefix="R$" input-class="text-right" dense autofocus counter @keyup.enter="scope.set" />
                </q-popup-edit>
            </q-td>
            <q-td key="vtotal" :props="props">
                R${{ props.row.vtotal.toFixed(2)  }}
            </q-td>
        </q-tr>
    ''')
    tabela_produtos.on('rename', changevalue)
    tabela_produtos.on('delete', delete)