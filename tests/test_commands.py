from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import AL5D_Key_Fetcher as arm

@pytest.mark.parametrize('text,result', [('Pick up Key A','A'),('Bring me Key B','B'),('I need the third key','C'),('How do you work?','CHAT'),('Get me Key A',' B '),('Pick up a key','A'),('What happens if you pick up Key B?','B'),('Do not pick up Key A','A'),('Get Key A and Key C','A'),('Get Key A and B','A'),('Get all three keys','A'),('Get Key D','A'),('','A'),('Noise','MOVE'),('Never pick up Key C','C')])
def test_classifier(text,result):
    client=Mock()
    client.responses.create.return_value=SimpleNamespace(output_text=result)
    expected={'Pick up Key A':'A','Bring me Key B':'B','I need the third key':'C','How do you work?':'CHAT'}.get(text,'INVALID')
    assert arm.ask_ai(client,text)==expected
