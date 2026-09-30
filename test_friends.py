"""Test persistence and connection behaviour without a desktop display."""
import tempfile
import unittest
from pathlib import Path
from myAppStarter import FriendStore

class FriendTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=FriendStore(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_exactly_five_initial_profiles(self):
        self.assertEqual([p['name'] for p in self.store.people],['Alex','Ali','Raj','Adam','Rima'])
        self.store.validate()
    def test_persistence(self):
        self.store.get('alex')['bio']='My updated note'
        self.store.save()
        self.assertEqual(FriendStore(self.temp.name).get('alex')['bio'],'My updated note')
    def test_mutual_connections(self):
        self.store.connect('alex','raj',True)
        self.assertIn('raj',self.store.get('alex')['friends'])
        self.assertIn('alex',self.store.get('raj')['friends'])
        self.store.connect('alex','raj',False)
        self.assertNotIn('raj',self.store.get('alex')['friends'])
        self.store.validate()
    def test_delete_removes_links(self):
        self.store.remove('ali')
        self.assertEqual(len(self.store.people),4)
        self.assertTrue(all('ali' not in p['friends'] for p in self.store.people))
        self.store.save()
    def test_friends_of_friends(self):
        self.assertEqual(self.store.suggestions('alex'),['adam','raj'])
    def test_sixth_profile_rejected(self):
        self.store.people.append({'id':'six','name':'Six','bio':'','photo':'','friends':[]})
        with self.assertRaises(ValueError):self.store.save()
    def test_invalid_file_kept(self):
        p=Path(self.temp.name)/'friends.json';p.write_text('broken json')
        loaded=FriendStore(self.temp.name)
        self.assertIsNotNone(loaded.warning)
        self.assertEqual(len(loaded.people),5)
        self.assertEqual(p.read_text(),'broken json')

if __name__=='__main__':unittest.main()
