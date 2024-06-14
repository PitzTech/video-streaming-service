import pytest
from chat_handler import ChatHandler
from flask_socketio import SocketIO

@pytest.fixture
def socketio():
    return SocketIO()

def test_chat_handler_initialization(socketio):
    handler = ChatHandler(socketio)
    assert handler.socketio == socketio

def test_handle_message(mocker, socketio):
    handler = ChatHandler(socketio)
    mocker.patch.object(handler.socketio, 'emit')
    handler.handle_message('Hello, world!')
    handler.socketio.emit.assert_called_once_with('chat_message', 'Hello, world!')
