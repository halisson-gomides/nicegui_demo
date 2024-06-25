from nicegui import events
from nicegui.elements.interactive_image import InteractiveImage


def handle_upload(e: events.UploadEventArguments, img_element:InteractiveImage, imgpath = "img/produtos"):
        '''
        Função para fazer upload de imagem
        '''
        import base64
        from os.path import join
        from os import makedirs
        
        # global imgfile     
        makedirs(imgpath, exist_ok=True)
        data = base64.b64encode(e.content.read())
        img_element.classes(remove="w-40 h-40")
        
        with open(join(imgpath, e.name), 'wb') as f:
            f.write(base64.b64decode(data))
        # img_element.source = f'data:{e.type};base64,{data.decode()}' # data:image/png 
        img_element.source = f"/images/{e.name}"
        e.sender.reset()


def validate_type(x, obj_type):
    try:
        x = obj_type(x)
        return True
    except TypeError:
        return False