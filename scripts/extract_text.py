"""重抽正文：块级标签→换行，行内标签→删除（不打碎行）。"""
import re, html, json, os

BLOCK = r'(?:p|div|br|tr|li|h[1-6]|table|ul|ol|blockquote|hr|section|article)'

def clean(htm: str) -> str:
    i = htm.find('entry-content')
    b = htm[i:i+200000].split('entry-utility')[0] if i > 0 else ''
    b = re.sub(r'<(script|style)\b.*?</\1>', '', b, flags=re.S|re.I)
    # 标红 → «»（2010 那页明说红色是答案）
    b = re.sub(r'<(span|font)[^>]*(?:color\s*[:=]\s*"?#?(?:ff0000|f00|red))[^>]*>(.*?)</\1>',
               r'«\2»', b, flags=re.S|re.I)
    b = re.sub(rf'</?{BLOCK}\b[^>]*>', '\n', b, flags=re.I)   # 块级 → 换行
    b = re.sub(r'<[^>]+>', '', b)                              # 行内 → 删除
    t = html.unescape(b)
    t = t.replace(' ', ' ').replace('　', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = '\n'.join(l.strip() for l in t.split('\n'))
    t = re.sub(r'\n{2,}', '\n', t).strip()
    for cut in ('搜尋關鍵字', '近期文章', 'Post Views'):
        j = t.find(cut)
        if j > 300: t = t[:j]
    return t.strip()

if __name__ == '__main__':
    idx = json.load(open('pages_index.json'))
    KEEP = re.compile(r'題目|答案'); SKIP = re.compile(r'圖片|相片|視頻|頒獎禮|場刊|刊物|通知')
    os.makedirs('raw2', exist_ok=True)
    for p in idx:
        if not KEEP.search(p['title']) or SKIP.search(p['title']): continue
        if not p['year']: continue
        t = clean(open('pages/%03d.html' % p['n'], encoding='utf-8', errors='replace').read())
        kind = 'answers' if ('答案' in p['title'] and '題目' not in p['title']) else 'questions'
        fn = f"raw2/{p['year']}_{kind}_{p['n']:03d}.txt"
        open(fn, 'w', encoding='utf-8').write(f"# {p['title']}\n# {p['url']}\n\n{t}")
        print(f"{p['year']} {kind:9s} {len(t):6d}字  {fn}")
