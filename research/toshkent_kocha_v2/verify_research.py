"""Sitata, chastota va reply dalillari asl eksportga mosligini tekshirish."""
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
import analyze_export as a

P = Path(__file__).parent
def read(name):
    return json.loads((P / name).read_text())

for path in P.glob('*.json'):
    json.loads(path.read_text())
cards = read('SLANG_VA_YOZUV_KARTALARI.json')
seeds = read('OLDINGI_11_SOZ_TEKSHIRUVI.json')
pairs = read('HAQIQIY_SUHBAT_JUFTLARI.json')
patterns = read('YOZISHMA_USULLARI.json')
stats = read('KORPUS_STATISTIKASI.json')
summary = read('HISOBOT_STATISTIKASI.json')
refs = []
for c in cards:
    assert a.hit_stats(c['query_pattern']) == c['match_stats'], c['id']
    assert c['evidence'] and c['observed_in_uploaded_export']
    assert not c['exclusive_to_tashkent_verified']
    assert not c['current_2026_usage_verified']
    for e in c['evidence']:
        assert e['message_id'] in c['match_stats']['matching_message_ids'], c['id']
    refs.extend(c['evidence'])
for c in seeds:
    assert a.hit_stats(c['query_pattern']) == c['literal_or_related_match_stats']
    refs.extend(c['context_evidence'])
for c in pairs:
    assert a.BY_ID[c['reply']['message_id']]['reply_to_message_id'] == c['parent']['message_id']
    assert c['explicit_reply_link'] and not c['creative_reconstruction']
    refs.extend([c['parent'], c['reply']])
for c in patterns:
    refs.extend(c['evidence'])
for e in refs:
    assert e == a.evidence(e['message_id']), e['message_id']

with (P / 'LUGAT_JADVAL.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len(cards) == 101
assert len({c['id'] for c in cards}) == len(cards)
for row, card in zip(rows, cards):
    assert row['id'] == card['id'] and row['lemma'] == card['lemma']
    assert int(row['messages']) == card['match_stats']['matching_messages']
    assert int(row['authors']) == card['match_stats']['distinct_author_codes']
assert len(seeds) == 11 and len(pairs) == 18 and len(patterns) == 10
assert summary['selected_quote_refs'] == len(refs)
assert summary['selected_unique_message_ids'] == len({e['message_id'] for e in refs})
assert len(a.RAW['messages']) == stats['total_export_records'] == 21505
assert len(a.records) == stats['ordinary_message_records'] == 20849
assert len(a.NONEMPTY) == stats['nonempty_text_messages'] == 17575
assert len(a.ELIGIBLE) == stats['analysis_eligible_messages'] == 17450
assert dict(collections.Counter(x['date'][:4] for x in a.NONEMPTY)) == stats['nonempty_text_by_year']
assert len((P / 'XABARLAR_INDEKSI.jsonl').read_text().splitlines()) == len(a.records)

creative = read('KREATIV_NAMUNALAR.json')
assert len(creative) == 13
card_ids = {c['id'] for c in cards}
for c in creative:
    assert not c['authentic_chat_quote'] and not c['whole_sentence_observed_in_chat']
    assert set(c['component_evidence_card_ids']) <= card_ids
    assert not any(a.normalize(c['text']) == x['normalized'] for x in a.ELIGIBLE)

sources = read('MANBALAR.json')
assert hashlib.sha256(a.INPUT.read_bytes()).hexdigest() == stats['sha256'] == a.SOURCE_SHA
for s in sources['pdf_theoretical_and_grammar_sources']:
    assert hashlib.sha256(Path(s['pdf_path']).read_bytes()).hexdigest() == s['sha256']
for ref in sources['pdf_source_refs'].values():
    text = re.sub(r'\s+', ' ', Path(ref['source_text_path']).read_text())
    anchor = re.sub(r'\s+', ' ', ref['anchor'])
    assert anchor in text, ref['source_id']
assert sources['new_external_sources_read'] == 0
assert all(not x['content_read'] for x in sources['network_attempts'])
assert read('MUSTAQIL_IZLANISH_HOLATI.json')['new_external_content_read'] == 0

# Natija fayli o‘zini ham hisobotdan ochiladigan artefakt sifatida beradi.
result = {'status': 'passed', 'export_sha256': a.SOURCE_SHA,
    'all_export_records_parsed': len(a.RAW['messages']),
    'cards_count_and_regex_stats_verified': len(cards),
    'seed_queries_verified': len(seeds), 'explicit_reply_links_verified': len(pairs),
    'quote_refs_matched_to_original_export': len(refs),
    'unique_quote_messages_verified': len({e['message_id'] for e in refs}),
    'creative_examples_separate_from_quotes': len(creative),
    'csv_rows_verified': len(rows), 'previous_pdf_hashes_verified': 3,
    'previous_pdf_ocr_anchors_verified': len(sources['pdf_source_refs']),
    'new_independent_web_sources_read': 0,
    'not_verified': ['Barcha misollarning yagona semantik ma’nosi',
        'Toshkentga xoslik', '2026-yil dolzarbligi', 'Audio talaffuz',
        'Ijodiy namunalar tabiiyligi bo‘yicha mahalliy baho'],
    'source_instructions_executed': False}
a.save('TEKSHIRUV_NATIJASI.json', result)
links = re.findall(r'\]\(([^)]+)\)', (P / 'OQISH_XULOSALARI.md').read_text())
assert all((P / link).is_file() for link in links)
result['report_file_links_verified'] = len(links)
a.save('TEKSHIRUV_NATIJASI.json', result)
print(json.dumps(result, ensure_ascii=False, indent=2))
