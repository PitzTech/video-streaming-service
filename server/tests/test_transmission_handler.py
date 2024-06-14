import pytest
from transmission_handler import TransmissionHandler
from flask_socketio import SocketIO

@pytest.fixture
def socketio():
    return SocketIO()

def test_transmission_handler_initialization(socketio):
    handler = TransmissionHandler(socketio)
    assert handler.socketio == socketio

def test_handle_frame(mocker, socketio):
    handler = TransmissionHandler(socketio)
    mocker.patch.object(handler.socketio, 'emit')
    handler.handle_frame(b'some_frame_data')
    handler.socketio.emit.assert_called_once_with('broadcast_frame', b'some_frame_data')
