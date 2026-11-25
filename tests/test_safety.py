from unittest.mock import Mock
import pytest
import AL5D_Key_Fetcher as arm

@pytest.mark.parametrize('key',['B','C','D'])
def test_uncalibrated_or_unknown(key):
    robot=Mock()
    with pytest.raises(ValueError): arm.pickup(robot,key)
    robot.write.assert_not_called()

def test_unverified_hardware(monkeypatch):
    monkeypatch.setattr(arm,'DRY_RUN',False)
    robot=Mock()
    with pytest.raises(RuntimeError): arm.pickup(robot,'A')
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
