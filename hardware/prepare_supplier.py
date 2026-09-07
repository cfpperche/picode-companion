"""Fetch and verify the exact supplier CAD, then prepare the model intermediate."""
from pathlib import Path
import urllib.request,hashlib,json,gzip,base64,tempfile
from import_step import read
root=Path(__file__).resolve().parent
spec=json.loads((root/'components.json').read_text())['components'][0]
with urllib.request.urlopen(spec['source'],timeout=120) as response:data=response.read()
actual=hashlib.sha256(data).hexdigest()
if actual!=spec['source_sha256']:
 raise RuntimeError('Supplier file changed; review new CAD before accepting it: '+actual)
with tempfile.TemporaryDirectory() as work:
 path=Path(work)/'supplier.stp';path.write_bytes(data);solids=read(path)
encoded=json.dumps(solids,separators=(',',':')).encode()
(root/'respeaker-native.json.gz.b64').write_text(base64.b64encode(gzip.compress(encoded,9,mtime=0)).decode())
print('Prepared',len(solids),'supplier solids without scaling')
