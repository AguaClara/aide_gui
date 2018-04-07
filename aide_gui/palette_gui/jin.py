from jinja2 import Template, Environment, FileSystemLoader
import os

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return Environment(
        loader=FileSystemLoader(path or './')
    ).get_template(filename).render(context)

context = {
    'name': 'John',
}

result = render('palette.html', context)
print(result)
