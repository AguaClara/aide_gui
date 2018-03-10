from urllib.request import urlopen
import yaml
link = "https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/aide_gui/test_gui/new_form.yaml"

f = urlopen(link)
myfile = f.read()

with open("webpull.yaml", 'w') as outfile:
    yaml.dump(str(myfile), outfile)
