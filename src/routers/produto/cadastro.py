from nicegui import APIRouter, ui
from sqlalchemy import exc, select
from utils import models, db
from utils.utils import handle_upload, validate_type
import asyncio


session = db.new_session()
cadastro = APIRouter()


def search_product(by:str=None, search_criteria:str=None):
    search_result = None
    if not by:
        search_result = session.scalars(select(models.Produto).order_by(models.Produto.description))
    elif by == "price":        
        search_result = session.scalars(select(models.Produto).where(models.Produto.price == search_criteria))
    elif by == "name": 
        search_result = session.scalars(select(models.Produto).where(models.Produto.product_desc.ilike(f'%{search_criteria}%')))            
    return search_result



def render_products(by=None, sc=None):
    
    async def edit_product(row, action:str):
        prod_desc = row['descricao']
        
        if action == "edit":
            ui.navigate.to(f"/produto_edicao/{prod_desc}")
        elif action == "delete":
            await delete_product(prod_desc)        
        return
    

    async def delete_product(prod_desc):
        from os.path import exists
        from os import remove
        
        result = await dialog_delete
        if result == "Sim":
            try:
                produto = session.scalar(select(models.Produto).where(models.Produto.description == prod_desc))
                session.delete(produto)
                ui.notification("Produto excluído com sucesso!", color='positive')
                session.commit()
                nomefoto = produto.picture.split('/')[-1]
                if nomefoto != "sem_foto.png":
                    imgpath = f"img/produtos/{nomefoto}"
                    if exists(imgpath):                    
                        remove(imgpath)
                await asyncio.sleep(1.5)
                ui.navigate.to('/produto_cadastro')
            except Exception as err:
                session.rollback()
                print(err.__repr__())
                ui.notification("Não foi possível excluir o produto", color='negative')
        


    produtos = search_product(by, sc).fetchall()
    
    if not len(produtos) and by is not None:
        ui.notify("Produto não econtrado", color="negative")
        
    prods_columns = [
        {'name': 'descricao', 'label': 'Descrição', 'field': 'descricao', 'required': True, 'sortable': True, 'align': 'left'},
        {'name': 'categoria', 'label': 'Categoria', 'field': 'categoria', 'required': True, 'sortable': True, 'align': 'left'},
        {'name': 'preco', 'label': 'Preço', 'field': 'preco', 'required': True, 'sortable': True, 'align': 'left', ':format': 'value => "R$ " + value.toFixed(2)'},        
        {'name': 'foto', 'label': 'Foto', 'field': 'foto', 'align': 'center'},
        {'name': 'action', 'label': 'Ações', 'field': 'action', 'align': 'center'} 
    ]
    prods_data = []
    for produto in produtos:        
        prods_data.append({
            'descricao': produto.description, 
            'categoria': session.query(models.ProdCategoria.description).filter(models.ProdCategoria.id==produto.category_id).first()[0],
            'preco': produto.price_val, 
            'foto': produto.picture,              
        })
    
    with ui.table(columns=prods_columns, rows=prods_data, row_key='descricao', pagination={'rowsPerPage': 10}).classes("w-5/6") as table:        
        with table.add_slot('top-left'):
            with ui.input(placeholder='Pesquise aqui').props('type=search').bind_value(table, 'filter').add_slot('append'):
                ui.icon('search')
        
        table.add_slot('body-cell-action', """
            <q-td :props="props">
                <q-btn @click="$parent.$emit('edit', props)" icon="build_circle" flat color='cyan-5'>
                    <q-tooltip anchor="top left" :offset="[10, 10]">
                    Editar
                    </q-tooltip>
                </q-btn>                
                <q-btn @click="$parent.$emit('delete', props)" icon="delete" flat color='red-5'>
                    <q-tooltip anchor="top right" :offset="[10, 10]">
                    Remover
                    </q-tooltip>
                </q-btn>
            </q-td>
        """)       
        table.add_slot('body-cell-foto', '''
            <q-td key="foto" :props="props">
                <q-img                
                spinner-color="white"
                :src="props.value"                
                style="height: 50px; width: 50px"
                class="rounded-borders"
                fit="scale-down"
                />
            </q-td>
        ''')
        table.on('edit', lambda msg: edit_product(msg.args['row'], action='edit'))
        table.on('delete', lambda msg: edit_product(msg.args['row'], action='delete'))

    # Modal para confirmação de exclusão
    with ui.dialog() as dialog_delete, ui.card():
        ui.label("Tem certeza que quer excluir o produto?")
        with ui.row():
            ui.button('Sim', on_click=lambda: dialog_delete.submit('Sim'))
            ui.button('Não', on_click=lambda: dialog_delete.submit('Não'))

    return None

