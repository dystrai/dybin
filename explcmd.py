#!/usr/bin/env python3

"""
explcmd: Explica comando com Markdown
"""

from os import environ as vars_amb
from pathlib import Path
import shlex
import sys

try:
    from bs4 import BeautifulSoup
except:
    print('Por favor, instale o módulo bs4!')
    print('Execute: pip3 install bs4')
    sys.exit(1)


try:
    import requests
except:
    print('Por favor, instale o módulo requests!')
    print('Execute: pip3 install requests')
    sys.exit(1)

try:
    from slugify import slugify
except:
    print('Por favor, instale o módulo slugify!')
    print('Execute: pip3 install python-slugify')
    sys.exit(1)


paths = [Path(p) for p in vars_amb['PATH'].split(':')]

def find_cmd_path(comando: str) -> Path:
    for p in paths:
       path = p/comando
       if path.exists():
           return path

    return None     

def md_link(url: str) -> str:
    global resp
    resp = requests.get(url)
    
    if resp.ok:
        if resp.headers['Content-Type'].startswith('text/html;') \
            or (resp.headers['Content-Type'] == 'text/html'):
                
                sopa = BeautifulSoup(resp.text, 'html.parser')
                tag_titulo = sopa.find_all('title')[0]
                titulo = tag_titulo.text
                return f'[{titulo}]({url})'

class Argumento:
    def __init__(self, arg: str, num: int) -> None:
        self.arg = arg if " " not in arg else f"'{arg}'"
        self.num = num
        if len(arg) == 1:
            self.ornamento = '|'
        elif not " " in arg:
            self.ornamento = f'\\{"_"*(len(arg)-2)}/'
        else:
            self.ornamento = f'\\{"_"*(len(arg))}/'
        self.num_centralizado = str(self.num).center(len(self.ornamento), ' ')

    def __str__(self) -> str:
        if ' ' in self.arg:
            return f'"{self.arg}"'
        else:
            return self.arg

def main():

    if len(sys.argv) > 1:
        slug = slugify(' '.join(sys.argv[1:]))
        args = [Argumento(arg, i) for i,arg in enumerate(sys.argv[1:], start=1)]

        cam_arq_md = Path() / 'comandos' / f'{slug}.md'
        cam_arq_saida = cam_arq_md.parent / 'saidas' / f'{slug}.txt'

        dir_name = cam_arq_saida.parent
        dir_name.mkdir(mode=0o750, parents=True, exist_ok=True)

        with cam_arq_saida.open(mode='w', encoding='utf-8') as arq_saida:
            pass

        with cam_arq_md.open(mode='w', encoding='utf-8') as arq_md:
            arq_md.write(f'''\

(comando:{slug})=

# Comando `{' '.join([str(a) for a in args])}`


''')            
            arq_md.write('```'+'\n')
            arq_md.write(' '.join([a.arg for a in args])+'\n')
            arq_md.write(' '.join([a.ornamento for a in args])+'\n')
            arq_md.write(' '.join([str(a.num).center(len(a.ornamento), ' ') for a in args])+'\n')
            arq_md.write('```'+'\n')
            arq_md.write('\n')
            for a in args:
                arq_md.write(f'{a.num}. `{a.arg}`'+'\n')
                arq_md.write('\n')
                arq_md.write(f'{" "*(len(str(a.num))+2)} Explicação'+'\n')
                arq_md.write('\n')

            arq_md.write(f'''

## Saída

```{{literalinclude}} saidas/{slug}.txt
:linenos:
```
''')

            arq_md.write(f'''\

## Referências

''')
            
            # TODO: Detectar se é um comando interno do shell (bash ou zsh)
            # Ver: Linux / Unix Bash Shell List All Builtin Commands
            #      <https://www.cyberciti.biz/faq/linux-unix-bash-shell-list-all-builtin-commands/>
            
            cmd = sys.argv[1]
            urls = [
                f'https://guialinux.uniriotec.br/{cmd}/',
                f'https://man7.org/linux/man-pages/man1/{cmd}.1.html',
            ]
            
            for url in urls:
                link = md_link(url)
                print(url, link)
                if link:    
                    arq_md.write(f'- {link}\n')            
    
if __name__ == '__main__':
    main()


