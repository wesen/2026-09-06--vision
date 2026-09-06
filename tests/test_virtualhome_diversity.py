import copy
import json
from pathlib import Path
import unittest
from virtualhome_corpus.diversity import plan,bind,camera_for,program_for


class DiversityContracts(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads(Path('configs/virtualhome-diversity-v2.json').read_text())

    def test_matched_lineages_and_unseen_apartment_split(self):
        rows=plan(self.cfg)
        self.assertEqual(len(rows),48)
        self.assertEqual(len({r['episode_id'] for r in rows}),48)
        for lineage in {r['lineage_id'] for r in rows}:
            group=[r for r in rows if r['lineage_id']==lineage]
            self.assertEqual(len(group),4)
            self.assertEqual(len({r['split'] for r in group}),1)
            self.assertEqual({(r['condition'],r['view']) for r in group},{('interaction','left'),('interaction','right'),('approach_only','left'),('approach_only','right')})
        for scene in range(3):
            self.assertEqual({r['scenario']['family'] for r in rows if r['scene_index']==scene},{'door','pickup','posture','switch'})
        self.assertEqual(rows,plan(self.cfg))

    def test_conflicting_scene_ownership_rejected(self):
        self.cfg['scenes'][1]['scene_index']=0
        with self.assertRaises(ValueError):plan(self.cfg)

    def test_binding_and_camera_contract(self):
        target={'id':2,'class_name':'fridge','properties':['CAN_OPEN'],'states':['CLOSED'],'bounding_box':{'center':[1,1,1],'size':[1,2,1]}}
        room={'id':1,'class_name':'kitchen','category':'Rooms','bounding_box':{'center':[0,1,0],'size':[6,3,6]}}
        g={'nodes':[target,room],'edges':[{'from_id':2,'to_id':1,'relation_type':'INSIDE'}]}
        scenario={'family':'door','target_id':2,'target_class':'fridge'}
        self.assertEqual(bind(g,scenario)[0],target)
        left=camera_for(target,room,'left');right=camera_for(target,room,'right')
        self.assertNotEqual(left['position'],right['position'])
        self.assertEqual(left['look_at'],right['look_at'])
        scenario['target_class']='microwave'
        with self.assertRaises(ValueError):bind(g,scenario)

    def test_control_has_no_target_manipulation(self):
        target={'id':2,'class_name':'fridge','states':['CLOSED']}
        control=program_for('door',target,None,'approach_only')
        self.assertTrue(all('[Walk]' in line or '[LookAt]' in line for line in control))
        positive=program_for('door',target,None,'interaction')
        self.assertEqual(sum('[Open]' in s for s in positive),1)
        self.assertEqual(sum('[Close]' in s for s in positive),1)
        self.assertEqual(program_for('posture',target,None,'interaction')[-2],'<char0> [StandUp]')

if __name__=='__main__':unittest.main()