@cadastro.page('/produto_cadastro')
def new_product_page(tipo=None, termo=None):    
    
    async def get_action_return():    

        mandatory_values = [
            prod_desc.value is  None, 
            prod_price.value is  None,
            prod_category.value is  None,
            prod_metric.value is  None,
        ]
        if any(mandatory_values):
            ui.notify("Entre com os dados necessários", color="red")
            return      
        
        imgfile = '/images/sem_foto.png' if image.source == ''  else image.source
        produto = models.Produto(
            description = prod_desc.value,
            category_id = prod_category.value,
            metric_id = prod_metric.value,
            price_val = prod_price.value,
            picture = imgfile       
        )
        # Tenta inserir no banco
        try:
            session.add(produto)
            session.commit()
            ui.notify("Produto cadastrado com sucesso!", color="green")
            await asyncio.sleep(1.5)
            ui.navigate.to("/produto_cadastro")
            
        except exc.IntegrityError:            
            session.rollback()
            ui.notify("Já existe Produto cadastrado com o nome informado", color="red")
        except Exception as e:
            session.rollback()
            print("Erro ao tentar cadastrar o produto:", e.__repr__())
            ui.notify("Entre com os dados necessários", color="red") 

    
    ui.colors(primary='#06b6d4')    
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():    
            ui.label("Cadastro de Produto").classes("text-lg font-medium text-stone-500")
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Fazer Pedido', on_click=lambda: ui.navigate.to('/pedido_cadastro'))
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))     
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa')) 

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full"):
            prod_desc = ui.input(label="Nome do produto", placeholder='entre com o nome...', on_change=lambda e: e.value).classes('w-3/5')
            prod_price = (ui.number(
                label="Preço de venda (R$)",                    
                validation={
                            'Entre com valor numérico': lambda v: validate_type(v, float),
                            'Entre com valor positivo': lambda v: v > 0,
                            },
                format='%.2f'
            ).props('mask="#.##" reverse-fill-mask input-class="text-right"'))
        with ui.row().classes("w-full"):
            prod_categories = session.scalars(select(models.ProdCategoria).order_by(models.ProdCategoria.description)).all()
            prod_metrics = session.scalars(select(models.ProdMetrica)).all()
            prod_category = ui.select({p.id:p.description for p in prod_categories}, with_input=True, label="Categoria do Produto").classes('w-60')
            prod_metric = ui.select({m.id:m.description for m in prod_metrics}, with_input=True, label="Unidade de venda").classes('w-60')
        with ui.row().classes("w-full"):     
            ui.label("Foto do produto:").classes("q-field__label no-pointer-events")
            prod_img = (ui.upload(
                                label="Tam. max: 1MB",
                                on_rejected=lambda: ui.notify('Arquivo maior que tamanho máximo permitido!', color='negative'), 
                                max_file_size=1_000_000,
                                max_files=1,
                                on_upload= lambda e: handle_upload(e=e, img_element=image)
                                
                            )
                        .props('accept=".jpeg,.jpg,.png" hint="Mask: #.00"')
                        .classes('max-w-full'))            
            image = ui.interactive_image().classes("border border-grey-600 w-40 h-40").style('border-radius: 10px; background-color: #f1faee;') 
            

    with ui.row():
        ui.button("Cadastrar", on_click=get_action_return).props('color="green"')
        ui.button("Limpar", on_click=lambda: ui.navigate.to('/produto_cadastro')).props('color="grey"')
        
    
    render_products(tipo, termo)