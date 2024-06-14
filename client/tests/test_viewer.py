import pytest
from viewer import Viewer

def test_viewer_initialization():
    viewer = Viewer()
    assert viewer.sio.connected

def test_list_transmissions(mocker):
    viewer = Viewer()
    mocker.patch('builtins.input', return_value='1')
    mocker.patch.object(viewer.sio, 'emit')
    viewer.list_transmissions()
    viewer.sio.emit.assert_called_once_with('join_transmission', '1')

def test_handle_frame(mocker):
    viewer = Viewer()
    mocker.patch('cv2.imshow')
    mocker.patch('cv2.imdecode', return_value='decoded_frame')
    mocker.patch('cv2.waitKey', return_value=ord('q'))
    viewer.handle_frame(b'some_frame_data')
    cv2.imshow.assert_called_once_with('Assistindo', 'decoded_frame')
