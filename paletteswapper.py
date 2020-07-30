import PySimpleGUI as sg
from PIL import Image
import paletteswapper_back as psb
import json
import os



def channelstring(channel):
    if channel < 16:
        return '0' + str(hex(channel))[2:]
    else:
        return str(hex(channel))[2:]

def colorstring(color):
    return f'#{channelstring(color[0])}{channelstring(color[1])}{channelstring(color[2])}'

def contrasting_color(color):
    if int(color[0]) + int(color[1]) + int(color[2]) < 220:
        return 'white'
    else:
        return 'black'

def preview_button(color):
    return sg.Button(button_text='Preview color', enable_events=True, key=buildkey(color, 'previewbutton'))

def colorline(origcolor):
    return sg.Column([[stablecolor(origcolor)] + changingcolor(origcolor) + [preview_button(origcolor), reset_button(origcolor)]],
                     background_color=(colorstring(origcolor)), key=buildkey(origcolor))

def reset_button(origcolor):
    return sg.Button(button_text='Reset color', enable_events=True, key=buildkey(origcolor, 'resetbutton'))

def stablecolor(color):
    return sg.Text(text=colortext(color), text_color=contrasting_color(color), background_color=(colorstring(color)))

def channelpicker(origcolor, channel):
    channels = {'red':0, 'green':1, 'blue':2, 'alpha':3}
    basevalue = origcolor[channels[channel]]
    return [sg.Text(channel.capitalize(), background_color=colorstring(origcolor),
                    text_color=contrasting_color(origcolor), key=buildkey(origcolor, channel+'text')),
            sg.Spin(list(range(256)), key=buildkey(origcolor, channel+'spin'),
                    initial_value=basevalue, enable_events=True)]

def changingcolor(origcolor):
    layout = channelpicker(origcolor, 'red') + channelpicker(origcolor, 'green') + channelpicker(origcolor, 'blue')
    if len(origcolor) > 3:
        layout.extend(channelpicker(origcolor, 'alpha'))
    return layout

def buildkey(color, identifier=None):
    if identifier:
        return str(color) + identifier
    else:
        return str(color)


def resetbutton():
    pass

def colortext(color):
    text = f'Red: {color[0]}, Green:{color[1]}, Blue: {color[2]}'
    if len(color) > 3:
        text += f', Alpha: {color[3]}'
    return text

def gettup(eventcode):
    return tuple([int(num) for num in eventcode.split(')')[0][1:].split(', ')])

def update_colorline(event, values, window):
    bar = gettup(event)
    if len(bar) == 3:
        newcolor = (values[buildkey(bar, 'redspin')],
                    values[buildkey(bar, 'greenspin')],
                    values[buildkey(bar, 'bluespin')])
        changing = [
            window[buildkey(bar, 'redtext')],
            window[buildkey(bar, 'greentext')],
            window[buildkey(bar, 'bluetext')]]
    else:
        newcolor = (values[buildkey(bar, 'redspin')],
                    values[buildkey(bar, 'greenspin')],
                    values[buildkey(bar, 'bluespin')],
                    values[buildkey(bar, 'alphaspin')])
        changing = [
            window[buildkey(bar, 'redtext')],
            window[buildkey(bar, 'greentext')],
            window[buildkey(bar, 'bluetext')],
            window[buildkey(bar, 'alphatext')]]
    for element in changing:
        element.update(background_color=colorstring(newcolor), text_color=contrasting_color(newcolor))

def reset_color(event, window):
    bar = gettup(event)
    window[buildkey(bar, 'redspin')].update(value=int(bar[0]))
    window[buildkey(bar, 'redtext')].update(background_color=colorstring(bar), text_color=contrasting_color(bar))
    window[buildkey(bar, 'greenspin')].update(value=int(bar[1]))
    window[buildkey(bar, 'greentext')].update(background_color=colorstring(bar), text_color=contrasting_color(bar))
    window[buildkey(bar, 'bluespin')].update(value=int(bar[2]))
    window[buildkey(bar, 'bluetext')].update(background_color=colorstring(bar), text_color=contrasting_color(bar))
    if len(bar) > 3:
        window[buildkey(bar, 'alphaspin')].update(value=int(bar[3]))
        window[buildkey(bar, 'alphatext')].update(background_color=colorstring(bar), text_color=contrasting_color(bar))

