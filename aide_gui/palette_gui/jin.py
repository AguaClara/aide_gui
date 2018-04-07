from jinja2 import Template

Template().stream(name='foo').dump('hello.html')
