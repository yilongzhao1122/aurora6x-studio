"""Read-only release audit; run: python audit_release.py PROJECT."""
from pathlib import Path
import sys,re
root=Path(sys.argv[1]).resolve();errors=[];count=0
for p in root.rglob('*'):
 if not p.is_file() or '.git' in p.relative_to(root).parts:continue
 count+=1
 if p.suffix.lower() in {'.der','.pem','.p12','.pfx'} or p.name=='developer_key':errors.append(str(p.relative_to(root))+': credential filename')
 if p.suffix.lower() in {'.md','.ps1','.cmd','.json','.yml','.yaml','.html'}:
  try:s=p.read_text(encoding='utf-8-sig')
  except (UnicodeError,OSError):continue
  if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',s):errors.append(str(p.relative_to(root))+': private key')
  if re.search(r'[A-Z]:\\(?:Users|ChromeDownload)\\',s):errors.append(str(p.relative_to(root))+': private workstation path')
for e in errors:print('FAIL',e)
print(f'{"FAIL" if errors else "PASS"}: {count} files scanned (filename/text audit, not exhaustive secret detection).')
sys.exit(bool(errors))
