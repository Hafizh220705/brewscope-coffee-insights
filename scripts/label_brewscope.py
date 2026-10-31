#!/usr/bin/env python3
"""Offline, conservative lexical pre-annotation for BrewScope.
NOT an LLM or human annotator, not a gold-standard generator.
No network, rating, place name, or URL is used to infer labels.
"""
import re, json, csv, hashlib, collections, pathlib, unicodedata
from urllib.parse import urlparse,parse_qs
import pandas as pd
import jsonschema

ROOT=pathlib.Path('/mnt/data')
SOURCE=ROOT/'reviews_for_annotation.csv'
SCHEMA=json.loads((ROOT/'annotation_schema(1).json').read_text())
ASPECTS=['product_quality','service','price_value','ambience','facilities','cleanliness']
ANNOTATOR='auto:lexical_preannotation_v1'
VERSION='0.1.0-draft'

def rx(s): return re.compile(s, re.I|re.UNICODE)
# Patterns describe mention TARGETS, not a preordained sentiment.
TARGETS={
'product_quality': rx(r'\b(?:makan\w*|minum\w*|kopi\w*|coffee|coffe|kopsu|latte|matcha|cappuc?cino|americano|espresso|mocha|moka|mojito|cold brew|v60|v-60|manual brew|beans|biji kopi|teh|tea|cokl(?:at|et)|chocolate|jus|juice|smoothie|susu|roti\w*|rot[iy]|ropang|bakery|cake|dessert|snack|camilan|cemilan|nasi\w*|nasgor|mie|mi\b|ayam|sate|burger|pizza|spaghetti|pasta|ramen|tahu|cireng|pisang|kue|croissant|sourdough|porsi\w*|plating\w*|rasa\w*|menu(?:nya|\b)|hidangan|masakan|kuliner|food|taste|drink|beverage|sarapan|lunch|dinner|sambal|sauce|saus|kuah|cemilan|aroma kopi|kopken|kopinya|es krim|ice cream|milkshake|yummy|delicious|tasty|fresh food|jajanan|gorengan|strawberry|pastry|flavour|flavor)\b'),
'service':rx(r'\b(?:pelayan\w*|pelayanannya|pelayananya|staff|staf\w*|barista\w*|kasir\w*|waiter\w*|waitress|server|pramusaji|pegawai\w*|karyawan\w*|kariawan\w*|crew\w*|customer service|services?|servis|hospitality|pesan\w*|pesenan|pesanan|order\w*|antri\w*|antre\w*|queue|waiting|nunggu\w*|menunggu|tunggu\w*|diusir|di\s*usir|dipaksa\s+beli|dilayani|melayani|penyajian|diantar|diantarkan|disajikan|datang\s+telat|dateng\s+lama|keluar\s+lama|terlambat|respons\w*|respon\w*|komplain|complain\w*|booking|reservasi|self.service|free refill)\b'),
'price_value':rx(r'\b(?:harga\w*|pricing|price|murah\w*|muraah\w*|mahal\w*|kemahalan|terjangkau|afford\w*|worth\w*|budget|value|promo\w*|promosi|diskon\w*|discount\w*|voucher\w*|coupon\w*|kupon\w*|cashback|low.budget|kantong|dompet|mahasiswa.friendly|ramah\s+(?:di\s+)?kantong|beli.*(?:ribu|rp\s?\d)|biaya|bayar|pajak|tax|overprice\w*|pricy|pricey|ekonomis|price.range|reasonable.price|cost)\b'),
'ambience':rx(r'\b(?:tempat\w*|tmpt\w*|suasana\w*|atmosf\w*|ambien\w*|vibes?\b|vibe\w*|cozy\w*|chozy\w*|nyaman\w*|nyamaa\w*|nyamann\w*|comf\w*|comfort\w*|nongkrong|nongki\w*|hangout|wfc|wfh|nugas|skripsi|belajar|kerja\s+tugas|meet\s*up|rapat|ngobrol|interior\w*|dekor\w*|aesthe\w*|estetik\w*|esthetic\w*|aesthetic\w*|musik\w*|music|live.music|berisik|bising|kebisingan|tenang|adem\w*|sejuk|syahdu|sunyi|rame\w*|ramai|crowded|sempit|luas|lapang|ruang\w*|indoor|outdoor|view\w*|pemandangan|spot\s*foto|foto.foto|photogenic|kalcer|work(?:ing)?\s*space|homy|homey|rumahan|betah|asyik|asik|seru|homi|hidden.gem|instagrammable|enak\s+buat\s+(?:nongkrong|wfc|nugas|belajar)|nice\s+place|good\s+place|panas|gerah|sepi|bising)\b'),
'facilities':rx(r'\b(?:wi.?fi\w*|wifi\w*|internet|hotspot|parkir\w*|parking|colokan\w*|stop\s*kontak|soket|socket|charger|charging|listrik|toilet\w*|wc\b|kamar\s*mandi|mushol\w*|mushal\w*|musol\w*|musala\w*|sholat|ibadah|photobooth\w*|photo\s*booth|kursi\w*|chair\w*|seat\w*|meja\w*|table\w*|ac\b|air\s*condition\w*|kipas\w*|fasilitas\w*|amenit\w*|tempat\s+duduk|colok\w*|printer\w*|ngeprint|print\w*|ruang\s*meeting|ruang\s*rapat|stok\s+colokan|area\s+parkir|garasi|lift|stairs|disabilitas|akses\s*kursi\s*roda)\b'),
'cleanliness':rx(r'\b(?:bersih\w*|kebersihan|clean\w*|kotor\w*|jorok|higien\w*|hygien\w*|sanitasi|sampah\w*|bau\s*(?:pesing|sampah|tak\s*sedap|busuk)|berbau|pesing|debu\w*|berdebu|lengket|lalat|kecoa|tikus|semut|berantakan|bekas\s*(?:makanan|minuman)|toilet\s*jorok|bau\s*toilet|lantai\s*licin|licin\s*karena\s*kotor|hand\s*saniti[sz]er|cuci\s*tangan|jaga\s*kebersihan|higiene)\b')
}
LOCATION=rx(r'\b(?:lokasi\w*|strategis|strategies|akses\s*jalan|jalan\s*menuju|sulit\s*ditemukan|mudah\s*ditemukan|letak\w*|dekat\s+kampus|pinggir\s*jalan|masuk\s*gang|jarak\s+dari|jalan\s*masuk|gampang\s*dicari)\b')
GENERAL=rx(r'\b(?:mantap\w*|bagus\w*|good|nice|best\w*|oke\w*|ok\b|keren\w*|top\b|rekomend\w*|recommend\w*|rekomen\w*|awesome|amazing|luar\s*biasa|sempurna|recommended|love\w*|suka\w*|favorit\w*|favorite|enak\w*|terbaik\w*|sip\w*|makasih|terima\s*kasih|thanks|thank you|mantull?\w*|enjoy\w*|asik|seru|ngangenin|gg\b|puas\w*|buruk|jelek|bad|kecewa|kapok|parah|mengesankan|satisf\w*|fine|okey)\b')
POS=rx(r'\b(?:enak\w*|enaak\w*|nikmat\w*|lezat|mantap\w*|mantep\w*|top\b|bagus\w*|baguss\w*|baik\w*|good|great|nice|best\w*|keren\w*|oke\w*|ok\b|suka\w*|favorit\w*|favorite|juara|ramah\w*|rmah\w*|helpful|friendly|cepat\w*|sigap|gercep\w*|worth\w*|afford\w*|murah\w*|muraah\w*|terjangkau|bersahabat|cozy\w*|chozy\w*|nyaman\w*|nyamann\w*|comf\w*|comfort\w*|adem\w*|sejuk|syahdu|tenang|asik|asyik|seru|love\w*|fresh|segar\w*|lezat|delicious|yummy|tasty|puas\w*|clean\w*|bersih\w*|lengkap\w*|melimpah|luas|banyak\s+pilihan|beragam|aesthe\w*|estetik\w*|aesthetic\w*|homey|homy|betah|rekomend\w*|recommend\w*|rekomen\w*|terbaik\w*|memuaskan|mengenyangkan|perfect|sopan|fast|quick|super|pas\b|lancar|sukses|premium|cantik|cakep|menarik|strategis|hemat|ramai\s*sekali)\b')
NEG=rx(r'\b(?:buruk|jelek\w*|bad|poor|worse|worst|kecewa\w*|kapok|kurang|tidak\s+ada|ngg?ak\s+ada|gak\s+ada|ga\s+ada|habis|kosong|hambar|basi|gosong|terbakar|pahit|asin\w*|keasinan|kemanisan|terlalu\s+manis|terlalu\s+asin|keras|mentah|mahal\w*|overprice\w*|overpriced|pricey|pricy|lama|lambat|telat|terlambat|nunggu|menunggu|waited|slow|slowly|crowded|berisik|bising|sempit|panas|gerah|kotor\w*|jorok|pesing|berbau|bau\s*(?:sampah|busuk|pesing)|rusak|error|eror|lemot|mati\s+total|gak\s+bisa|ngga\s+bisa|tidak\s+bisa|susah|sulit|ribet|antre\w*|antri\w*|terlalu\s+(?:sempit|ramai|berisik)|uncomfortable|unfriendly|mahal|ngetawain|diusir|di\s*usir|lupa|diabaikan|tidak\s+sesuai|nggak\s+sesuai|tidak\s+nyaman|ga\s+ramah|bukan\s+yang|parah)\b')
NEGATION=rx(r'\b(?:tidak|nggak|ngga|gak|ga|gk|tak|bukan|belum|kurang|no|not|never|kagak|ndak)\b')
NEG_NEG=rx(r'\b(?:tidak|ngga|nggak|gak|ga|gk|tak)\s+(?:pernah\s+)?(?:mengecewakan|buruk|jelek|parah|mahal|buruk|kurang\s+enak|salah)\b')
NEG_POS=rx(r'\b(?:tidak|ngga|nggak|gak|ga|gk|tak|kurang|not|no)\s+(?:terlalu\s+)?(?:enak\w*|bagus\w*|nyaman\w*|ramah\w*|baik\w*|cepat|bersih\w*|worth\w*|menarik|segar|oke|mantap\w*|murah|puas|nyambung|lancar|friendly|clean)\b')
PRAISE_ONLY=rx(r'^(?:\W|\s)*(?:(?:bagus|baguss+|mantap\w*|mantul\w*|top|oke\w*|ok|best\w*|good|nice|amazing|recommended|rekomendasi|rekomend\w*|rekomen\w*|makasih|terimakasih|terima\s+kasih|thanks|sip|keren\w*|asik|asyik|enak\w*|puas|recommended|excellent|juara|sangat|banget|bgt|pokoknya|everything|semuanya|ini|sih|lah|brow\w*|the|gaes|guys|definitely|love|it|sekali|bangett|bangeet|sm|bnget|bngt|parah|perfect|terbaik\w*|memuaskan|selalu|favorite|fav|all|overall|wow)\b[\s.,!+\-]*|[^\w\s])+$')
SPECIAL_UNCERTAIN=rx(r'\b(?:bukan\s+berarti\s+tidak|entahlah|mungkin\s+enak|agak\s+aneh|lambat\s+sekali|ga\s+tau|gak\s+tau)\b')
# Explicit malformed instruction in text remains data; no tool execution.

