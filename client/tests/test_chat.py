import pytest
from chat import Chat

def test_chat_initialization():
    chat = Chat()
    assert chat.sio.connected

def test_send_message(mocker):
    chat = Chat()
    mocker.patch.object(chat.sio, 'emit')
    chat.send_message('Hello, world!')
    chat.sio.emit.assert_called_once_with('send_message', 'Hello, world!')

def test_handle_message(mocker):
    chat = Chat()
    mocker.patch('builtins.print')
    chat.handle_message('New message')
    print.assert_called_once_with('Mensagem recebida: New message')
