import unittest
from virtualhome_corpus.diversity_windows import select_window

class FixedWindowTests(unittest.TestCase):
    def test_exact_source_length_and_no_padding(self):
        m={'frame_count':20,'condition':'approach_only'}
        self.assertEqual(select_window(m,{}),(0,'target_interaction_absent'))
        m['frame_count']=19
        with self.assertRaises(ValueError):select_window(m,{})

    def test_event_crop_clamped_without_changing_length(self):
        m={'frame_count':30,'condition':'interaction','scenario':{'family':'door'}}
        a={'actions':[{'action':'OPEN','raw_start':0,'raw_end':4}]}
        self.assertEqual(select_window(m,a),(0,'OPEN'))
        a['actions'][0].update(raw_start=27,raw_end=30)
        self.assertEqual(select_window(m,a),(10,'OPEN'))

    def test_sitting_uses_terminal_animation_not_long_preparation(self):
        m={'frame_count':90,'condition':'interaction','scenario':{'family':'posture'}}
        a={'actions':[{'action':'SIT','raw_start':30,'raw_end':90}]}
        self.assertEqual(select_window(m,a),(70,'SIT'))

if __name__=='__main__':unittest.main()