# Return spans covering clauses without altering characters. The corpus has many typos and code-switching.
SPLITTER=rx(r'[,;\n]+|(?<=[.!?])\s+(?=[\w(])|\s+\b(?:tapi|tetapi|namun|cuman|cuma|cuman|sayangnya|sedangkan|meskipun|walaupun|kecuali|padahal)\b\s+|(?<=\s)\+\s+(?=\w)')

def segments(text):
    chunks=[]; last=0
    for m in SPLITTER.finditer(text):
        frag=text[last:m.start()]
        a=last+len(frag)-len(frag.lstrip()); b=m.start()-len(frag)+len(frag.rstrip())
        if b>a: chunks.append((a,b,text[a:b]))
        last=m.end()
    frag=text[last:]
    a=last+len(frag)-len(frag.lstrip()); b=len(text)-len(frag)+len(frag.rstrip())
    if b>a: chunks.append((a,b,text[a:b]))
    return chunks or ([(0,len(text),text)] if text else [])

def get_shop_id(url):
    q=parse_qs(urlparse(url).query)
    pid=q.get('query_place_id',[''])[0]
    key=pid if pid else url
    return 'SHOP_'+hashlib.sha256(key.encode()).hexdigest()[:14].upper()

def soften_repeated(s):
    """Reading normalization only; evidence retains exact original."""
    return re.sub(r'(\w)\1{2,}',r'\1\1',s.lower())

