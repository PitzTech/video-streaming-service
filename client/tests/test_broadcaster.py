import pytest
from broadcaster import Broadcaster

def test_broadcaster_initialization():
    broadcaster = Broadcaster()
    assert broadcaster.sio.connected

def test_broadcaster_start_broadcast(mocker):
    broadcaster = Broadcaster()
    mocker.patch('cv2.VideoCapture')
    mocker.patch('cv2.imshow')
    mocker.patch('cv2.waitKey', return_value=ord('q'))
    broadcaster.start_broadcast()
    assert True
