from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import GDIP_CODE as arm

@pytest.mark.parametrize('text,result', [('Pick up Key A','A'),('Bring me Key B','B'),('I need the third key','C'),('How do you work?','CHAT'),('Get me Key A',' B '),('Pick up a key','A'),('What happens if you pick up Key B?','B'),('Do not pick up Key A','A'),('Get Key A and Key C','A'),('Get Key A and B','A'),('Get all three keys','A'),('Get Key D','A'),('','A'),('Noise','MOVE'),('Never pick up Key C','C')])
def test_classifier(text,result):
    client=Mock()
    client.responses.create.return_value=SimpleNamespace(output_text=result)
    expected={'Pick up Key A':'A','Bring me Key B':'B','I need the third key':'C','How do you work?':'CHAT'}.get(text,'INVALID')
    assert arm.ask_ai(client,text)==expected

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

def test_unknown_key():
    robot=Mock()
    with pytest.raises(ValueError): arm.pickup(robot,'D')
    robot.write.assert_not_called()

def test_missing_connection(monkeypatch):
    monkeypatch.setattr(arm,'DRY_RUN',False)
    with pytest.raises(RuntimeError): arm.send(None,'#0P1500T1000\r')

def test_invalid_gripper(monkeypatch):
    monkeypatch.setattr(arm,'GRIP_CLOSED',2700)
    robot=Mock()
    with pytest.raises(ValueError): arm.pickup(robot,'A')
    robot.write.assert_not_called()

def test_partial_serial_write():
    robot=Mock(); robot.write.return_value=1
    with pytest.raises(OSError): arm.send(robot,'#0P1500T1000\r')
    robot.flush.assert_not_called()

def test_serial_disconnect_aborts(monkeypatch):
    robot=Mock(); robot.write.side_effect=OSError('disconnected')
    with pytest.raises(OSError): arm.pickup(robot,'A')
    assert robot.write.call_count==1

def test_interrupt_aborts():
    robot=Mock(); robot.write.side_effect=KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt): arm.pickup(robot,'A')
    assert robot.write.call_count==1
