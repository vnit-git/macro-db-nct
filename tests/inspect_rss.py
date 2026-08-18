import feedparser
from bs4 import BeautifulSoup
import re

f = feedparser.parse('http://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss')
for i, e in enumerate(f.entries[:5]):
    summary_raw = e.get('summary', '')
    soup = BeautifulSoup(summary_raw, 'html.parser')
    text = soup.get_text().strip()
    print(f"ITEM {i}: title_len={len(e.get('title', ''))}, summary_len={len(summary_raw)}")
    print(f"TEXT {i}: {text[:150].encode('ascii', 'ignore').decode('ascii')}")
    print("-" * 40)