def redraw_picture(window, values, pilimg):
    palette = build_palette(values)
    img = psb.fullswap(pilimg, palette)
    img.save('temp.png', compress_level=0)
    window['changed_image'].update('temp.png')

def build_palette(values):
    oldcolors = set()
    for info in values.keys():
        toadd = gettup(info)
        if len(toadd) > 2:
            oldcolors.add(toadd)
    palette = {}
    for color in oldcolors:
        if len(color) == 3:
            palette[color] = [values[buildkey(color, 'redspin')],
                          values[buildkey(color, 'greenspin')],
                          values[buildkey(color, 'bluespin')]]
        else:
            palette[color] = [values[buildkey(color, 'redspin')],
                              values[buildkey(color, 'greenspin')],
                              values[buildkey(color, 'bluespin')],
                              values[buildkey(color, 'alphaspin')]]
    return palette

def save_picture():
    img = Image.open('temp.png')
    path = sg.popup_get_file('Save the new picture where?', save_as=True, default_extension='png')
    img.save(path, compress_level=7)

def save_palette(values):
    palette = {str(k):v for k,v in build_palette(values).items()}
    palettestring = json.dumps(palette, indent=4)
    with open(sg.popup_get_file('Save the palette where?', save_as=True, default_extension='json'), 'w') as f:
        f.write(palettestring)

def reset_all(window, values):
    for color in values.keys():
        reset_color(str(color), window)


def colorbarlist(palette):
    return [[colorline(tuple(col))] for col in palette.keys()]

def redraw_picture_button():
    return sg.Button(button_text='Redraw changed picture', enable_events=True, key='redraw_picture_button')

def reset_all_button():
    return sg.Button(button_text='Reset all colors', enable_events=True, key='reset_all_button')

def save_picture_button():
    return sg.Button(button_text='Save changed picture', enable_events=True, key='save_picture')

def save_palette_button():
    return sg.Button(button_text='Save current palette', enable_events=True, key='save_palette')

def mainloop(window, pilimg):
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break
        if 'spin' in event or 'previewbutton' in event:
            #print('Seen spin or preview')
            update_colorline(event, values, window)
        if 'resetbutton' in event:
            #print('Seen single reset')
            reset_color(event, window)
        if 'redraw_picture_button' in event:
            #print('Seen redraw picture')
            redraw_picture(window, values, pilimg)
        if 'reset_all_button' in event:
            #print('Seen reset all colors')
            reset_all(window, values)
            pass
        if 'save_picture' in event:
            #print('Seen Save picture')
            save_picture()
        if 'save_palette' in event:
            #print('Seen saving a palette')
            save_palette(values)
            pass
    window.close()



def run_safe():
    sg.theme('DarkGrey')
    img = sg.popup_get_file('Pick an image to open', title='Open image')
    pilimg = Image.open(img)
    pilimg.save('temp.png', compress_level=0)
    palette = psb.pil_analysis(pilimg)
    print(palette)
    winlayout = [[sg.Image(img), sg.Image(img, key='changed_image')]] + colorbarlist(palette) + \
                [[redraw_picture_button(), reset_all_button(), save_palette_button(), save_picture_button()]]
    win = sg.Window('Palette Swapper', winlayout)
    mainloop(win, pilimg)
    os.remove('temp.png')

def run():
    try:
        run_safe()
    except Exception as e:
        try:
            os.remove('temp.png')
        except FileNotFoundError:
            pass
        sg.Popup("Something went wrong!", e)

if __name__ == '__main__':
    run()