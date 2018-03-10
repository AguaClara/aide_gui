from urllib.request import urlopen
import yaml

link = "https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/aide_gui/test_gui/new_form.yaml"

f = urlopen(link)
myfile = f.read()

unform = str(myfile)
start = unform.find('---')
end = unform.find("...")
form = unform[start:end+3]

with open("webpull.txt", 'w') as outfile:
    outfile.write(form)

doc="---\n- flow_rate:\n    name : Flow Rate (L/s)\n    default : 34\n    type : string\n    options : null\n- sed_tank_length:\n    name : Sed tank length (m)\n    default : null\n    type : dropdown\n    options : [2, 4, 5]\n- blablabla:\n    name : Hi There!\n    default : 56\n    type : spinnerFloat\n    options: [1, 1, 10]\n- snow:\n    name: just inputs\n    default: 34\n    type: dropdown\n    options: [10, 20, 30]\n..."

don=yaml.load(doc)
