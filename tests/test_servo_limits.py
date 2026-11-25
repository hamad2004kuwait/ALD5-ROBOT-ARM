from unittest.mock import Mock
import pytest
import AL5D_Key_Fetcher as arm

@pytest.mark.parametrize('value',[599,2601,None,True,1500.0,'1500'])
def test_invalid_position(value):
    robot=Mock()
    with pytest.raises(ValueError): arm.servo(robot,0,value)
    robot.write.assert_not_called()

@pytest.mark.parametrize('value',[600,601,1500,2599,2600])
def test_protocol_boundaries(value,monkeypatch):
    send=Mock(); monkeypatch.setattr(arm,'send',send)
    arm.servo(None,0,value)
    send.assert_called_once_with(None,f'#0P{value}T{arm.MOVE_TIME}\r')

@pytest.mark.parametrize('channel',[-1,6,True,1.5])
def test_invalid_channel(channel):
    with pytest.raises(ValueError): arm.servo(None,channel,1500)

@pytest.mark.parametrize('pose',[[1500]*4,[1500]*6,[1500]*4+[2700]])
def test_pose_atomic_validation(pose):
    robot=Mock()
    with pytest.raises(ValueError): arm.move(robot,pose)
    robot.write.assert_not_called()
