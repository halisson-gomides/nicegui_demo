from nicegui import app, ui
from routers.cliente.cadastro import cadastro as cadastro_cliente
from routers.cliente.pesquisa import pesquisa as pesquisa_cliente
from routers.cliente.edicao import edicao as edicao_cliente
from routers.produto.cadastro import cadastro as cadastro_produto
from routers.produto.edicao import edicao as edicao_produto
from routers.pedido.cadastro import cadastro as cadastro_pedido

app.add_static_files(url_path="/images", local_directory="img/produtos")
app.include_router(cadastro_cliente)
app.include_router(pesquisa_cliente)
app.include_router(edicao_cliente)
app.include_router(cadastro_produto)
app.include_router(edicao_produto)
app.include_router(cadastro_pedido)


ui.colors(primary='#06b6d4')
with ui.header(elevated=True).style('background-color: #f1faee').classes('items-center'):
    with ui.card():
        ui.label("Bem vindo ao Café GG!").classes("text-xl font-medium text-wrap text-stone-500")
        with ui.row():
            ui.label("Por:").classes('text-xs text-stone-500')
            ui.link("Halisson Gomides", "mailto:halisson.gomides@gmail.com").classes('text-sky-500 dark:text-sky-400 text-xs')
    ui.button('Início', on_click=ui.navigate.to('/'))
    ui.button('Fazer Pedido', on_click=lambda: ui.navigate.to('/pedido_cadastro')),
    ui.button('Cadastro', on_click=lambda: ui.navigate.to('/cliente_cadastro'))
    ui.button('Clientes', on_click=lambda: ui.navigate.to('/cliente_pesquisa'))
    ui.button('Produtos', on_click=lambda: ui.navigate.to('/produto_cadastro'))


ui.run(favicon="img/favicon/favicon_02.png", title="Cafeteria", language='pt-BR')