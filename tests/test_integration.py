from unittest.mock import Mock
import pytest
import AL5D_Key_Fetcher as arm

@pytest.mark.parametrize('key',['A','B','C'])
def test_complete_sequence(key,monkeypatch):
    # Synthetic poses for B/C only; not physical calibration.
    poses=([1500]*5,[1600,1550,1450,1500,1500],[1500]*5)
    monkeypatch.setitem(arm.KEYS,key,poses)
    robot=Mock(); robot.write.side_effect=lambda data:len(data)
    monkeypatch.setattr(arm.time,'sleep',lambda _:None)
    arm.pickup(robot,key)
    commands=[c.args[0].decode() for c in robot.write.call_args_list]
    servo=[c for c in commands if 'P' in c]
    expected=[f'#{i}P{v}T1000\r' for i,v in enumerate(poses[0])]+['#5P1500T1000\r']+[f'#{i}P{v}T1000\r' for i,v in enumerate(poses[1])]+['#5P2500T1000\r']+[f'#{i}P{poses[2][i]}T1000\r' for i in range(4,-1,-1)]
    assert servo==expected
    assert commands.index('#29H\r')<commands.index('#28H\r')<commands.index('#31H\r')

@pytest.mark.parametrize('messages,count',[(['1','A','A','Q'],1),(['1','A','R','REMOVED','A','Q'],2),(['1','B','Q'],0),(['1','','Q'],0)])
def test_keyboard_session(messages,count,monkeypatch):
    monkeypatch.setattr('builtins.input',lambda _:next(iterator))
    iterator=iter(messages)
    pickup=Mock(); monkeypatch.setattr(arm,'pickup',pickup)
    monkeypatch.setattr(arm,'speak',Mock())
    arm.main()
    assert pickup.call_count==count

def test_voice_session(monkeypatch):
    monkeypatch.setattr('builtins.input',lambda _:'2')
    monkeypatch.setattr(arm,'connect_ai',Mock())
    monkeypatch.setattr(arm,'listen',Mock(side_effect=['Pick up Key A','quit']))
    monkeypatch.setattr(arm,'ask_ai',Mock(return_value='A'))
    monkeypatch.setattr(arm,'speak',Mock())
    pickup=Mock(); monkeypatch.setattr(arm,'pickup',pickup)
    arm.main()
    pickup.assert_called_once_with(None,'A')

def test_ai_failure_no_motion(monkeypatch):
    iterator=iter(['1','Pick up Key A','Q'])
    monkeypatch.setattr('builtins.input',lambda _:next(iterator))
    monkeypatch.setattr(arm,'connect_ai',Mock())
    monkeypatch.setattr(arm,'ask_ai',Mock(side_effect=TimeoutError))
    pickup=Mock(); monkeypatch.setattr(arm,'pickup',pickup)
    arm.main(); pickup.assert_not_called()

def test_microphone_failure_no_motion(monkeypatch):
    monkeypatch.setattr('builtins.input',lambda _:'2')
    monkeypatch.setattr(arm,'connect_ai',Mock())
    monkeypatch.setattr(arm,'listen',Mock(side_effect=[OSError('missing microphone'),'quit']))
    pickup=Mock(); monkeypatch.setattr(arm,'pickup',pickup)
    arm.main(); pickup.assert_not_called()
