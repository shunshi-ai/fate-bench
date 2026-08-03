import re, html, json, os, subprocess, time, urllib.parse
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'
os.makedirs('pages', exist_ok=True)

urls=[u.strip() for u in open('all_urls.txt') if u.strip()]
hits=[u for u in urls if re.search(r'題目|答案|算命師|算命师|得獎', urllib.parse.unquote(u))
      and '/tag/' not in u]
print(f'待抓 {len(hits)}\n', flush=True)

out=[]
for n,u in enumerate(hits,1):
    fn='pages/%03d.html'%n
    if not os.path.exists(fn):
        r=subprocess.run(['curl','-sL','-A',UA,'--max-time','30',u],
                         capture_output=True,text=True,errors='replace')
        open(fn,'w',encoding='utf-8').write(r.stdout); time.sleep(0.5)
    s=open(fn,encoding='utf-8',errors='replace').read()
    i=s.find('entry-content')
    body=s[i:i+120000].split('entry-utility')[0] if i>0 else ''
    title=re.search(r'<title>(.*?)</title>',s,re.S)
    title=html.unescape(title.group(1)).split('|')[0].strip() if title else '?'
    imgs=[x for x in re.findall(r'<img[^>]+src="([^"]+)"',body)
          if not re.search(r'/fb\.jpg|logo|icon|avatar|banner',x,re.I)]
    t=html.unescape(re.sub(r'<[^>]+>','\n',body)); t=re.sub(r'\n\s*\n+','\n',t).strip()
    cjk=len(re.findall(r'[一-鿿]',t))
    # 是否含题干结构
    nq=len(re.findall(r'(?:^|\n)\s*(?:Q\s*)?\d+\s*[).、．]',t))
    nopt=len(re.findall(r'(?:^|\n)\s*[A-E]\s*[).、．]?\s*\S',t))
    has_ans = bool(re.search(r'答案|正确答案|正確答案',t))
    yr=re.search(r'(20\d\d)',title)
    out.append(dict(n=n,url=u,title=title,year=int(yr.group(1)) if yr else None,
                    cjk=cjk,imgs=len(imgs),img_urls=imgs[:20],nq=nq,nopt=nopt,has_ans=has_ans))
    print(f'{n:3d} {title[:44]:44s} 汉字{cjk:5d} 图{len(imgs):3d} 题干{nq:3d} 选项{nopt:3d} 答案{"✓" if has_ans else "·"}', flush=True)

json.dump(out, open('pages_index.json','w'), ensure_ascii=False, indent=1)
