from prompt_toolkit.styles import Style

style = Style.from_dict({
    'dialog': 'bg:ansired',
    'status': 'bg:ansiblue',
    'separator': 'fg:#333',
    'name': 'bold',
    'cursor': 'bold reverse',
    'message.deleted': '#666 italic',
    'not-searching': '#888888',
})
