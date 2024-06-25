from nicegui import APIRouter, ui
from sqlalchemy import select
from utils.models import Produto, ProdCategoria, ProdMetrica
from utils import db
from datetime import datetime
import asyncio
from utils.utils import handle_upload

session = db.new_session()
edicao = APIRouter()
imgfile = None


@edicao.page('/produto_edicao/{proddesc}')
def product_edit_page(proddesc: str):

    async def delete_product(prod_indentifier):
        from os.path import exists
        from os import remove

        result = await dialog_delete
        if result == "Sim":
            try:
                produto = session.scalar(select(Produto).where(Produto.id == prod_indentifier))
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


    def update_product():
        mandatory_values = [
            prod_desc.value is  None, 
            prod_price.value is  None,
            prod_category.value is  None,
            prod_metric.value is  None,
        ]
        if any(mandatory_values):
            ui.notify("Entre com os dados necessários", color="red")
            return

        produto.description     = prod_desc.value        
        produto.price_val       = prod_price.value
        produto.category_id     = prod_category.value
        produto.metric_id       = prod_metric.value
        produto.picture         = image.source              
        session.commit()
        ui.notification("Alteração realizada com sucesso!", color='positive')


    produto = session.scalar(select(Produto).where(Produto.description == proddesc))
    
    ui.colors(primary='#06b6d4')
    with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
        with ui.card():
            ui.label("Edite os dados do Cliente").classes("text-xl font-medium text-wrap text-stone-500")            
        ui.button('Início', on_click=lambda: ui.navigate.to('/'))
        ui.button('Fazer Pedido', on_click=lambda: ui.navigate.to('/'))
        ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))
        ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
        ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))

    with ui.card().classes("w-5/6"):        
        with ui.row().classes("w-full"):
            prod_desc = ui.input(value=produto.description, label="Nome do produto", placeholder='entre com o nome...', on_change=lambda e: e.value).classes('w-3/5')
            prod_price = (ui.number(
                value=produto.price_val,
                label="Preço de venda (R$)",                
                validation={'Entre com duas casas decimais': lambda value: float(value) > 0},
                format='%.2f'
            ).props('mask="#.##" reverse-fill-mask input-class="text-right"'))
        with ui.row().classes("w-full"):
            prod_categories = session.scalars(select(ProdCategoria).order_by(ProdCategoria.description)).all()
            prod_metrics = session.scalars(select(ProdMetrica)).all()
            prod_category = ui.select({p.id:p.description for p in prod_categories}, with_input=True, label="Categoria do Produto", value=produto.category_id).classes('w-60')
            prod_metric = ui.select({m.id:m.description for m in prod_metrics}, with_input=True, label="Unidade de venda", value=produto.metric_id).classes('w-60')
        with ui.row().classes("w-full"):     
            ui.label("Foto do produto:").classes("q-field__label no-pointer-events")
            prod_img = (ui.upload(
                                label="Tam. max: 1MB",
                                on_rejected=lambda: ui.notify('Arquivo maior que tamanho máximo permitido!', color='negative'), 
                                max_file_size=1_000_000,
                                max_files=1,
                                on_upload=lambda e: handle_upload(e=e, img_element=image),
                            )
                        .props('accept=".jpeg,.jpg,.png" hint="Mask: #.00"')
                        .classes('max-w-full'))            
            image = ui.interactive_image(source=produto.picture).classes("border border-grey-600").style('border-radius: 10px; background-color: #f1faee;')
        with ui.row():
            ui.button("Voltar", on_click=lambda: ui.navigate.to('/produto_cadastro'), color='grey')
            ui.button("Salvar", on_click=update_product, color='green')
            ui.button("Excluir", on_click=lambda: delete_product(produto.id), color='red')

    # Modal para confirmação de exclusão
    with ui.dialog() as dialog_delete, ui.card():
        ui.label("Tem certeza que quer excluir o produto?")
        with ui.row():
            ui.button('Sim', on_click=lambda: dialog_delete.submit('Sim'))
            ui.button('Não', on_click=lambda: dialog_delete.submit('Não'))