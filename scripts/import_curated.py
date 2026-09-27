"""Import the curated Markdown export, preserving source files and local attachments."""
from pathlib import Path
import re,json,hashlib,shutil,unicodedata
from datetime import datetime
from urllib.parse import quote,unquote,urlsplit
import yaml
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(r'D:\技术文档')
DEST=ROOT/'content/posts'
MEDIA=ROOT/'static/journal-media'
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def norm(s):return re.sub(r'[^\w\u4e00-\u9fff]','',unicodedata.normalize('NFKC',s).lower()).replace('_','')
def read(p):return p.read_text(encoding='utf-8-sig')
def metadata(text):
 m=re.match(r'^---\s*\n(.*?)\n---\s*\n',text,re.S)
 return (yaml.safe_load(m[1]) or {},text[m.end():]) if m else ({},text)
def slug(s):return re.sub(r'[^\w\u4e00-\u9fff]+','-',s.lower()).strip('-')
def main():
 if not SOURCE.is_dir():raise SystemExit('Source not found')
 files=sorted(SOURCE.rglob('*.md'))
 if not files:raise SystemExit('No Markdown files; refusing empty replacement')
 backup=ROOT.parent/('journal-import-backup-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
 shutil.copytree(DEST,backup/'posts')
 shutil.copy2(ROOT/'data/journal_index.json',backup/'journal_index.json')
 old={}
 for p in DEST.rglob('*.md'):
  meta,_=metadata(read(p));old.setdefault(norm(p.stem),[]).append(meta)
 assets={};MEDIA.mkdir(parents=True,exist_ok=True)
 for p in SOURCE.rglob('*'):
  if p.is_file() and p.suffix.lower()!='.md':
   digest=hashlib.sha256(p.read_bytes()).hexdigest()[:20]
   name=digest+p.suffix.lower();shutil.copy2(p,MEDIA/name)
   assets[p.resolve()]='/journal-media/'+name
 documents={p.resolve():'/posts/'+slug(p.stem)+'/' for p in files}
 if len(set(documents.values()))!=len(files):raise SystemExit('Duplicate article slugs')
 missing=[];linked=set();outputs={};index={}
 oldindex=json.loads((ROOT/'data/journal_index.json').read_text(encoding='utf-8'))
 lookup={norm(k):v for k,v in oldindex.items()}
 for p in files:
  body=metadata(read(p))[1]
  body=re.sub(r'!\[[^\]]*\]\(https://internal-api-drive-stream\.feishu\.cn/[^\s)]+\)', '> 图片待补充（原图未包含在本次导出中）。', body)
  def replace(m):
   target=m[2].strip().strip('<>');parts=urlsplit(target)
   if parts.scheme or target.startswith(('#','/')):return m[0]
   local=(p.parent/unquote(parts.path)).resolve()
   # Exported Markdown sometimes backslash-escapes filenames.
   if not local.exists():local=(p.parent/unquote(parts.path).replace('\\','')).resolve()
   if local in assets:
    linked.add(local);url=assets[local]
   elif local in documents:url=documents[local]
   else:
    missing.append({'article':str(p.relative_to(SOURCE)),'target':target});return m[0]
   if parts.fragment:url+='#'+parts.fragment
   return m[1]+url+m[3]
  # Do not rewrite examples within fenced code blocks.
  segments=re.split(r'(^```[^\n]*\n.*?^```[^\n]*(?:\n|$)|^~~~[^\n]*\n.*?^~~~[^\n]*(?:\n|$))',body,flags=re.M|re.S)
  for i in range(0,len(segments),2):segments[i]=re.sub(r'(!?\[[^\]\n]*\]\()((?:[^()\n]|\([^()\n]*\))*)(\))',replace,segments[i])
  body=''.join(segments)
  # The page header already renders this title; preserve every lower heading.
  body=re.sub(r'\A\s*#\s+[^\n]+\n','',body,count=1)
  candidates=old.get(norm(p.stem),[])
  aliases=[];date=None
  for meta in candidates:
   aliases.extend(meta.get('aliases',[]))
   d=meta.get('date');ds=str(d)
   if d and len(ds)>=7:
    aliases.append('/posts/'+ds[:4]+'/'+ds[5:7]+'/'+str(meta.get('slug',slug(p.stem)))+'/')
    if ds[:4].isdigit() and int(ds[:4])>=2000:date=ds
  meta={'title':p.stem,'url':documents[p.resolve()],'draft':False,'source_group':p.relative_to(SOURCE).parts[0],'source_file':p.relative_to(SOURCE).as_posix(),'showtoc':True}
  if date:meta['date']=date
  if aliases:meta['aliases']=sorted(set(a for a in aliases if a!=meta['url']))
  topic=lookup.get(norm(p.stem),'technology')
  if p.relative_to(SOURCE).parts[0]=='机械臂':topic='projects'
  if p.stem=='互联网':topic='technology'
  index[slug(p.stem)]=topic
  outputs[slug(p.stem)+'.md']='---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n'+body.strip()+'\n'
 for p,url in assets.items():
  if p.suffix.lower() in {'.pdf','.docx'} and p not in linked:
   name='arm-user-manual' if 'FRUIT_PICKING' in p.name else slug(p.stem)+'-attachment'
   meta={'title':'机械臂使用手册' if 'FRUIT_PICKING' in p.name else p.stem,'url':'/posts/'+name+'/','draft':False,'showtoc':False,'source_group':p.relative_to(SOURCE).parts[0]}
   outputs[name+'.md']='---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n[打开或下载原始文档]('+url+')\n'
   index[name]='projects';linked.add(p)
 if missing:
  write(ROOT/'import-report.json',json.dumps({'missing':missing},ensure_ascii=False,indent=2))
  raise SystemExit('Unresolved local links; see import-report.json. Articles not replaced.')
 # Exact directory guard before replacing the generated Markdown collection.
 if DEST.resolve()!=ROOT.resolve()/'content'/'posts':raise SystemExit('Unexpected destination')
 for p in DEST.rglob('*.md'):p.unlink()
 for name,body in outputs.items():write(DEST/name,body)
 write(ROOT/'data/journal_index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')
 write(ROOT/'import-report.json',json.dumps({'markdown':len(files),'published_articles':len(outputs),'media':len(assets),'local_links_missing':missing,'source':str(SOURCE)},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'markdown':len(files),'published_articles':len(outputs),'media':len(assets),'missing':len(missing)}))
if __name__=='__main__':main()