def detect_flags(text):
    flags=[]
    if LOCATION.search(text):flags.append('out_of_taxonomy')
    if re.search(r'\b(?:the|very|nice|great|best|comfort|good|place|food|service|affordable|love|but|with|and|is|for|worth|coffee)\b',text,re.I):flags.append('code_switching')
    if re.search(r'\b(?:bgt|bangett|bangettt|gk|ga|gak|ngga|yg|klo|bnget|bgtt|tmpt|rmah|rasa\s*nya)\b',text,re.I):flags.append('misspelling')
    if re.search(r'\b(?:sarkas|cepat\s+banget.{0,35}(?:jam|lama|nunggu)|makasih\s+ya.{0,35}(?:lama|lambat))\b',text,re.I|re.S):flags.append('sarcasm')
    return flags

def clause_aspects(part):
    s=soften_repeated(part)
    candidates={a for a,p in TARGETS.items() if p.search(s)}
    # Domain-specific distinctions and overlap resolution
    only_clean=re.search(r'\b(?:toilet|wc|kamar mandi|meja|kursi|ruangan|lantai|peralatan)\w*\b',s) and TARGETS['cleanliness'].search(s)
    facility_op=re.search(r'\b(?:tersedia|tidak\s+tersedia|gak\s+ada|ga\s+ada|ada|nggak\s+ada|rusak|tidak\s+berfungsi|nggak\s+bisa|ngga\s+bisa|kurang|sempit|terbatas|banyak|cukup|melimpah|rusak|mati|lemot|lambat|kapasitas|fungsi|susah|error|eror|bermasalah|luas|kosong)\b',s)
    if only_clean and not facility_op and not re.search(r'\b(wifi|internet|parkir|photobooth|colokan|stop kontak|ac|mushola|musholla)\b',s):
        candidates.discard('facilities')
    if 'ambience' in candidates and 'facilities' in candidates:
        # Generic room/space description plus explicit amenity: keep ambience only if independent ambience evaluation
        amb_eval= re.search(r'\b(?:nyaman|cozy|enak\s+buat|vibe|suasana|adem|aesthetic|estetik|interior|berisik|bising|rame|ramai|tenang|pemandangan|view|nongkrong|betah|nugas|wfc|working space|sempit|luas|outdoor|indoor)\b',s)
        if not amb_eval: candidates.discard('ambience')
    if 'product_quality' in candidates and 'service' in candidates:
        # order of food, response time is service, not automatically food quality
        if re.search(r'\b(?:pesanan|pesenan|pesen|order|makanan|minuman)\b',s) and re.search(r'\b(?:lama|nunggu|cepat|telat|dateng|datang|keluar|disajikan)\b',s) and not re.search(r'\b(?:enak|rasa|porsi|hambar|menu|basi|gosong|lezat|nikmat|manis|segar|pahit)\b',s):
            candidates.discard('product_quality')
    if 'price_value' in candidates and re.search(r'\bdompet\b',s) and not re.search(r'\b(?:harga|bayar|mahal|murah|uang|biaya|worth|kantong|menjerit)\b',s): candidates.discard('price_value')
    if 'ambience' in candidates and 'service' in candidates and re.search(r'\b(?:pelayan|staff|staf|barista|kasir|pegawai|karyawan|service)\w*\b',s):
        if not re.search(r'\b(?:nyaman|cozy|suasana|vibe|nugas|nongkrong|wfc|interior|berisik|pemandangan|view|adem|tempat\w*|luas|sempit)\b',s): candidates.discard('ambience')
    # The location (provisional) should not trigger the ambience label by itself
    if LOCATION.search(s) and 'ambience' in candidates and not re.search(r'\b(?:nyaman|cozy|pemandangan|suasana|view|nugas|nongkrong|wfc|interior|vibes|tempatnya\s+(?:enak|bagus|adem))\b',s):
        if re.search(r'\b(?:lokasi|strategis|dekat|jalan|akses)\b',s): candidates.discard('ambience')
    # Implicit service quality: timing for ordered food, or forced eviction while visiting.
    if re.search(r'\b(?:lama|cepat|telat|lambat|nunggu|menunggu)\b',s) and re.search(r'\b(?:makan\w*|minum\w*|pesanan|order|dateng|datang|keluar)\b',s):
        candidates.add('service')
        if not re.search(r'\b(?:enak|rasa|porsi|hambar|basi|gosong|lezat|nikmat|manis|segar|pahit|burger|kopi|latte)\b',s):candidates.discard('product_quality')
    if re.search(r'\b(?:diusir|di\s*usir|dipaksa\s+beli)\b',s):candidates.add('service')
    # Facility terms in food/service clause should not automatically signal separate amenity claims
    if 'facilities' in candidates and re.search(r'\b(?:kasir|barista|staff|pelayan)\b',s) and re.search(r'\b(?:meja|table)\b',s) and not re.search(r'\b(?:kursi|colokan|wifi|parkir|toilet|fasilitas|banyak meja|meja kosong|mejanya rusak|meja kotor)\b',s):candidates.discard('facilities')
    return candidates

