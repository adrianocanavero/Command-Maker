import PySimpleGUI as sg
import pyperclip
import json
import os

sg.theme('Topanga')

data_path = 'data'
simple_commands_file_path = f'{data_path}/simple_commands.json'

if not os.path.exists(data_path):
    os.makedirs(data_path)

simple_commands_file = ''
simple_commands_list = ''

try:
    if not os.path.exists(simple_commands_file_path):
        simple_commands_file = open(simple_commands_file_path, 'w')
        simple_commands_file.write('[\n\t"bundle exec ruby test_scraper.rb --j"\n]')
        simple_commands_file.close()

    simple_commands_file = open(simple_commands_file_path, 'r')
    simple_commands_list = json.load(simple_commands_file)
except Exception as e:
    print('Hubo un problema cargando los archivos de ./data')
    print(e)
finally:
    simple_commands_file.close()

simple_commands_list.append("ruby test_scrapper.rb --j")

#--------------------------LAYOUTS--------------------------


simple_command_layout = [
    [
        sg.Text("Comando:"),
        sg.Button('+', key='SC_ADD'),
        sg.Button('-', key='SC_REMOVE')
    ],
    [
        sg.Combo(
            simple_commands_list,
            default_value=simple_commands_list[0],
            size=(40,1),
            readonly=True,
            key='SC_COMMAND'
        )
    ],
    [sg.Text("Pegar rows con ids:", key='TEXTO-MEMOS')],
    [sg.Multiline(size=(40,20), key='SC_PARAMS', do_not_clear=False)],
    [sg.Button('Copiar comandos', size=(20,5)), sg.Exit(size=(9,5))]
]

memos_eraser_layout = [
    [sg.Text("ID de la page:"), sg.Input(size=(21,1), key="ME_PAGE_ID", do_not_clear=False)],
    [sg.Text("Pegar rows con ids: ", key= 'TEXTO-ERASER')],
    [sg.Multiline(size=(40,20), key='ME_MEMOS_IDS')],
    [
      sg.Button('Copiar condiciones\n de query', size=(20,5)),
      sg.Exit(key="Exit1", size=(9,5)),
    ]
]

tabs_layout = [ 
    [sg.Tab(title="Simple Command", layout=simple_command_layout)],
    [sg.Tab(title="Memos Eraser", layout=memos_eraser_layout)]
]

window_layout = [ 
    [sg.TabGroup(layout=tabs_layout)]
]

window = sg.Window("FM Command Maker v0.4", grab_anywhere=True)
window.Layout(window_layout)


def generate_simple_commands(values) -> None:
    """Generates simple commands and copies them to the clipboard"""

    rows =  values['SC_PARAMS'].split("\n") 
    command = values['SC_COMMAND'] # comando seleccionado por el user
    command_list = []

    for text in rows:
        code = text.split("'")[1]
        full_command = f"{command} {code}\n"
        command_list.append(full_command)

    final_string = ''.join(command_list)
    pyperclip.copy(final_string)

def generate_memos_eraser(values) -> None:
    """Generates conditions for deleting memos and copies them to the clipboard"""

    ids = values['ME_MEMOS_IDS'].replace("\n", ",")

    if values['ME_PAGE_ID'] == "":
        window['TEXTO-ERASER'].update("Pegar rows con ids: ERROR: falta el page_id!", text_color ='red')
    else:
        page_id = f"igz_page_id = {values['ME_PAGE_ID']}"
        ids_list = f"id in ({ids})"
        condiciones_query = f"{page_id} and action <> 'Deleted' and {ids_list}"

        pyperclip.copy(condiciones_query)
        limpiar_texto(window,"TEXTO-ERASER")
        window['ME_MEMOS_IDS'].update('')

def add_simple_command():
    pass

def remove_simple_command():
    pass

def limpiar_texto(window, text_key):

    window[text_key].update("Pegar rows con ids: ", text_color = "yellow")


while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Exit', 'Exit1'):
        break
    elif event == 'Copiar comandos':
        try:
            generate_simple_commands(values)
            limpiar_texto(window,"TEXTO-MEMOS")
        except IndexError:
            window['TEXTO-MEMOS'].update("Pegar rows con ids: ERROR: Copialas del mysql!", text_color ='red')
    elif event == 'Copiar condiciones\n de query':
        generate_memos_eraser(values)
    elif event == 'SC_ADD':
        add_simple_command()
    elif event == 'SC_REMOVE':
        remove_simple_command()


window.close()
