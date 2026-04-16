"""
add_translation_keys.py
Adds missing tooltip, File Lab, content-style, and other translation keys
to translations.json and switches language_names to native script.
Run once: python add_translation_keys.py
"""
import json, os

PATH = os.path.join(os.path.dirname(__file__), "translations.json")

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)

# ── 1. Native-language names in meta ──────────────────────────────────────
data["meta"]["language_names"] = {
    "en":    "English",
    "es":    "Español",
    "fr":    "Français",
    "de":    "Deutsch",
    "pt-BR": "Português (Brasil)",
    "it":    "Italiano",
    "nl":    "Nederlands",
    "ru":    "Русский",
    "ja":    "日本語",
    "zh-CN": "中文（简体）",
    "ko":    "한국어",
    "pl":    "Polski",
    "tr":    "Türkçe",
    "ar":    "العربية",
    "hi":    "हिन्दी",
    "sv":    "Svenska",
}

# ── 2. New string keys ──────────────────────────────────────────────────
NEW_KEYS = {

  # File Lab card headers
  "FILE_LAB_AUDIO_HEADER": {
    "value":"Audio Conversion","en":"Audio Conversion",
    "es":"Conversión de audio","fr":"Conversion audio","de":"Audiokonvertierung",
    "pt-BR":"Conversão de áudio","it":"Conversione audio","nl":"Audioconversie",
    "ru":"Конвертация аудио","ja":"音声変換","zh-CN":"音频转换",
    "ko":"오디오 변환","pl":"Konwersja audio","tr":"Ses Dönüştürme",
    "ar":"تحويل الصوت","hi":"ऑडियो रूपांतरण","sv":"Ljudkonvertering"
  },
  "FILE_LAB_COMBINE_HEADER": {
    "value":"Combine Audio Files → Audiobook","en":"Combine Audio Files → Audiobook",
    "es":"Combinar archivos de audio → Audiolibro",
    "fr":"Combiner des fichiers audio → Livre audio",
    "de":"Audiodateien zusammenführen → Hörbuch",
    "pt-BR":"Combinar arquivos de áudio → Audiolivro",
    "it":"Combina file audio → Audiolibro",
    "nl":"Audiobestanden combineren → Luisterboek",
    "ru":"Объединение аудиофайлов → Аудиокнига",
    "ja":"音声ファイルを結合 → オーディオブック",
    "zh-CN":"合并音频文件 → 有声书",
    "ko":"오디오 파일 합치기 → 오디오북",
    "pl":"Połącz pliki audio → Audiobook",
    "tr":"Ses Dosyalarını Birleştir → Sesli Kitap",
    "ar":"دمج الملفات الصوتية → كتاب صوتي",
    "hi":"ऑडियो फ़ाइलें जोड़ें → ऑडियोबुक",
    "sv":"Kombinera ljudfiler → Ljudbok"
  },

  # File Lab audio format notes
  "FILE_LAB_AUDIO_NOTE_CHAPTERS": {
    "value":"Chapters preserved if source has them","en":"Chapters preserved if source has them",
    "es":"Capítulos conservados si la fuente los tiene",
    "fr":"Chapitres conservés si la source en possède",
    "de":"Kapitel werden beibehalten, wenn die Quelle sie enthält",
    "pt-BR":"Capítulos preservados se a fonte os tiver",
    "it":"Capitoli preservati se la sorgente li contiene",
    "nl":"Hoofdstukken bewaard als de bron ze heeft",
    "ru":"Главы сохраняются, если они есть в источнике",
    "ja":"ソースにある場合はチャプターが保持されます",
    "zh-CN":"如果源文件有章节则保留",
    "ko":"원본에 챕터가 있으면 보존됩니다",
    "pl":"Rozdziały zachowane, jeśli źródło je zawiera",
    "tr":"Kaynakta varsa bölümler korunur",
    "ar":"الفصول محفوظة إذا كانت المصدر يحتوي عليها",
    "hi":"यदि स्रोत में हैं तो अध्याय सुरक्षित रहते हैं",
    "sv":"Kapitel bevaras om källan har dem"
  },
  "FILE_LAB_AUDIO_NOTE_MP3": {
    "value":"ID3v2 chapter tags embedded — data survives re-encoding to M4B/MP4 later",
    "en":"ID3v2 chapter tags embedded — data survives re-encoding to M4B/MP4 later",
    "es":"Etiquetas de capítulo ID3v2 incrustadas — los datos sobreviven a la recodificación a M4B/MP4",
    "fr":"Balises de chapitre ID3v2 intégrées — les données survivent au réencodage en M4B/MP4",
    "de":"ID3v2-Kapitel-Tags eingebettet — Daten bleiben bei Re-Encodierung in M4B/MP4 erhalten",
    "pt-BR":"Tags de capítulo ID3v2 incorporadas — dados sobrevivem à recodificação para M4B/MP4",
    "it":"Tag capitolo ID3v2 incorporati — i dati sopravvivono alla ricodifica in M4B/MP4",
    "nl":"ID3v2 hoofdstuktags ingesloten — gegevens overleven hercodering naar M4B/MP4",
    "ru":"Встроенные теги глав ID3v2 — данные сохраняются при перекодировании в M4B/MP4",
    "ja":"ID3v2チャプタータグ埋め込み — M4B/MP4への再エンコード後もデータが保持されます",
    "zh-CN":"嵌入 ID3v2 章节标签 — 重新编码为 M4B/MP4 后数据依然保留",
    "ko":"ID3v2 챕터 태그 포함 — M4B/MP4로 재인코딩해도 데이터 유지",
    "pl":"Osadzone tagi rozdziałów ID3v2 — dane przeżywają ponowne kodowanie do M4B/MP4",
    "tr":"ID3v2 bölüm etiketleri gömülü — veriler M4B/MP4'e yeniden kodlamadan sonra da korunur",
    "ar":"علامات الفصول ID3v2 مضمنة — البيانات تبقى عند إعادة الترميز إلى M4B/MP4",
    "hi":"ID3v2 चैप्टर टैग एम्बेडेड — M4B/MP4 में री-एन्कोडिंग के बाद भी डेटा बचा रहता है",
    "sv":"ID3v2-kapiteltaggar inbäddade — data överlever omkodning till M4B/MP4"
  },
  "FILE_LAB_AUDIO_NOTE_WAV": {
    "value":"⚠ Chapter metadata will be lost — WAV has no chapter support",
    "en":"⚠ Chapter metadata will be lost — WAV has no chapter support",
    "es":"⚠ Los metadatos de capítulo se perderán — WAV no tiene soporte de capítulos",
    "fr":"⚠ Les métadonnées de chapitre seront perdues — WAV ne prend pas en charge les chapitres",
    "de":"⚠ Kapitel-Metadaten gehen verloren — WAV unterstützt keine Kapitel",
    "pt-BR":"⚠ Metadados de capítulo serão perdidos — WAV não tem suporte a capítulos",
    "it":"⚠ I metadati del capitolo andranno persi — WAV non supporta i capitoli",
    "nl":"⚠ Hoofdstukmetadata gaat verloren — WAV heeft geen hoofdstukondersteuning",
    "ru":"⚠ Метаданные глав будут утеряны — WAV не поддерживает главы",
    "ja":"⚠ チャプターのメタデータが失われます — WAVはチャプターをサポートしていません",
    "zh-CN":"⚠ 章节元数据将丢失 — WAV 不支持章节",
    "ko":"⚠ 챕터 메타데이터가 손실됩니다 — WAV는 챕터를 지원하지 않습니다",
    "pl":"⚠ Metadane rozdziałów zostaną utracone — WAV nie obsługuje rozdziałów",
    "tr":"⚠ Bölüm meta verisi kaybolacak — WAV bölüm desteğine sahip değil",
    "ar":"⚠ ستُفقد بيانات الفصول — WAV لا يدعم الفصول",
    "hi":"⚠ चैप्टर मेटाडेटा खो जाएगा — WAV में चैप्टर सपोर्ट नहीं है",
    "sv":"⚠ Kapitelmetadata förloras — WAV stöder inte kapitel"
  },
  "FILE_LAB_AUDIO_NOTE_FLAC": {
    "value":"Lossless · limited chapter support","en":"Lossless · limited chapter support",
    "es":"Sin pérdida · soporte de capítulos limitado",
    "fr":"Sans perte · prise en charge limitée des chapitres",
    "de":"Verlustfrei · eingeschränkte Kapitelunterstützung",
    "pt-BR":"Sem perda · suporte limitado a capítulos",
    "it":"Senza perdita · supporto capitoli limitato",
    "nl":"Verliesvrij · beperkte hoofdstukondersteuning",
    "ru":"Без потерь · ограниченная поддержка глав",
    "ja":"ロスレス · チャプターサポートは限定的",
    "zh-CN":"无损 · 有限章节支持",
    "ko":"무손실 · 제한적 챕터 지원",
    "pl":"Bezstratny · ograniczona obsługa rozdziałów",
    "tr":"Kayıpsız · sınırlı bölüm desteği",
    "ar":"بدون فقدان · دعم محدود للفصول",
    "hi":"लॉसलेस · सीमित चैप्टर सपोर्ट",
    "sv":"Förlustfritt · begränsat kapitelstöd"
  },

  # ── Speech Lab bottom-bar tooltips ──────────────────────────────────────
  "SPEECH_LAB_TOOLTIP_SPEED": {
    "value":"Playback speed — 1.0x is normal, 0.5x is half speed, 2.0x is double",
    "en":"Playback speed — 1.0x is normal, 0.5x is half speed, 2.0x is double",
    "es":"Velocidad de reproducción — 1.0x es normal, 0.5x es la mitad, 2.0x es el doble",
    "fr":"Vitesse de lecture — 1.0x est normale, 0.5x est la moitié, 2.0x est le double",
    "de":"Wiedergabegeschwindigkeit — 1.0x ist normal, 0.5x halbe, 2.0x doppelte Geschwindigkeit",
    "pt-BR":"Velocidade de reprodução — 1.0x é normal, 0.5x é metade, 2.0x é dobro",
    "it":"Velocità di riproduzione — 1.0x è normale, 0.5x è metà velocità, 2.0x è doppia",
    "nl":"Afspeelsnelheid — 1.0x is normaal, 0.5x is halve snelheid, 2.0x is dubbel",
    "ru":"Скорость воспроизведения — 1.0x нормальная, 0.5x половинная, 2.0x двойная",
    "ja":"再生速度 — 1.0xが標準、0.5xは半速、2.0xは倍速",
    "zh-CN":"播放速度 — 1.0x 为正常，0.5x 为半速，2.0x 为双倍",
    "ko":"재생 속도 — 1.0x가 정상, 0.5x는 절반 속도, 2.0x는 두 배",
    "pl":"Prędkość odtwarzania — 1.0x to normalna, 0.5x to połowa, 2.0x to podwójna",
    "tr":"Oynatma hızı — 1.0x normal, 0.5x yarı hız, 2.0x çift hız",
    "ar":"سرعة التشغيل — 1.0x طبيعية، 0.5x نصف السرعة، 2.0x ضعف السرعة",
    "hi":"प्लेबैक स्पीड — 1.0x सामान्य, 0.5x आधी, 2.0x दोगुनी",
    "sv":"Uppspelningshastighet — 1.0x är normal, 0.5x är halv hastighet, 2.0x är dubbel"
  },
  "SPEECH_LAB_TOOLTIP_VOLUME": {
    "value":"Playback volume — audio is peak-normalized before this is applied",
    "en":"Playback volume — audio is peak-normalized before this is applied",
    "es":"Volumen de reproducción — el audio se normaliza por pico antes de aplicarse",
    "fr":"Volume de lecture — l'audio est normalisé en crête avant application",
    "de":"Wiedergabelautstärke — Audio wird vor Anwendung auf Spitzenpegel normalisiert",
    "pt-BR":"Volume de reprodução — o áudio é normalizado por pico antes de ser aplicado",
    "it":"Volume di riproduzione — l'audio viene normalizzato al picco prima dell'applicazione",
    "nl":"Afspeelvolume — audio wordt gepiekt genormaliseerd voordat dit wordt toegepast",
    "ru":"Громкость воспроизведения — аудио нормализуется по пику перед применением",
    "ja":"再生音量 — 適用前にオーディオはピーク正規化されます",
    "zh-CN":"播放音量 — 应用前音频会进行峰值归一化",
    "ko":"재생 볼륨 — 적용 전 오디오는 피크 정규화됩니다",
    "pl":"Głośność odtwarzania — audio jest normalizowane szczytowo przed zastosowaniem",
    "tr":"Oynatma ses seviyesi — ses uygulanmadan önce tepe noktasına göre normalleştirilir",
    "ar":"مستوى صوت التشغيل — يتم تطبيع الصوت عند الذروة قبل التطبيق",
    "hi":"प्लेबैक वॉल्यूम — ऑडियो पीक-नॉर्मलाइज़ होने के बाद लागू होता है",
    "sv":"Uppspelningsvolym — ljud toppnormaliseras innan detta tillämpas"
  },
  "SPEECH_LAB_TOOLTIP_CADENCE": {
    "value":"Cadence — adds a brief pause between decoded speech chunks (Fish Speech only). 0% = no pause, 100% = ~600 ms gap. Has no effect on Kokoro.",
    "en":"Cadence — adds a brief pause between decoded speech chunks (Fish Speech only). 0% = no pause, 100% = ~600 ms gap. Has no effect on Kokoro.",
    "es":"Cadencia — añade una pausa breve entre fragmentos de voz (solo Fish Speech). 0% = sin pausa, 100% = ~600 ms. Sin efecto en Kokoro.",
    "fr":"Cadence — ajoute une courte pause entre les segments vocaux (Fish Speech uniquement). 0% = sans pause, 100% = ~600 ms. Sans effet sur Kokoro.",
    "de":"Kadenz — fügt eine kurze Pause zwischen Sprachblöcken ein (nur Fish Speech). 0% = keine Pause, 100% = ~600 ms. Kein Einfluss auf Kokoro.",
    "pt-BR":"Cadência — adiciona uma breve pausa entre blocos de fala (somente Fish Speech). 0% = sem pausa, 100% = ~600 ms. Sem efeito no Kokoro.",
    "it":"Cadenza — aggiunge una breve pausa tra i blocchi vocali (solo Fish Speech). 0% = nessuna pausa, 100% = ~600 ms. Nessun effetto su Kokoro.",
    "nl":"Cadans — voegt een korte pauze toe tussen spraakfragmenten (alleen Fish Speech). 0% = geen pauze, 100% = ~600 ms. Geen effect op Kokoro.",
    "ru":"Каданс — добавляет короткую паузу между речевыми блоками (только Fish Speech). 0% = без паузы, 100% = ~600 мс. Не влияет на Kokoro.",
    "ja":"ケイデンス — 音声チャンク間に短い間を追加します（Fish Speechのみ）。0% = 間なし、100% = ~600 ms。Kokoroには影響しません。",
    "zh-CN":"节奏 — 在语音块之间添加短暂停顿（仅限 Fish Speech）。0% = 无停顿，100% = ~600 毫秒。对 Kokoro 无效。",
    "ko":"케이던스 — 음성 청크 사이에 짧은 일시 정지를 추가합니다 (Fish Speech 전용). 0% = 일시 정지 없음, 100% = ~600 ms. Kokoro에는 영향 없음.",
    "pl":"Kadencja — dodaje krótką pauzę między fragmentami mowy (tylko Fish Speech). 0% = brak pauzy, 100% = ~600 ms. Brak efektu na Kokoro.",
    "tr":"Kadans — konuşma parçaları arasına kısa bir duraklama ekler (yalnızca Fish Speech). 0% = duraklama yok, 100% = ~600 ms. Kokoro'ya etkisi yok.",
    "ar":"الإيقاع — يضيف توقفًا مؤقتًا بين أجزاء الكلام (Fish Speech فقط). 0% = بدون توقف، 100% = ~600 مللي ثانية. لا تأثير على Kokoro.",
    "hi":"कैडेंस — स्पीच चंक्स के बीच संक्षिप्त विराम जोड़ता है (केवल Fish Speech)। 0% = कोई विराम नहीं, 100% = ~600 ms। Kokoro पर कोई प्रभाव नहीं।",
    "sv":"Kadans — lägger till en kort paus mellan talblock (endast Fish Speech). 0% = ingen paus, 100% = ~600 ms. Ingen effekt på Kokoro."
  },
  "SPEECH_LAB_TOOLTIP_PLAY_ALL": {
    "value":"Convert and play all items in the playlist","en":"Convert and play all items in the playlist",
    "es":"Convertir y reproducir todos los elementos de la lista",
    "fr":"Convertir et lire tous les éléments de la liste de lecture",
    "de":"Alle Elemente in der Wiedergabeliste konvertieren und abspielen",
    "pt-BR":"Converter e reproduzir todos os itens da lista",
    "it":"Converti e riproduci tutti gli elementi della playlist",
    "nl":"Alle items in de afspeellijst converteren en afspelen",
    "ru":"Конвертировать и воспроизвести все элементы плейлиста",
    "ja":"プレイリストのすべてのアイテムを変換して再生",
    "zh-CN":"转换并播放播放列表中的所有项目",
    "ko":"재생목록의 모든 항목 변환 및 재생",
    "pl":"Konwertuj i odtwórz wszystkie elementy playlisty",
    "tr":"Çalma listesindeki tüm öğeleri dönüştür ve oynat",
    "ar":"تحويل وتشغيل جميع العناصر في قائمة التشغيل",
    "hi":"प्लेलिस्ट में सभी आइटम को कन्वर्ट करें और चलाएं",
    "sv":"Konvertera och spela upp alla objekt i spellistan"
  },
  "SPEECH_LAB_TOOLTIP_CONVERT_SELECTED": {
    "value":"Convert selected items to speech","en":"Convert selected items to speech",
    "es":"Convertir elementos seleccionados a voz",
    "fr":"Convertir les éléments sélectionnés en parole",
    "de":"Ausgewählte Elemente in Sprache konvertieren",
    "pt-BR":"Converter itens selecionados para fala",
    "it":"Converti gli elementi selezionati in parlato",
    "nl":"Geselecteerde items naar spraak converteren",
    "ru":"Конвертировать выбранные элементы в речь",
    "ja":"選択したアイテムを音声に変換",
    "zh-CN":"将选定项目转换为语音",
    "ko":"선택된 항목을 음성으로 변환",
    "pl":"Konwertuj zaznaczone elementy na mowę",
    "tr":"Seçili öğeleri konuşmaya dönüştür",
    "ar":"تحويل العناصر المحددة إلى كلام",
    "hi":"चयनित आइटम को स्पीच में कन्वर्ट करें",
    "sv":"Konvertera valda objekt till tal"
  },
  "SPEECH_LAB_TOOLTIP_PAUSE_CONV": {
    "value":"Pause conversion","en":"Pause conversion",
    "es":"Pausar conversión","fr":"Mettre la conversion en pause",
    "de":"Konvertierung pausieren","pt-BR":"Pausar conversão",
    "it":"Metti in pausa la conversione","nl":"Conversie pauzeren",
    "ru":"Приостановить конвертацию","ja":"変換を一時停止",
    "zh-CN":"暂停转换","ko":"변환 일시 정지",
    "pl":"Wstrzymaj konwersję","tr":"Dönüşümü duraklat",
    "ar":"إيقاف التحويل مؤقتًا","hi":"कन्वर्ज़न रोकें","sv":"Pausa konvertering"
  },
  "SPEECH_LAB_TOOLTIP_STOP_CONV": {
    "value":"Stop / cancel conversion","en":"Stop / cancel conversion",
    "es":"Detener / cancelar conversión","fr":"Arrêter / annuler la conversion",
    "de":"Konvertierung stoppen / abbrechen","pt-BR":"Parar / cancelar conversão",
    "it":"Ferma / annulla la conversione","nl":"Conversie stoppen / annuleren",
    "ru":"Остановить / отменить конвертацию","ja":"変換を停止 / キャンセル",
    "zh-CN":"停止/取消转换","ko":"변환 중지/취소",
    "pl":"Zatrzymaj / anuluj konwersję","tr":"Dönüşümü durdur / iptal et",
    "ar":"إيقاف / إلغاء التحويل","hi":"कन्वर्ज़न रोकें / रद्द करें","sv":"Stopp / avbryt konvertering"
  },
  "SPEECH_LAB_TOOLTIP_PLAY_SELECTED": {
    "value":"Play audio for selected items","en":"Play audio for selected items",
    "es":"Reproducir audio para los elementos seleccionados",
    "fr":"Lire l'audio des éléments sélectionnés",
    "de":"Audio für ausgewählte Elemente abspielen",
    "pt-BR":"Reproduzir áudio para itens selecionados",
    "it":"Riproduci audio per gli elementi selezionati",
    "nl":"Audio afspelen voor geselecteerde items",
    "ru":"Воспроизвести аудио для выбранных элементов",
    "ja":"選択したアイテムのオーディオを再生",
    "zh-CN":"播放选定项目的音频","ko":"선택된 항목의 오디오 재생",
    "pl":"Odtwórz audio dla zaznaczonych elementów",
    "tr":"Seçili öğeler için ses oynat",
    "ar":"تشغيل الصوت للعناصر المحددة",
    "hi":"चयनित आइटम के लिए ऑडियो चलाएं",
    "sv":"Spela upp ljud för valda objekt"
  },
  "SPEECH_LAB_TOOLTIP_PAUSE_PB": {
    "value":"Pause playback","en":"Pause playback",
    "es":"Pausar reproducción","fr":"Mettre la lecture en pause",
    "de":"Wiedergabe pausieren","pt-BR":"Pausar reprodução",
    "it":"Metti in pausa la riproduzione","nl":"Afspelen pauzeren",
    "ru":"Приостановить воспроизведение","ja":"再生を一時停止",
    "zh-CN":"暂停播放","ko":"재생 일시 정지",
    "pl":"Wstrzymaj odtwarzanie","tr":"Oynatmayı duraklat",
    "ar":"إيقاف التشغيل مؤقتًا","hi":"प्लेबैक रोकें","sv":"Pausa uppspelning"
  },
  "SPEECH_LAB_TOOLTIP_STOP_PB": {
    "value":"Stop playback","en":"Stop playback",
    "es":"Detener reproducción","fr":"Arrêter la lecture",
    "de":"Wiedergabe stoppen","pt-BR":"Parar reprodução",
    "it":"Ferma la riproduzione","nl":"Afspelen stoppen",
    "ru":"Остановить воспроизведение","ja":"再生を停止",
    "zh-CN":"停止播放","ko":"재생 중지",
    "pl":"Zatrzymaj odtwarzanie","tr":"Oynatmayı durdur",
    "ar":"إيقاف التشغيل","hi":"प्लेबैक बंद करें","sv":"Stoppa uppspelning"
  },
  "SPEECH_LAB_TOOLTIP_EXPORT_MP3": {
    "value":"Export selected items as individual MP3 files",
    "en":"Export selected items as individual MP3 files",
    "es":"Exportar elementos seleccionados como archivos MP3 individuales",
    "fr":"Exporter les éléments sélectionnés en fichiers MP3 individuels",
    "de":"Ausgewählte Elemente als einzelne MP3-Dateien exportieren",
    "pt-BR":"Exportar itens selecionados como arquivos MP3 individuais",
    "it":"Esporta gli elementi selezionati come file MP3 individuali",
    "nl":"Geselecteerde items exporteren als afzonderlijke MP3-bestanden",
    "ru":"Экспортировать выбранные элементы как отдельные MP3-файлы",
    "ja":"選択したアイテムを個別のMP3ファイルとしてエクスポート",
    "zh-CN":"将选定项目导出为单独的 MP3 文件",
    "ko":"선택된 항목을 개별 MP3 파일로 내보내기",
    "pl":"Eksportuj zaznaczone elementy jako oddzielne pliki MP3",
    "tr":"Seçili öğeleri ayrı MP3 dosyaları olarak dışa aktar",
    "ar":"تصدير العناصر المحددة كملفات MP3 منفصلة",
    "hi":"चयनित आइटम को अलग MP3 फ़ाइलों के रूप में एक्सपोर्ट करें",
    "sv":"Exportera valda objekt som enskilda MP3-filer"
  },
  "SPEECH_LAB_TOOLTIP_AUDIOBOOK": {
    "value":"Merge selected items into one M4B audiobook with chapter marks",
    "en":"Merge selected items into one M4B audiobook with chapter marks",
    "es":"Combinar elementos seleccionados en un audiolibro M4B con marcas de capítulo",
    "fr":"Fusionner les éléments sélectionnés en un livre audio M4B avec marques de chapitre",
    "de":"Ausgewählte Elemente zu einem M4B-Hörbuch mit Kapitelmarken zusammenführen",
    "pt-BR":"Mesclar itens selecionados em um audiolivro M4B com marcadores de capítulo",
    "it":"Unisci gli elementi selezionati in un audiolibro M4B con segni di capitolo",
    "nl":"Geselecteerde items samenvoegen tot één M4B-luisterboek met hoofdstukmarkeringen",
    "ru":"Объединить выбранные элементы в одну аудиокнигу M4B с метками глав",
    "ja":"選択したアイテムをチャプターマーク付きのM4Bオーディオブックに結合",
    "zh-CN":"将选定项目合并为带章节标记的 M4B 有声书",
    "ko":"선택된 항목을 챕터 마크가 있는 M4B 오디오북으로 합치기",
    "pl":"Połącz zaznaczone elementy w jeden audiobook M4B ze znacznikami rozdziałów",
    "tr":"Seçili öğeleri bölüm işaretleriyle birlikte tek bir M4B sesli kitaba birleştir",
    "ar":"دمج العناصر المحددة في كتاب صوتي M4B واحد مع علامات الفصول",
    "hi":"चयनित आइटम को चैप्टर मार्क्स के साथ एक M4B ऑडियोबुक में मर्ज करें",
    "sv":"Slå samman valda objekt till en M4B-ljudbok med kapitelmarkeringar"
  },
  "SPEECH_LAB_TOOLTIP_SELECT_ALL": {
    "value":"Select all items","en":"Select all items",
    "es":"Seleccionar todos los elementos","fr":"Sélectionner tous les éléments",
    "de":"Alle Elemente auswählen","pt-BR":"Selecionar todos os itens",
    "it":"Seleziona tutti gli elementi","nl":"Alle items selecteren",
    "ru":"Выбрать все элементы","ja":"すべてのアイテムを選択",
    "zh-CN":"选择所有项目","ko":"모든 항목 선택",
    "pl":"Zaznacz wszystkie elementy","tr":"Tüm öğeleri seç",
    "ar":"تحديد جميع العناصر","hi":"सभी आइटम चुनें","sv":"Välj alla objekt"
  },
  "SPEECH_LAB_TOOLTIP_DESELECT_ALL": {
    "value":"Deselect all items","en":"Deselect all items",
    "es":"Deseleccionar todos los elementos","fr":"Désélectionner tous les éléments",
    "de":"Auswahl aller Elemente aufheben","pt-BR":"Desmarcar todos os itens",
    "it":"Deseleziona tutti gli elementi","nl":"Selectie van alle items opheffen",
    "ru":"Снять выделение со всех элементов","ja":"すべてのアイテムの選択を解除",
    "zh-CN":"取消选择所有项目","ko":"모든 항목 선택 해제",
    "pl":"Odznacz wszystkie elementy","tr":"Tüm öğelerin seçimini kaldır",
    "ar":"إلغاء تحديد جميع العناصر","hi":"सभी आइटम का चयन हटाएं","sv":"Avmarkera alla objekt"
  },
  "SPEECH_LAB_TOOLTIP_REMOVE_SEL": {
    "value":"Remove selected items from the playlist","en":"Remove selected items from the playlist",
    "es":"Eliminar los elementos seleccionados de la lista",
    "fr":"Supprimer les éléments sélectionnés de la liste de lecture",
    "de":"Ausgewählte Elemente aus der Wiedergabeliste entfernen",
    "pt-BR":"Remover itens selecionados da lista",
    "it":"Rimuovi gli elementi selezionati dalla playlist",
    "nl":"Geselecteerde items uit de afspeellijst verwijderen",
    "ru":"Удалить выбранные элементы из плейлиста",
    "ja":"選択したアイテムをプレイリストから削除",
    "zh-CN":"从播放列表中删除选定项目","ko":"재생목록에서 선택된 항목 제거",
    "pl":"Usuń zaznaczone elementy z playlisty",
    "tr":"Seçili öğeleri çalma listesinden kaldır",
    "ar":"إزالة العناصر المحددة من قائمة التشغيل",
    "hi":"प्लेलिस्ट से चयनित आइटम हटाएं","sv":"Ta bort valda objekt från spellistan"
  },

  # ── Listen Lab tooltips ──────────────────────────────────────────────────
  "LISTEN_LAB_TOOLTIP_TR_SWITCH": {
    "value":"When on: Whisper transcribes → Qwen translates → TTS re-reads in target language",
    "en":"When on: Whisper transcribes → Qwen translates → TTS re-reads in target language",
    "es":"Cuando está activado: Whisper transcribe → Qwen traduce → TTS relee en el idioma destino",
    "fr":"Activé : Whisper transcrit → Qwen traduit → TTS relit dans la langue cible",
    "de":"Eingeschaltet: Whisper transkribiert → Qwen übersetzt → TTS liest in Zielsprache vor",
    "pt-BR":"Quando ativo: Whisper transcreve → Qwen traduz → TTS relê no idioma destino",
    "it":"Attivato: Whisper trascrive → Qwen traduce → TTS rilegge nella lingua di destinazione",
    "nl":"Ingeschakeld: Whisper transcribeert → Qwen vertaalt → TTS herleest in doeltaal",
    "ru":"При включении: Whisper транскрибирует → Qwen переводит → TTS перечитывает на целевом языке",
    "ja":"オン時: Whisperが文字起こし → Qwenが翻訳 → TTSがターゲット言語で読み上げ",
    "zh-CN":"开启时：Whisper 转录 → Qwen 翻译 → TTS 用目标语言重新朗读",
    "ko":"켜졌을 때: Whisper 전사 → Qwen 번역 → TTS가 대상 언어로 다시 읽기",
    "pl":"Włączone: Whisper transkrybuje → Qwen tłumaczy → TTS odczytuje w języku docelowym",
    "tr":"Açıkken: Whisper transkribe eder → Qwen çevirir → TTS hedef dilde yeniden okur",
    "ar":"عند التشغيل: Whisper يفرّغ → Qwen يترجم → TTS يُعيد القراءة بالغة المستهدفة",
    "hi":"चालू होने पर: Whisper ट्रांसक्राइब करता है → Qwen अनुवाद करता है → TTS लक्ष्य भाषा में पुनः पढ़ता है",
    "sv":"När på: Whisper transkriberar → Qwen översätter → TTS läser om på målspråket"
  },
  "LISTEN_LAB_TOOLTIP_LANG_MENU": {
    "value":"Language to translate audio into","en":"Language to translate audio into",
    "es":"Idioma al que traducir el audio","fr":"Langue dans laquelle traduire l'audio",
    "de":"Sprache, in die Audio übersetzt werden soll",
    "pt-BR":"Idioma para o qual traduzir o áudio",
    "it":"Lingua in cui tradurre l'audio","nl":"Taal om audio in te vertalen",
    "ru":"Язык для перевода аудио","ja":"オーディオを翻訳する言語",
    "zh-CN":"将音频翻译成的语言","ko":"오디오를 번역할 언어",
    "pl":"Język, na który przetłumaczyć audio","tr":"Sesi çevirmek için dil",
    "ar":"اللغة المراد ترجمة الصوت إليها",
    "hi":"ऑडियो को जिस भाषा में अनुवाद करना है","sv":"Språk att översätta ljud till"
  },
  "LISTEN_LAB_TOOLTIP_VOICE_MENU": {
    "value":"TTS voice used for the re-read","en":"TTS voice used for the re-read",
    "es":"Voz TTS utilizada para la relectura","fr":"Voix TTS utilisée pour la relecture",
    "de":"TTS-Stimme für das Vorlesen","pt-BR":"Voz TTS usada para a releitura",
    "it":"Voce TTS usata per la rilettura","nl":"TTS-stem gebruikt voor het herlezen",
    "ru":"Голос TTS для перечитывания","ja":"再読み上げに使用するTTSの声",
    "zh-CN":"重新朗读时使用的 TTS 语音","ko":"재읽기에 사용되는 TTS 음성",
    "pl":"Głos TTS używany do ponownego odczytania",
    "tr":"Yeniden okuma için kullanılan TTS sesi",
    "ar":"صوت TTS المستخدم لإعادة القراءة",
    "hi":"री-रीड के लिए उपयोग की जाने वाली TTS आवाज़","sv":"TTS-röst som används för omläsning"
  },
  "LISTEN_LAB_TOOLTIP_PLAY_ALL": {
    "value":"Play all selected items in sequence","en":"Play all selected items in sequence",
    "es":"Reproducir todos los elementos seleccionados en secuencia",
    "fr":"Lire tous les éléments sélectionnés en séquence",
    "de":"Alle ausgewählten Elemente nacheinander abspielen",
    "pt-BR":"Reproduzir todos os itens selecionados em sequência",
    "it":"Riproduci tutti gli elementi selezionati in sequenza",
    "nl":"Alle geselecteerde items achtereenvolgens afspelen",
    "ru":"Воспроизвести все выбранные элементы по очереди",
    "ja":"選択したすべてのアイテムを順番に再生",
    "zh-CN":"按顺序播放所有选定项目","ko":"선택된 모든 항목을 순서대로 재생",
    "pl":"Odtwórz wszystkie zaznaczone elementy w kolejności",
    "tr":"Seçili tüm öğeleri sırayla oynat",
    "ar":"تشغيل جميع العناصر المحددة بالتسلسل",
    "hi":"सभी चयनित आइटम को क्रम में चलाएं","sv":"Spela upp alla valda objekt i ordning"
  },
  "LISTEN_LAB_TOOLTIP_PREV": {
    "value":"Previous track","en":"Previous track",
    "es":"Pista anterior","fr":"Piste précédente","de":"Vorheriger Titel",
    "pt-BR":"Faixa anterior","it":"Traccia precedente","nl":"Vorig nummer",
    "ru":"Предыдущий трек","ja":"前のトラック","zh-CN":"上一曲","ko":"이전 트랙",
    "pl":"Poprzedni utwór","tr":"Önceki parça","ar":"المسار السابق",
    "hi":"पिछला ट्रैक","sv":"Föregående spår"
  },
  "LISTEN_LAB_TOOLTIP_NEXT": {
    "value":"Next track","en":"Next track",
    "es":"Pista siguiente","fr":"Piste suivante","de":"Nächster Titel",
    "pt-BR":"Próxima faixa","it":"Traccia successiva","nl":"Volgend nummer",
    "ru":"Следующий трек","ja":"次のトラック","zh-CN":"下一曲","ko":"다음 트랙",
    "pl":"Następny utwór","tr":"Sonraki parça","ar":"المسار التالي",
    "hi":"अगला ट्रैक","sv":"Nästa spår"
  },
  "LISTEN_LAB_TOOLTIP_REMOVE_SEL": {
    "value":"Remove selected items from the list","en":"Remove selected items from the list",
    "es":"Eliminar los elementos seleccionados de la lista",
    "fr":"Supprimer les éléments sélectionnés de la liste",
    "de":"Ausgewählte Elemente aus der Liste entfernen",
    "pt-BR":"Remover itens selecionados da lista",
    "it":"Rimuovi gli elementi selezionati dall'elenco",
    "nl":"Geselecteerde items uit de lijst verwijderen",
    "ru":"Удалить выбранные элементы из списка",
    "ja":"選択したアイテムをリストから削除",
    "zh-CN":"从列表中删除选定项目","ko":"목록에서 선택된 항목 제거",
    "pl":"Usuń zaznaczone elementy z listy","tr":"Seçili öğeleri listeden kaldır",
    "ar":"إزالة العناصر المحددة من القائمة",
    "hi":"सूची से चयनित आइटम हटाएं","sv":"Ta bort valda objekt från listan"
  },
  "LISTEN_LAB_TOOLTIP_SELECT_ALL": {
    "value":"Select all items","en":"Select all items",
    "es":"Seleccionar todos los elementos","fr":"Sélectionner tous les éléments",
    "de":"Alle Elemente auswählen","pt-BR":"Selecionar todos os itens",
    "it":"Seleziona tutti gli elementi","nl":"Alle items selecteren",
    "ru":"Выбрать все элементы","ja":"すべてのアイテムを選択",
    "zh-CN":"选择所有项目","ko":"모든 항목 선택",
    "pl":"Zaznacz wszystkie elementy","tr":"Tüm öğeleri seç",
    "ar":"تحديد جميع العناصر","hi":"सभी आइटम चुनें","sv":"Välj alla objekt"
  },
  "LISTEN_LAB_TOOLTIP_DESELECT_ALL": {
    "value":"Deselect all items","en":"Deselect all items",
    "es":"Deseleccionar todos los elementos","fr":"Désélectionner tous les éléments",
    "de":"Auswahl aller Elemente aufheben","pt-BR":"Desmarcar todos os itens",
    "it":"Deseleziona tutti gli elementi","nl":"Selectie van alle items opheffen",
    "ru":"Снять выделение со всех элементов","ja":"すべてのアイテムの選択を解除",
    "zh-CN":"取消选择所有项目","ko":"모든 항목 선택 해제",
    "pl":"Odznacz wszystkie elementy","tr":"Tüm öğelerin seçimini kaldır",
    "ar":"إلغاء تحديد جميع العناصر","hi":"सभी आइटम का चयन हटाएं","sv":"Avmarkera alla objekt"
  },

  # ── Voice Lab recording tooltips ──────────────────────────────────────────
  "VOICE_LAB_TOOLTIP_PREVIEW_REC": {
    "value":"Preview recording","en":"Preview recording",
    "es":"Previsualizar grabación","fr":"Aperçu de l'enregistrement",
    "de":"Aufnahme vorschau","pt-BR":"Pré-visualizar gravação",
    "it":"Anteprima registrazione","nl":"Opname vooraf bekijken",
    "ru":"Предварительный просмотр записи","ja":"録音のプレビュー",
    "zh-CN":"预览录音","ko":"녹음 미리보기",
    "pl":"Podgląd nagrania","tr":"Kaydı önizle",
    "ar":"معاينة التسجيل","hi":"रिकॉर्डिंग का पूर्वावलोकन",
    "sv":"Förhandsgranska inspelning"
  },
  "VOICE_LAB_TOOLTIP_SAVE_REC": {
    "value":"Save recording to file","en":"Save recording to file",
    "es":"Guardar grabación en archivo","fr":"Enregistrer la capture dans un fichier",
    "de":"Aufnahme in Datei speichern","pt-BR":"Salvar gravação em arquivo",
    "it":"Salva registrazione su file","nl":"Opname opslaan naar bestand",
    "ru":"Сохранить запись в файл","ja":"録音をファイルに保存",
    "zh-CN":"将录音保存到文件","ko":"녹음을 파일로 저장",
    "pl":"Zapisz nagranie do pliku","tr":"Kaydı dosyaya kaydet",
    "ar":"حفظ التسجيل في ملف","hi":"रिकॉर्डिंग को फ़ाइल में सेव करें",
    "sv":"Spara inspelning till fil"
  },

  # ── Prompt Lab context tooltip ──────────────────────────────────────────
  "PROMPT_LAB_TOOLTIP_CTX": {
    "value":"How many conversation turns to include with each message.\n0 = send full history.  Small models (0.5B) overflow above ~8 turns.\nLarger models (1.5B+) handle 15-25 turns comfortably.",
    "en":"How many conversation turns to include with each message.\n0 = send full history.  Small models (0.5B) overflow above ~8 turns.\nLarger models (1.5B+) handle 15-25 turns comfortably.",
    "es":"Cuántos turnos de conversación incluir con cada mensaje.\n0 = enviar historial completo. Los modelos pequeños (0.5B) se desbordan por encima de ~8 turnos.\nLos modelos más grandes (1.5B+) manejan 15-25 turnos cómodamente.",
    "fr":"Combien de tours de conversation inclure avec chaque message.\n0 = envoyer l'historique complet. Les petits modèles (0.5B) débordent au-delà de ~8 tours.\nLes grands modèles (1.5B+) gèrent confortablement 15-25 tours.",
    "de":"Wie viele Gesprächsrunden mit jeder Nachricht gesendet werden.\n0 = gesamten Verlauf senden. Kleine Modelle (0,5B) laufen bei ~8 Runden über.\nGrößere Modelle (1,5B+) verarbeiten 15-25 Runden problemlos.",
    "pt-BR":"Quantos turnos de conversa incluir com cada mensagem.\n0 = enviar histórico completo. Modelos pequenos (0,5B) transbordam acima de ~8 turnos.\nModelos maiores (1,5B+) lidam com 15-25 turnos confortavelmente.",
    "it":"Quanti turni di conversazione includere con ogni messaggio.\n0 = invia la cronologia completa. I modelli piccoli (0.5B) vanno in overflow oltre ~8 turni.\nI modelli più grandi (1.5B+) gestiscono comodamente 15-25 turni.",
    "nl":"Hoeveel gespreksronden bij elk bericht worden meegestuurd.\n0 = volledige geschiedenis sturen. Kleine modellen (0.5B) raken boven ~8 ronden vol.\nGrotere modellen (1.5B+) verwerken comfortabel 15-25 ronden.",
    "ru":"Сколько ходов разговора включать в каждое сообщение.\n0 = отправить полную историю. Малые модели (0.5B) переполняются при ~8 ходах.\nБольшие модели (1.5B+) легко обрабатывают 15-25 ходов.",
    "ja":"各メッセージに含める会話ターンの数。\n0 = 全履歴を送信。小さいモデル（0.5B）は~8ターン以上でオーバーフローします。\n大きいモデル（1.5B+）は15-25ターンを余裕で処理します。",
    "zh-CN":"每条消息包含多少个对话轮次。\n0 = 发送完整历史。小模型 (0.5B) 超过 ~8 轮会溢出。\n较大模型 (1.5B+) 可轻松处理 15-25 轮。",
    "ko":"각 메시지에 포함할 대화 턴 수.\n0 = 전체 기록 전송. 소형 모델(0.5B)은 ~8턴 이상에서 오버플로우됩니다.\n대형 모델(1.5B+)은 15-25턴을 편안하게 처리합니다.",
    "pl":"Ile tur rozmowy dołączyć do każdej wiadomości.\n0 = wyślij pełną historię. Małe modele (0.5B) przepełniają się powyżej ~8 tur.\nWiększe modele (1.5B+) wygodnie obsługują 15-25 tur.",
    "tr":"Her mesajla kaç konuşma turu dahil edilecek.\n0 = tam geçmişi gönder. Küçük modeller (0.5B) ~8 turun üzerinde taşar.\nDaha büyük modeller (1.5B+) 15-25 turu rahatça işler.",
    "ar":"عدد أدوار المحادثة المراد تضمينها مع كل رسالة.\n0 = إرسال السجل الكامل. النماذج الصغيرة (0.5B) تفيض فوق ~8 أدوار.\nالنماذج الأكبر (1.5B+) تتعامل براحة مع 15-25 دورًا.",
    "hi":"प्रत्येक संदेश के साथ कितने बातचीत के दौर शामिल करने हैं।\n0 = पूरा इतिहास भेजें। छोटे मॉडल (0.5B) ~8 दौर के ऊपर ओवरफ्लो हो जाते हैं।\nबड़े मॉडल (1.5B+) 15-25 दौर आराम से संभालते हैं।",
    "sv":"Hur många konversationsturer som ska inkluderas med varje meddelande.\n0 = skicka fullständig historik. Små modeller (0.5B) svämmar över vid ~8 turer.\nStörre modeller (1.5B+) hanterar bekvämt 15-25 turer."
  },

  # ── Content style dropdown options ──────────────────────────────────────
  "SPEECH_LAB_CONTENT_STYLE_NONE": {
    "value":"None","en":"None","es":"Ninguno","fr":"Aucun","de":"Keine",
    "pt-BR":"Nenhum","it":"Nessuno","nl":"Geen","ru":"Нет","ja":"なし",
    "zh-CN":"无","ko":"없음","pl":"Brak","tr":"Hiçbiri","ar":"لا شيء",
    "hi":"कोई नहीं","sv":"Ingen"
  },
  "SPEECH_LAB_CONTENT_STYLE_FORMAL": {
    "value":"Formal","en":"Formal","es":"Formal","fr":"Formel","de":"Formal",
    "pt-BR":"Formal","it":"Formale","nl":"Formeel","ru":"Официальный",
    "ja":"フォーマル","zh-CN":"正式","ko":"격식체","pl":"Formalny",
    "tr":"Resmi","ar":"رسمي","hi":"औपचारिक","sv":"Formell"
  },
  "SPEECH_LAB_CONTENT_STYLE_CASUAL": {
    "value":"Casual","en":"Casual","es":"Informal","fr":"Décontracté","de":"Locker",
    "pt-BR":"Casual","it":"Informale","nl":"Informeel","ru":"Неформальный",
    "ja":"カジュアル","zh-CN":"随意","ko":"일상적","pl":"Swobodny",
    "tr":"Günlük","ar":"عادي","hi":"सामान्य","sv":"Avslappnad"
  },
  "SPEECH_LAB_CONTENT_STYLE_SCIENTIFIC": {
    "value":"Scientific","en":"Scientific","es":"Científico","fr":"Scientifique",
    "de":"Wissenschaftlich","pt-BR":"Científico","it":"Scientifico",
    "nl":"Wetenschappelijk","ru":"Научный","ja":"科学的","zh-CN":"科学性",
    "ko":"과학적","pl":"Naukowy","tr":"Bilimsel","ar":"علمي",
    "hi":"वैज्ञानिक","sv":"Vetenskaplig"
  },
  "SPEECH_LAB_CONTENT_STYLE_PROFESSIONAL": {
    "value":"Professional","en":"Professional","es":"Profesional","fr":"Professionnel",
    "de":"Professionell","pt-BR":"Profissional","it":"Professionale",
    "nl":"Professioneel","ru":"Профессиональный","ja":"プロフェッショナル",
    "zh-CN":"专业","ko":"전문적","pl":"Profesjonalny","tr":"Profesyonel",
    "ar":"مهني","hi":"व्यावसायिक","sv":"Professionell"
  },
  "SPEECH_LAB_CONTENT_STYLE_STORY_FICTION": {
    "value":"Story — Fiction","en":"Story — Fiction",
    "es":"Historia — Ficción","fr":"Récit — Fiction","de":"Geschichte — Fiktion",
    "pt-BR":"História — Ficção","it":"Storia — Narrativa","nl":"Verhaal — Fictie",
    "ru":"История — Художественная","ja":"ストーリー — フィクション",
    "zh-CN":"故事 — 虚构","ko":"이야기 — 픽션","pl":"Historia — Fikcja",
    "tr":"Hikaye — Kurgu","ar":"قصة — خيال","hi":"कहानी — काल्पनिक",
    "sv":"Berättelse — Fiktion"
  },
  "SPEECH_LAB_CONTENT_STYLE_STORY_NONFICTION": {
    "value":"Story — Non-Fiction","en":"Story — Non-Fiction",
    "es":"Historia — No ficción","fr":"Récit — Non-fiction","de":"Geschichte — Sachbuch",
    "pt-BR":"História — Não-ficção","it":"Storia — Non narrativa",
    "nl":"Verhaal — Non-fictie","ru":"История — Документальная",
    "ja":"ストーリー — ノンフィクション","zh-CN":"故事 — 非虚构",
    "ko":"이야기 — 논픽션","pl":"Historia — Non-fiction",
    "tr":"Hikaye — Kurgu Dışı","ar":"قصة — غير خيالي",
    "hi":"कहानी — गैर-काल्पनिक","sv":"Berättelse — Fakta"
  },
  "SPEECH_LAB_CONTENT_STYLE_PODCAST": {
    "value":"Podcast","en":"Podcast","es":"Podcast","fr":"Podcast","de":"Podcast",
    "pt-BR":"Podcast","it":"Podcast","nl":"Podcast","ru":"Подкаст",
    "ja":"ポッドキャスト","zh-CN":"播客","ko":"팟캐스트","pl":"Podcast",
    "tr":"Podcast","ar":"بودكاست","hi":"Podcast","sv":"Podcast"
  },
}

added = 0
for key, val in NEW_KEYS.items():
    if key not in data["strings"]:
        data["strings"][key] = val
        added += 1
    else:
        print(f"  skipped (already exists): {key}")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done. Added {added} keys. Total: {len(data['strings'])}")