def score_polarity(part,aspect):
    """Return sentiment / reason, prioritizing negation and absence over lexical positives."""
    s=soften_repeated(part)
    if SPECIAL_UNCERTAIN.search(s) and not re.search(r'\b(?:pesanan|pelayanan|barista|waiter|cepat\s+banget.*jam)\b',s):return (None,'Ambiguous wording requires context')
    if re.search(r'\b(?:bukan\s+berarti\s+tidak|bukannya\s+tidak)\b',s):return (None,'Double negation: polarity not safely inferred')
    if re.search(r'\b(?:tidak|nggak|ngga|ga|gak|gk|tak|not)\s+(?:terlalu\s+)?mahal\b',s) and aspect=='price_value':return ('positive','Negated expensiveness')
    if NEG_NEG.search(s):return ('positive','Negated negative evaluation')
    if aspect=='ambience' and re.search(r'\b(?:tidak|nggak|ngga|gak|ga|gk|tak)\s+(?:terlalu\s+)?(?:panas|berisik|rame|ramai|pengap|crowded|bising)\b',s):return ('positive','Absence of ambience discomfort')
    if NEG_POS.search(s):return ('negative','Negated positive evaluation')
    # context scoped by target
    if aspect=='cleanliness':
        if re.search(r'\b(?:kotor|jorok|pesing|sampah\s+berserakan|bau\s+(?:sampah|pesing)|berbau|berdebu|lengket|lalat|kecoa|semut|tikus|tidak\s+bersih|kurang\s+bersih|ga\s+bersih)\b',s):return ('negative','Physical hygiene complaint')
        if re.search(r'\b(?:bersih\w*|clean\w*|higien\w*|terawat|rapi)\b',s):return ('positive','Physical hygiene praise')
        return ('neutral','Factual hygiene reference')
    if aspect=='price_value':
        if re.search(r'\b(?:kemahalan|mahal\w*|overpriced|overprice|pricey|pricy|dompet\s+menjerit|tidak\s+worth|nggak\s+worth|ga\s+worth|kurang\s+worth|harga\s+(?:tidak|ga|gak)\s+(?:sesuai|sepadan))\b',s):return ('negative','Price/value complaint')
        if re.search(r'\b(?:harga\s+(?:pelajar|mahasiswa|bersahabat)|murah\w*|muraah\w*|terjangkau|afford\w*|bersahabat|worth\w*|value\s+for\s+money|ramah\s+(?:di\s+)?kantong|hemat|low\s*budget|budget\s+mahasiswa|promo|voucher|diskon)\b',s):return ('positive','Favorable price/value or promotion')
        return ('neutral','Price information without clear valuation')
    if aspect=='facilities':
        if re.search(r'\b(?:tidak|gak|ga|ngga|nggak|gk|belum)\s+(?:ada|tersedia|berfungsi|bisa\s+(?:dipakai|nyambung|terhubung|ngeprint))\b|\b(?:rusak|eror|error|lemot|lambat|slow|susah|sulit|kurang|terbatas|habis|mati|kosong|hilang|jelek|bad|gajelas)\b',s):return ('negative','Unavailable/poor amenity')
        if re.search(r'\b(?:lancar|kuat|kencang|kenceng|cepat|melimpah|banyak|luas|lega|cukup|bagus|oke|nyaman|berfungsi|bersahabat|lengkap|mudah|gampang)\b',s):return ('positive','Amenity favorable function/capacity')
        # Availability alone is neutral per guideline.
        return ('neutral','Factual amenity mention/availability')
    if aspect=='product_quality':
        if re.search(r'\b(?:basi|gosong|mentah|keras|hambar|anyep|pahit|keasinan|asin\s+banget|kemanisan|terlalu\s+manis|terlalu\s+asin|kurang\s+kopi|kurang\s+rasa|rasa\s+.*?(?:aneh|buruk|jelek|ga\s+konsisten)|tidak\s+enak|gak\s+enak|ga\s+enak|kurang\s+enak|tidak\s+segar|kecil\s+banget|tidak\s+sesuai\s+foto|porsinya\s+.*?sedikit|stok\s+habis|menu\s+.*?\s+habis|menu\s+.*?\s+kosong|bau\s+(?:sabun|sunlight)|aroma\s+aneh|menu\s+.*?\s+nggak\s+ada)\b',s):return ('negative','Unfavorable food/drink quality or availability')
        if re.search(r'\b(?:enak\w*|enaak\w*|nikmat\w*|lezat|mantap\w*|mantep\w*|manta+p+\w*|juara\w*|suka\w*|favorit\w*|favorite|fresh|segar|porsi\s+besar|porsinya\s+pas|beragam|bervariasi|banyak\s+pilihan|menarik|delicious|yummy|tasty|rasa\s+(?:unik|khas|enak)|harum|aroma\s+.*?wangi|lembut|pas\s+di\s+lidah|top\b|oke\w*|good|nice|great|best\w*|recommended|rekomen\w*|puas\w*|cakep|cantik|gurih|maknyus|nampol)\b',s):return ('positive','Favorable food/drink evaluation')
        # 'menu banyak', 'makanan tersedia' remain factual unless evaluation explicit
        return ('neutral','Factual product/menu mention')
    if aspect=='service':
        if re.search(r'\b(?:diusir|di\s*usir|dipaksa\s+beli)\b',s):return ('negative','Hostile forced removal/request')
        if re.search(r'\bbaru\s+(?:datang|dateng|disajikan|diantar)\s+setelah\s+(?:\d+|satu|dua|setengah)\s+(?:jam|menit)\b',s):return ('negative','Excessive waiting time for order')
        if re.search(r'\b(?:lama|telat|lambat|slow|nunggu|menunggu|kurang|jutek|cuek|galak|nggak\s+ramah|ga\s+ramah|tidak\s+ramah|tidak\s+responsif|diabaikan|lupa|salah\s+order|salah\s+pesan|gajelas|jelek|parah|buruk|tidak\s+profesional|diusir|di\s*usir|bad|worse|jelek|parah|marah|tidak\s+sigap)\b',s):return ('negative','Unfavorable service interaction/timing')
        if re.search(r'\b(?:langsung\s+di\s+amankan|diamankan|ramah\w*|rmah\w*|baik\w*|helpful|friendly|cepat\w*|sigap|gercep|fast|responsif|sopan|suka\w*|seneng|senyum|puas\w*|bagus\w*|mantep\w*|manta+p+\w*|mantap\w*|oke\w*|best\w*|terbaik|great|excellent|good|memuaskan|cekatan|terbantu|top\b|welcome|welcoming|solutif|bantu)\b',s):return ('positive','Favorable service interaction/timing')
        return ('neutral','Service process stated without evaluation')
    if aspect=='ambience':
        if re.search(r'\b(?:tidak\s+nyaman|ga\s+nyaman|gak\s+nyaman|ngga\s+nyaman|kurang\s+nyaman|sempit|berisik|bising|crowded|terlalu\s+ramai|panas|gerah|kaku|bikin\s+pusing|gelap|ribut|sumpek|sesak|silau|pengap|bosen|tidak\s+betah)\b',s):return ('negative','Unfavorable ambience/comfort')
        if re.search(r'\b(?:nyaman\w*|nyamann\w*|cozy\w*|chozy\w*|comfort\w*|comf\w*|adem\w*|sejuk|syahdu|tenang|nice|good|great|homy|homey|aesthe\w*|estetik\w*|instagrammable|asik|asyik|seru|enak\s+buat|cocok\s+buat|cocok\s+untuk|bikin\s+betah|betah|luas|lega|lapang|keren|bagus|cantik|menarik|sunyi|pw\b|nge\s*date)\b',s):return ('positive','Favorable ambience/comfort')
        if (POS.search(s) or re.search(r'\b(?:nice|good|great|perfect)\b',s)) and re.search(r'\b(?:tempat|suasana|vibe|pemandangan|view|interior|musik|ruangan|outdoor|indoor)\w*\b',s):return ('positive','Favorable ambience target')
        return ('neutral','Factual space/atmosphere mention')
    return (None,'No polarity assessment')

