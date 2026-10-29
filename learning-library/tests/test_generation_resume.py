"""An interrupted paid submission must never buy another image automatically."""
import hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import generate_illustrations as gen

class GenerationResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.state=self.root/'private';self.state.mkdir()
        self.root_patch=patch.object(gen,'ROOT',self.root);self.root_patch.start();self.addCleanup(self.root_patch.stop)
        self.item=('T01:1',{'prompt':'A greeting.','asset':'assets/test.webp'})
    def test_unknown_submit_state_stops_without_post(self):
        (self.state/'T01-1.json').write_text(json.dumps({'fingerprint':'unknown','status':'submitting'}))
        with patch.object(gen,'api') as api:
            with self.assertRaisesRegex(RuntimeError,'manual review'):gen.generate(self.item,'fake-key',self.state)
            api.assert_not_called()
    def test_created_state_polled_then_resumed_without_second_post(self):
        responses=[{'id':'known-task'},{'status':'created'},{'status':'completed','outputs':['https://assets.example/image.png']}]
        data=io.BytesIO();Image.new('RGB',(768,512),'ivory').save(data,format='PNG');raw=data.getvalue()
        with patch.object(gen,'api',side_effect=responses) as api,patch.object(gen.time,'sleep'),patch.object(gen,'urlopen',return_value=io.BytesIO(raw)):
            sid,metadata=gen.generate(self.item,'fake-key',self.state)
            self.assertEqual(sid,'T01:1');self.assertTrue(metadata['sha256'])
            self.assertEqual(sum(call.args[0]==gen.MODEL for call in api.call_args_list),1)
        self.item[1].update(metadata)
        # A downloaded asset is reused without any provider call.
        with patch.object(gen,'api') as api:
            gen.generate(self.item,'fake-key',self.state);api.assert_not_called()
    def test_rejected_request_keeps_submission_record(self):
        with patch.object(gen,'api',side_effect=RuntimeError('Provider HTTP 403')):
            with self.assertRaises(RuntimeError):gen.generate(self.item,'fake-key',self.state)
        self.assertEqual(json.loads((self.state/'T01-1.json').read_text())['status'],'submitting')
        with patch.object(gen,'api') as api:
            with self.assertRaisesRegex(RuntimeError,'manual review'):gen.generate(self.item,'fake-key',self.state)
            api.assert_not_called()
    def existing_asset(self):
        asset=self.root/self.item[1]['asset'];asset.parent.mkdir(parents=True)
        Image.new('RGB',(768,512),'ivory').save(asset)
        self.item[1]['sha256']=hashlib.sha256(asset.read_bytes()).hexdigest()
        return asset
    def test_swapped_valid_image_is_not_silently_adopted(self):
        asset=self.existing_asset();Image.new('RGB',(768,512),'orange').save(asset)
        with patch.object(gen,'api') as api:
            with self.assertRaisesRegex(RuntimeError,'checksum'):gen.generate(self.item,'fake-key',self.state)
            api.assert_not_called()
    def test_changed_prompt_cannot_reuse_existing_artwork(self):
        self.existing_asset();self.item[1]['generation_fingerprint']='previous-prompt'
        with patch.object(gen,'api') as api:
            with self.assertRaisesRegex(RuntimeError,'fingerprint'):gen.generate(self.item,'fake-key',self.state)
            api.assert_not_called()

if __name__=='__main__':unittest.main()