def make_record(row,aspect,presence='not_mentioned',ev=None,notes='',flags=None):
    ev=ev or []; flags=flags or []
    polarities={e['opinion_sentiment'] for e in ev if e['opinion_sentiment'] is not None}
    evaluative=polarities.intersection({'positive','negative'})
    mixed=len(evaluative)==2
    # A neutral/factual evidence does not cancel a single evaluative polarity.
    if mixed: senti=None
    elif len(evaluative)==1:senti=next(iter(evaluative))
    elif polarities=={'neutral'}:senti='neutral'
    else:senti=None
    unknown=any(e['opinion_sentiment'] is None for e in ev)
    uncertain=(presence=='uncertain' or (presence=='mentioned' and (unknown or (senti is None and not mixed))))
    if mixed: notes=(notes+' | ' if notes else '')+'Positive and negative evidence in same aspect; retain both; exclude 3-class training.'
    if unknown: notes=(notes+' | ' if notes else '')+'At least one opinion remains unresolvable; verify before using.'
    if presence=='uncertain' and not notes:notes='Target/aspect cannot be disambiguated from text.'
    if uncertain and not notes:notes='Present target but ambiguous polarity; human adjudication needed.'
    types={e['mention_type'] for e in ev}
    mention_type= ('mixed' if len(types)>1 else next(iter(types))) if ev else None
    if presence=='uncertain':mention_type=None if not ev else mention_type
    status='uncertain' if uncertain else 'draft'
    return dict(annotation_id='PRE_'+hashlib.sha256((str(row.review_id)+'|'+aspect+'|'+ANNOTATOR).encode()).hexdigest()[:24],review_id=str(row.review_id),coffee_shop_id=get_shop_id(row.url_tempat),data_origin='authorized_review',review_text=str(row.teks_review),aspect_category=aspect,aspect_presence=presence,sentiment=senti,mention_type=mention_type,mixed_sentiment=mixed,evidence=ev,annotation_status=status,annotator_id=ANNOTATOR,taxonomy_version=VERSION,adjudication_status='pending' if uncertain else 'not_required',training_eligible=False,notes=notes,review_flags=sorted(set(flags)))

def decide_review(row):
    text=str(row.teks_review); clauses=segments(text)
    evidence=collections.defaultdict(list); ambi={}; flags=detect_flags(text)
    target_mentions=set()
    for ix,(a,b,fragment) in enumerate(clauses):
        clean=fragment.strip(' \t\r\n.,;:!?')
        if not clean:continue
        aa=a+fragment.find(clean); bb=aa+len(clean)
        candidates=clause_aspects(clean)
        # Split clause if multiple explicit targets? Keep minimal contiguous fragment, avoid inventing words.
        for aspect in sorted(candidates,key=ASPECTS.index):
            target_mentions.add(aspect)
            pol,reason=score_polarity(clean,aspect)
            # Factual bare visit/mention is neutral, but sentiment-less long, subjective words may need review
            if pol=='neutral' and re.search(r'\b(?:suka|parah|sayang|agak|kurang|hanya|cmn|cuma|cuman|tapi|sebenernya|kenapa|kok|what)\b',clean,re.I) and len(clean)>35:
                pol=None; ambi[aspect]='Aspect mentioned, subjective evaluation not safely resolved.'
            # Facility: keep only cleanliness for 'toilet kotor' unless other amenity predicate exists
            implicit= bool(aspect=='service' and re.search(r'\b(?:nunggu|menunggu|antri|antre|pesanan|pesen|order)\b',clean,re.I) and not re.search(r'\b(?:pelayan|service|barista|pegawai|staff|staf|kasir|waiter)\w*\b',clean,re.I))
            implicit |= bool(aspect=='ambience' and re.search(r'\b(?:nugas|nongkrong|wfc|bikin\s+betah|fokus\s+kerja)\b',clean,re.I) and not re.search(r'\b(?:tempat|suasana|atmos|ambien|cozy|nyaman|view|vibes|interior)\w*\b',clean,re.I))
            evidence[aspect].append(dict(quote=text[aa:bb],start=aa,end=bb,opinion_sentiment=pol,mention_type='implicit' if implicit else 'explicit',target=aspect))
            if pol is None:ambi[aspect]=ambi.get(aspect,reason)
    if not target_mentions:
        if GENERAL.search(text) or PRAISE_ONLY.search(text):
            flags.append('general_praise')
        elif LOCATION.search(text):pass
        else:flags.append('needs_context')
        # An object-free negative speed remark is impossible to assign to service confidently
        if re.search(r'\b(?:lambat\s+sekali|lama\s+banget|enak\s+banget|ga\s+enak|nggak\s+enak|ramah\s+banget)\b',text,re.I):
            flags.append('needs_context')
    # Object-free 'lambat sekali': explicitly withhold service decision
    uncertain_aspects=set()
    if not target_mentions and re.search(r'\b(?:lambat|lama\s+banget|pelan\s+banget|slow\s+banget)\b',text,re.I):
        uncertain_aspects.add('service')
    if not target_mentions and re.search(r'\b(?:enak\w*|nikmat|lezat)\b',text,re.I):
        uncertain_aspects.update({'product_quality','ambience'})
    if not target_mentions and re.search(r'\b(?:ramah\w*|rmah\w*)\b',text,re.I):
        uncertain_aspects.add('service')
    result=[]
    for aspect in ASPECTS:
        ev=evidence.get(aspect,[])
        if ev:
            # If neutral and subjective evidence appears with another clear polarity, ignore neutral in vote not in record
            polarityset={e['opinion_sentiment'] for e in ev if e['opinion_sentiment'] in ('positive','negative')}
            if polarityset and any(e['opinion_sentiment']=='neutral' for e in ev):
                for e in ev:
                    if e['opinion_sentiment']=='neutral': pass
            note=ambi.get(aspect,'')
            if any(e['opinion_sentiment'] is None for e in ev):
                note=note or 'At least one evidence has ambiguous polarity; human review required.'
                if len(ev)>1 and any(e['opinion_sentiment'] is not None for e in ev):
                    # Don't silently ignore unknown evidence and assign a confident polarity
                    for e in ev: e['opinion_sentiment']=None if e['opinion_sentiment'] is None else e['opinion_sentiment']
            res=make_record(row,aspect,'mentioned',ev,notes=note,flags=flags)
            if any(e['opinion_sentiment'] is None for e in ev):
                res['sentiment']=None;res['annotation_status']='uncertain';res['adjudication_status']='pending'
            result.append(res)
        elif aspect in uncertain_aspects:
            result.append(make_record(row,aspect,'uncertain',notes='No explicit target. Cannot infer this aspect from object-free evaluative fragment.',flags=flags))
        else:result.append(make_record(row,aspect,flags=flags))
    return result


def fixture_diagnostic():
    fixtures=json.loads((ROOT/'synthetic_reviews.json').read_text())
    outcomes=[]
    class Rec:pass
    for fixture in fixtures:
        obj=Rec();obj.review_id=fixture['review']['review_id'];obj.teks_review=fixture['review']['review_text'];obj.url_tempat='https://example.com?query_place_id=SYN_SHOP'
        pred=decide_review(obj)
        gold=fixture['response']['decisions'];match=0
        diffs=[]
        for row,g in zip(pred,gold):
            expected=(g['presence'],g['sentiment'],g['mixed_sentiment'])
            actual=(row['aspect_presence'],row['sentiment'],row['mixed_sentiment'])
            if expected==actual:match+=1
            else:diffs.append({'aspect':row['aspect_category'],'expected':expected,'predicted':actual})
        outcomes.append({'case':fixture['case'],'pair_agree':match,'pairs':6,'differences':diffs})
    return outcomes

def main():
    df=pd.read_csv(SOURCE,encoding='utf-8-sig',keep_default_na=False)
    assert len(df)==df.review_id.nunique()
    out=ROOT/'brewscope_annotation_draft';out.mkdir(exist_ok=True)
    allrows=[];reviews=[]
    for row in df.itertuples(index=False):
        pair=decide_review(row)
        allrows.extend(pair)
        decisions={x['aspect_category']: {'presence':x['aspect_presence'],'sentiment':x['sentiment'],'mixed_sentiment':x['mixed_sentiment'],'annotation_status':x['annotation_status']} for x in pair}
        flagged=sorted(set(f for r in pair for f in r['review_flags']))
        reviews.append({'review_id':str(row.review_id),'coffee_shop_id':pair[0]['coffee_shop_id'],'review_text':str(row.teks_review),'source_row_number':row.source_row_number,'decisions':decisions,'review_flags':flagged,'review_needs_manual_review':bool(flagged or any(p['annotation_status']=='uncertain' or p['mixed_sentiment'] for p in pair) or len(row.teks_review)>220 or sum(p['aspect_presence']=='mentioned' for p in pair)>2),'needs_language_review_in_source':bool(row.needs_language_review),'needs_privacy_review_in_source':bool(row.needs_privacy_review)})
    with (out/'annotations_full.jsonl').open('w',encoding='utf-8') as fp:
        for p in allrows:fp.write(json.dumps(p,ensure_ascii=False)+'\n')
    flat=[]
    for p in allrows:
        flat.append({**{k:v for k,v in p.items() if k not in ('evidence','review_flags')},'evidence_json':json.dumps(p['evidence'],ensure_ascii=False),'review_flags_json':json.dumps(p['review_flags'],ensure_ascii=False)})
    pd.DataFrame(flat).to_csv(out/'annotations_flat.csv',index=False,encoding='utf-8-sig')
    res=[]
    for r in reviews:
        x={k:v for k,v in r.items() if k!='decisions'}
        x['review_flags']=';'.join(r['review_flags'])
        for a,d in r['decisions'].items():
            x[a+'_presence']=d['presence'];x[a+'_sentiment']=d['sentiment'];x[a+'_mixed']=d['mixed_sentiment'];x[a+'_annotation_status']=d['annotation_status']
        res.append(x)
    pd.DataFrame(res).to_csv(out/'review_level_summary.csv',index=False,encoding='utf-8-sig')
    # Review queue: all uncertain, mixed, domain gaps, very long, multi-aspect or prior language flags
    queue=[]
    for row,src in zip(reviews,df.itertuples(index=False)):
        uncertain=[k for k,v in row['decisions'].items() if v['annotation_status']=='uncertain']
        mixed=[k for k,v in row['decisions'].items() if v['mixed_sentiment']]
        flags=row['review_flags']
        reasons=[]
        if uncertain:reasons.append('uncertain:'+','.join(uncertain))
        if mixed:reasons.append('mixed:'+','.join(mixed))
        if 'out_of_taxonomy' in flags:reasons.append('out_of_taxonomy')
        if 'needs_context' in flags:reasons.append('needs_context')
        if 'sarcasm' in flags:reasons.append('sarcasm')
        if bool(src.needs_language_review):reasons.append('source_language_review')
        if bool(src.needs_privacy_review):reasons.append('source_privacy_review')
        if len(row['review_text'])>220:reasons.append('long_review')
        if sum(v['presence']=='mentioned' for v in row['decisions'].values())>2:reasons.append('multi_aspect_3plus')
        if not reasons and 'general_praise' in flags:reasons.append('general_praise')
        if not reasons and all(v['presence']=='not_mentioned' for v in row['decisions'].values()):reasons.append('no_detected_aspect')
        if reasons:
            priority= 'HIGH' if uncertain or mixed or 'sarcasm' in flags else ('MEDIUM' if len(reasons)>1 or len(row['review_text'])>220 or 'out_of_taxonomy' in flags else 'LOW')
            queue.append(dict(review_id=row['review_id'],coffee_shop_id=row['coffee_shop_id'],review_text=row['review_text'],priority=priority,reasons=';'.join(reasons),mentioned_aspects=';'.join(a for a,d in row['decisions'].items() if d['presence']=='mentioned'),source_row_number=row['source_row_number']))
    pd.DataFrame(queue,columns=['review_id','coffee_shop_id','review_text','priority','reasons','mentioned_aspects','source_row_number']).to_csv(out/'manual_review_queue.csv',index=False,encoding='utf-8-sig')
    # Strict validation schema + offset + each review has exactly six unique aspects.
    validator=jsonschema.Draft202012Validator(SCHEMA)
    errors=[];id_set=set();counts=collections.defaultdict(set); sentiments=collections.Counter(); statuses=collections.Counter(); presence=collections.Counter(); aspect_counts=collections.Counter(); mixedn=0;evidn=0
    for i,p in enumerate(allrows):
        vv=list(validator.iter_errors(p))
        for e in vv[:3]:errors.append({'row':i,'reason':e.message})
        if p['annotation_id'] in id_set:errors.append({'row':i,'reason':'duplicate annotation_id'})
        id_set.add(p['annotation_id'])
        if p['aspect_category'] in counts[p['review_id']]:errors.append({'row':i,'reason':'duplicate aspect on review'})
        counts[p['review_id']].add(p['aspect_category'])
        for evidence in p['evidence']:
            evidn+=1
            if not (0<=evidence['start']<evidence['end']<=len(p['review_text']) and p['review_text'][evidence['start']:evidence['end']]==evidence['quote']):errors.append({'row':i,'reason':'incorrect evidence quote/offset'})
        presence[(p['aspect_category'],p['aspect_presence'])]+=1
        if p['sentiment']:sentiments[(p['aspect_category'],p['sentiment'])]+=1
        statuses[p['annotation_status']]+=1
        aspect_counts[p['aspect_category']]+=1
        mixedn+=p['mixed_sentiment']
    for k,v in counts.items():
        if v!=set(ASPECTS):errors.append({'review_id':k,'reason':'wrong aspect set'})
    fixture=fixture_diagnostic()
    report={
     'result_kind':'OFFLINE_RULE_BASED_PREANNOTATION_NOT_HUMAN_GOLD',
     'source_file':SOURCE.name,'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'taxonomy_version':VERSION,'annotator_id':ANNOTATOR,'review_count':len(reviews),'distinct_review_ids':len(counts),'source_shop_name_count':df.nama_tempat.nunique(),'pseudonymous_coffee_shop_ids':len({r['coffee_shop_id'] for r in reviews}),
     'aspect_decisions':len(allrows),'expected_six_per_review':len(reviews)*6,'aspect_rows':dict(aspect_counts),'presence_counts':{k[0]+'|'+k[1]:v for k,v in sorted(presence.items())},'sentiment_counts':{k[0]+'|'+k[1]:v for k,v in sorted(sentiments.items())},'status_counts':dict(statuses),'mixed_pairs':mixedn,'evidence_spans':evidn,'flag_counts':dict(collections.Counter(f for r in reviews for f in r['review_flags'])),'manual_review_queue_reviews':len(queue),'manual_review_priority':dict(collections.Counter(r['priority'] for r in queue)),
     'validation':{'schema_and_offset_errors':len(errors),'all_unique_aspects_per_review':all(v==set(ASPECTS) for v in counts.values()),'all_training_eligible_false':all(not v['training_eligible'] for v in allrows),'errors':errors[:25]},
     'synthetic_fixture_diagnostic':{'total_cases':len(fixture),'pair_agreement':sum(z['pair_agree'] for z in fixture),'total_pairs':6*len(fixture),'cases':fixture},
     'provenance_and_limitations':['AI-generated label candidates from deterministic lexical heuristics only; NOT direct contextual human or LLM review of every text','Labels are draft and NEVER human gold; all training_eligible=false until quality control and Stage 4 gates','Not_mentioned reflects unrecognized mention under rules; false negative risk','No ratings were read for any label; names/URLs used only for shop pseudonym identifier','No external network/API or review transfer performed','40 shops geographic verification and source permissions still require independent documentation','Absent privacy flags in input do not constitute a privacy rights audit']}
    (out/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    pd.DataFrame([{'case':z['case'],'pair_agree':z['pair_agree'],'total_pairs':z['pairs'],'differences':json.dumps(z['differences'],ensure_ascii=False)} for z in fixture]).to_csv(out/'synthetic_fixture_diagnostic.csv',index=False,encoding='utf-8-sig')
    print(json.dumps({k:report[k] for k in ('review_count','aspect_decisions','status_counts','mixed_pairs','evidence_spans','manual_review_queue_reviews','manual_review_priority','validation')},ensure_ascii=False,indent=2))
    print('fixtures:',sum(z['pair_agree'] for z in fixture),'/',len(fixture)*6)
    print('outputs',out)
    if errors:raise SystemExit('Schema / offset validation failed')

if __name__=='__main__':main()
