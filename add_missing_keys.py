"""Add all missing UI string keys with full 16-language translations."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

NEW_KEYS = {
  # ── Speech Lab ────────────────────────────────────────────────────────
  "SPEECH_LAB_HEADER_PLAYLIST": {
    "value":"📋  Playlist","dynamic":False,
    "en":"📋  Playlist","es":"📋  Lista de reproducción","fr":"📋  Liste de lecture","de":"📋  Wiedergabeliste","pt-BR":"📋  Lista de reprodução","it":"📋  Playlist","nl":"📋  Afspeellijst","ru":"📋  Плейлист","ja":"📋  プレイリスト","zh-CN":"📋  播放列表","ko":"📋  재생목록","pl":"📋  Playlista","tr":"📋  Çalma listesi","ar":"📋  قائمة التشغيل","hi":"📋  प्लेलिस्ट","sv":"📋  Spellista",
  },
  "SPEECH_LAB_HINT_DBLCLICK": {
    "value":"(Double-Click File Name to open in Editor.)","dynamic":False,
    "en":"(Double-Click File Name to open in Editor.)","es":"(Haz doble clic en el nombre para abrir en el Editor.)","fr":"(Double-cliquez sur le nom du fichier pour l'ouvrir dans l'Éditeur.)","de":"(Doppelklick auf den Dateinamen, um ihn im Editor zu öffnen.)","pt-BR":"(Duplo clique no nome do arquivo para abrir no Editor.)","it":"(Doppio clic sul nome del file per aprirlo nell'Editor.)","nl":"(Dubbelklik op de bestandsnaam om in de Editor te openen.)","ru":"(Дважды щёлкните по имени файла, чтобы открыть в Редакторе.)","ja":"(ファイル名をダブルクリックするとエディターで開きます。)","zh-CN":"(双击文件名在编辑器中打开。)","ko":"(파일 이름을 더블클릭하면 편집기에서 열립니다.)","pl":"(Kliknij dwukrotnie nazwę pliku, aby otworzyć w Edytorze.)","tr":"(Düzenleyicide açmak için dosya adına çift tıklayın.)","ar":"(انقر نقراً مزدوجاً على اسم الملف لفتحه في المحرر.)","hi":"(एडिटर में खोलने के लिए फ़ाइल नाम पर डबल-क्लिक करें।)","sv":"(Dubbelklicka på filnamnet för att öppna i Redigeraren.)",
  },
  "SPEECH_LAB_LANG_FILTER_LABEL": {
    "value":"Language:","dynamic":False,
    "en":"Language:","es":"Idioma:","fr":"Langue :","de":"Sprache:","pt-BR":"Idioma:","it":"Lingua:","nl":"Taal:","ru":"Язык:","ja":"言語:","zh-CN":"语言:","ko":"언어:","pl":"Język:","tr":"Dil:","ar":"اللغة:","hi":"भाषा:","sv":"Språk:",
  },
  "SPEECH_LAB_BTN_CONVERT_SELECTED": {
    "value":"🔊 Convert Selected","dynamic":False,
    "en":"🔊 Convert Selected","es":"🔊 Convertir selección","fr":"🔊 Convertir la sélection","de":"🔊 Auswahl konvertieren","pt-BR":"🔊 Converter seleção","it":"🔊 Converti selezione","nl":"🔊 Selectie converteren","ru":"🔊 Конвертировать выбранное","ja":"🔊 選択を変換","zh-CN":"🔊 转换选中项","ko":"🔊 선택 항목 변환","pl":"🔊 Konwertuj zaznaczone","tr":"🔊 Seçileni dönüştür","ar":"🔊 تحويل المحدد","hi":"🔊 चयनित को बदलें","sv":"🔊 Konvertera markerade",
  },
  "SPEECH_LAB_BTN_PLAY_SELECTED": {
    "value":"▶ Play Selected","dynamic":False,
    "en":"▶ Play Selected","es":"▶ Reproducir selección","fr":"▶ Lire la sélection","de":"▶ Auswahl abspielen","pt-BR":"▶ Reproduzir seleção","it":"▶ Riproduci selezione","nl":"▶ Selectie afspelen","ru":"▶ Воспроизвести выбранное","ja":"▶ 選択を再生","zh-CN":"▶ 播放选中项","ko":"▶ 선택 항목 재생","pl":"▶ Odtwórz zaznaczone","tr":"▶ Seçileni oynat","ar":"▶ تشغيل المحدد","hi":"▶ चयनित चलाएं","sv":"▶ Spela markerade",
  },
  "SPEECH_LAB_BTN_SAVE_SELECTED": {
    "value":"💾 Save Selected","dynamic":False,
    "en":"💾 Save Selected","es":"💾 Guardar selección","fr":"💾 Enregistrer la sélection","de":"💾 Auswahl speichern","pt-BR":"💾 Salvar seleção","it":"💾 Salva selezione","nl":"💾 Selectie opslaan","ru":"💾 Сохранить выбранное","ja":"💾 選択を保存","zh-CN":"💾 保存选中项","ko":"💾 선택 항목 저장","pl":"💾 Zapisz zaznaczone","tr":"💾 Seçileni kaydet","ar":"💾 حفظ المحدد","hi":"💾 चयनित सहेजें","sv":"💾 Spara markerade",
  },
  "SPEECH_LAB_BTN_AUDIOBOOK": {
    "value":"📚 Audiobook","dynamic":False,
    "en":"📚 Audiobook","es":"📚 Audiolibro","fr":"📚 Livre audio","de":"📚 Hörbuch","pt-BR":"📚 Audiobook","it":"📚 Audiolibro","nl":"📚 Luisterboek","ru":"📚 Аудиокнига","ja":"📚 オーディオブック","zh-CN":"📚 有声书","ko":"📚 오디오북","pl":"📚 Audiobook","tr":"📚 Sesli kitap","ar":"📚 كتاب صوتي","hi":"📚 ऑडियोबुक","sv":"📚 Ljudbok",
  },
  "SPEECH_LAB_BTN_SELECT_ALL": {
    "value":"☑ All","dynamic":False,
    "en":"☑ All","es":"☑ Todo","fr":"☑ Tout","de":"☑ Alle","pt-BR":"☑ Todos","it":"☑ Tutti","nl":"☑ Alles","ru":"☑ Все","ja":"☑ 全て","zh-CN":"☑ 全部","ko":"☑ 전체","pl":"☑ Wszystko","tr":"☑ Tümü","ar":"☑ الكل","hi":"☑ सभी","sv":"☑ Alla",
  },
  "SPEECH_LAB_BTN_SELECT_NONE": {
    "value":"☐ None","dynamic":False,
    "en":"☐ None","es":"☐ Ninguno","fr":"☐ Aucun","de":"☐ Keine","pt-BR":"☐ Nenhum","it":"☐ Nessuno","nl":"☐ Geen","ru":"☐ Снять","ja":"☐ なし","zh-CN":"☐ 无","ko":"☐ 없음","pl":"☐ Żadne","tr":"☐ Hiçbiri","ar":"☐ لا شيء","hi":"☐ कोई नहीं","sv":"☐ Inget",
  },
  "SPEECH_LAB_BTN_CLEAR_SELECTED": {
    "value":"🗑 Clear Selected","dynamic":False,
    "en":"🗑 Clear Selected","es":"🗑 Limpiar selección","fr":"🗑 Effacer la sélection","de":"🗑 Auswahl löschen","pt-BR":"🗑 Limpar seleção","it":"🗑 Cancella selezione","nl":"🗑 Selectie wissen","ru":"🗑 Очистить выбранное","ja":"🗑 選択を削除","zh-CN":"🗑 清除选中项","ko":"🗑 선택 항목 지우기","pl":"🗑 Wyczyść zaznaczone","tr":"🗑 Seçileni temizle","ar":"🗑 مسح المحدد","hi":"🗑 चयनित हटाएं","sv":"🗑 Rensa markerade",
  },

  # ── Text Lab ────────────────────────────────────────────────────────
  "TEXT_LAB_TRANSLATE_TO_LABEL": {
    "value":"Translate to","dynamic":False,
    "en":"Translate to","es":"Traducir a","fr":"Traduire en","de":"Übersetzen nach","pt-BR":"Traduzir para","it":"Traduci in","nl":"Vertalen naar","ru":"Перевести на","ja":"翻訳先:","zh-CN":"翻译至","ko":"다음으로 번역","pl":"Przetłumacz na","tr":"Şuna çevir:","ar":"ترجمة إلى","hi":"इसमें अनुवाद करें","sv":"Översätt till",
  },
  "TEXT_LAB_FROM_LABEL": {
    "value":"From:","dynamic":False,
    "en":"From:","es":"De:","fr":"De :","de":"Von:","pt-BR":"De:","it":"Da:","nl":"Van:","ru":"Из:","ja":"元:","zh-CN":"从:","ko":"에서:","pl":"Z:","tr":"Kaynak:","ar":"من:","hi":"से:","sv":"Från:",
  },
  "TEXT_LAB_TO_LABEL": {
    "value":"To:","dynamic":False,
    "en":"To:","es":"A:","fr":"Vers :","de":"Nach:","pt-BR":"Para:","it":"A:","nl":"Naar:","ru":"В:","ja":"先:","zh-CN":"到:","ko":"까지:","pl":"Do:","tr":"Hedef:","ar":"إلى:","hi":"तक:","sv":"Till:",
  },
  "TEXT_LAB_BTN_CONVERT_FMT": {
    "value":"Convert","dynamic":False,
    "en":"Convert","es":"Convertir","fr":"Convertir","de":"Konvertieren","pt-BR":"Converter","it":"Converti","nl":"Converteren","ru":"Конвертировать","ja":"変換","zh-CN":"转换","ko":"변환","pl":"Konwertuj","tr":"Dönüştür","ar":"تحويل","hi":"बदलें","sv":"Konvertera",
  },

  # ── File Lab ────────────────────────────────────────────────────────
  "FILE_LAB_AUDIO_DROP_HINT": {
    "value":"🎵  Drop an MP3, WAV, M4B, FLAC or MP4 here — or click to browse","dynamic":False,
    "en":"🎵  Drop an MP3, WAV, M4B, FLAC or MP4 here — or click to browse","es":"🎵  Suelta un MP3, WAV, M4B, FLAC o MP4 aquí — o haz clic para buscar","fr":"🎵  Déposez un MP3, WAV, M4B, FLAC ou MP4 ici — ou cliquez pour parcourir","de":"🎵  MP3, WAV, M4B, FLAC oder MP4 hier ablegen — oder zum Suchen klicken","pt-BR":"🎵  Solte um MP3, WAV, M4B, FLAC ou MP4 aqui — ou clique para procurar","it":"🎵  Trascina un MP3, WAV, M4B, FLAC o MP4 qui — o clicca per cercare","nl":"🎵  Zet een MP3, WAV, M4B, FLAC of MP4 hier neer — of klik om te bladeren","ru":"🎵  Перетащите MP3, WAV, M4B, FLAC или MP4 сюда — или нажмите для выбора","ja":"🎵  MP3, WAV, M4B, FLAC または MP4 をここにドロップ — またはクリックして参照","zh-CN":"🎵  将 MP3、WAV、M4B、FLAC 或 MP4 拖放至此 — 或点击浏览","ko":"🎵  MP3, WAV, M4B, FLAC 또는 MP4를 여기에 놓거나 클릭하여 찾아보기","pl":"🎵  Upuść plik MP3, WAV, M4B, FLAC lub MP4 tutaj — lub kliknij, aby przeglądać","tr":"🎵  Buraya bir MP3, WAV, M4B, FLAC veya MP4 bırakın — ya da gözatmak için tıklayın","ar":"🎵  أفلت ملف MP3 أو WAV أو M4B أو FLAC أو MP4 هنا — أو انقر للتصفح","hi":"🎵  यहाँ MP3, WAV, M4B, FLAC या MP4 ड्रॉप करें — या ब्राउज़ करने के लिए क्लिक करें","sv":"🎵  Släpp en MP3, WAV, M4B, FLAC eller MP4 här — eller klicka för att bläddra",
  },
  "FILE_LAB_CONVERT_TO_LABEL": {
    "value":"Convert to:","dynamic":False,
    "en":"Convert to:","es":"Convertir a:","fr":"Convertir en :","de":"Konvertieren nach:","pt-BR":"Converter para:","it":"Converti in:","nl":"Converteren naar:","ru":"Конвертировать в:","ja":"変換先:","zh-CN":"转换为:","ko":"다음으로 변환:","pl":"Konwertuj do:","tr":"Şuna dönüştür:","ar":"تحويل إلى:","hi":"इसमें बदलें:","sv":"Konvertera till:",
  },
  "FILE_LAB_BTN_CONVERT_AUDIO": {
    "value":"Convert","dynamic":False,
    "en":"Convert","es":"Convertir","fr":"Convertir","de":"Konvertieren","pt-BR":"Converter","it":"Converti","nl":"Converteren","ru":"Конвертировать","ja":"変換","zh-CN":"转换","ko":"변환","pl":"Konwertuj","tr":"Dönüştür","ar":"تحويل","hi":"बदलें","sv":"Konvertera",
  },
  "FILE_LAB_STATUS_CONVERTING_AUDIO": {
    "value":"Converting…","dynamic":False,
    "en":"Converting…","es":"Convirtiendo…","fr":"Conversion en cours…","de":"Konvertierung läuft…","pt-BR":"Convertendo…","it":"Conversione in corso…","nl":"Converteren…","ru":"Конвертация…","ja":"変換中…","zh-CN":"正在转换…","ko":"변환 중…","pl":"Konwertowanie…","tr":"Dönüştürülüyor…","ar":"جارٍ التحويل…","hi":"बदला जा रहा है…","sv":"Konverterar…",
  },
  "FILE_LAB_COMBINER_HINT": {
    "value":"Drop or add audio files, drag to reorder, then export as M4B/MP4/WAV/MP3.","dynamic":False,
    "en":"Drop or add audio files, drag to reorder, then export as M4B/MP4/WAV/MP3.","es":"Suelta o añade archivos de audio, arrastra para reordenar y exporta como M4B/MP4/WAV/MP3.","fr":"Déposez ou ajoutez des fichiers audio, faites glisser pour réorganiser, puis exportez en M4B/MP4/WAV/MP3.","de":"Audiodateien ablegen oder hinzufügen, zum Neuanordnen ziehen, dann als M4B/MP4/WAV/MP3 exportieren.","pt-BR":"Solte ou adicione arquivos de áudio, arraste para reordenar e exporte como M4B/MP4/WAV/MP3.","it":"Trascina o aggiungi file audio, trascina per riordinare, poi esporta come M4B/MP4/WAV/MP3.","nl":"Zet audiobestanden neer of voeg ze toe, versleep om te herordenen en exporteer als M4B/MP4/WAV/MP3.","ru":"Перетащите или добавьте аудиофайлы, перетащите для изменения порядка, затем экспортируйте в M4B/MP4/WAV/MP3.","ja":"オーディオファイルをドロップまたは追加し、ドラッグして並び替え、M4B/MP4/WAV/MP3 として出力。","zh-CN":"拖放或添加音频文件，拖动重新排序，然后导出为 M4B/MP4/WAV/MP3。","ko":"오디오 파일을 놓거나 추가하고, 드래그하여 순서를 변경한 후 M4B/MP4/WAV/MP3로 내보내기.","pl":"Upuść lub dodaj pliki audio, przeciągnij, aby zmienić kolejność, a następnie wyeksportuj jako M4B/MP4/WAV/MP3.","tr":"Ses dosyalarını bırakın veya ekleyin, yeniden sıralamak için sürükleyin ve M4B/MP4/WAV/MP3 olarak dışa aktarın.","ar":"أفلت أو أضف ملفات صوتية، واسحب لإعادة الترتيب، ثم صدّرها بصيغة M4B/MP4/WAV/MP3.","hi":"ऑडियो फ़ाइलें ड्रॉप करें या जोड़ें, क्रम बदलने के लिए खींचें, फिर M4B/MP4/WAV/MP3 के रूप में निर्यात करें।","sv":"Släpp eller lägg till ljudfiler, dra för att ordna om och exportera sedan som M4B/MP4/WAV/MP3.",
  },
  "FILE_LAB_COMBINER_EMPTY": {
    "value":"No files added yet.","dynamic":False,
    "en":"No files added yet.","es":"No se han añadido archivos.","fr":"Aucun fichier ajouté.","de":"Noch keine Dateien hinzugefügt.","pt-BR":"Nenhum arquivo adicionado ainda.","it":"Nessun file aggiunto.","nl":"Nog geen bestanden toegevoegd.","ru":"Файлы ещё не добавлены.","ja":"ファイルが追加されていません。","zh-CN":"尚未添加文件。","ko":"추가된 파일이 없습니다.","pl":"Nie dodano jeszcze plików.","tr":"Henüz dosya eklenmedi.","ar":"لم تتم إضافة ملفات بعد.","hi":"अभी कोई फ़ाइल नहीं जोड़ी गई।","sv":"Inga filer tillagda ännu.",
  },
  "FILE_LAB_COMBINER_EMPTY_BTN": {
    "value":"No files — click Add Files below","dynamic":False,
    "en":"No files — click Add Files below","es":"Sin archivos — haz clic en Agregar archivos","fr":"Aucun fichier — cliquez sur Ajouter des fichiers","de":"Keine Dateien — unten auf Dateien hinzufügen klicken","pt-BR":"Sem arquivos — clique em Adicionar Arquivos","it":"Nessun file — fai clic su Aggiungi file","nl":"Geen bestanden — klik hieronder op Bestanden toevoegen","ru":"Нет файлов — нажмите «Добавить файлы»","ja":"ファイルなし — 下の「ファイルを追加」をクリック","zh-CN":"无文件 — 点击下方"添加文件"","ko":"파일 없음 — 아래 파일 추가 클릭","pl":"Brak plików — kliknij Dodaj pliki poniżej","tr":"Dosya yok — aşağıda Dosya Ekle'ye tıklayın","ar":"لا توجد ملفات — انقر على \"إضافة ملفات\" أدناه","hi":"कोई फ़ाइल नहीं — नीचे \"फ़ाइलें जोड़ें\" पर क्लिक करें","sv":"Inga filer — klicka på Lägg till filer nedan",
  },
  "FILE_LAB_STATUS_COMBINING": {
    "value":"Combining…","dynamic":False,
    "en":"Combining…","es":"Combinando…","fr":"Combinaison en cours…","de":"Zusammenführen…","pt-BR":"Combinando…","it":"Combinazione in corso…","nl":"Samenvoegen…","ru":"Объединение…","ja":"結合中…","zh-CN":"正在合并…","ko":"결합 중…","pl":"Łączenie…","tr":"Birleştiriliyor…","ar":"جارٍ الدمج…","hi":"जोड़ा जा रहा है…","sv":"Kombinerar…",
  },
  "FILE_LAB_STATUS_ENCODING": {
    "value":"Encoding final file…","dynamic":False,
    "en":"Encoding final file…","es":"Codificando archivo final…","fr":"Encodage du fichier final…","de":"Finale Datei wird kodiert…","pt-BR":"Codificando arquivo final…","it":"Codifica del file finale…","nl":"Definitief bestand coderen…","ru":"Кодирование финального файла…","ja":"最終ファイルをエンコード中…","zh-CN":"正在编码最终文件…","ko":"최종 파일 인코딩 중…","pl":"Kodowanie ostatecznego pliku…","tr":"Son dosya kodlanıyor…","ar":"جارٍ ترميز الملف النهائي…","hi":"अंतिम फ़ाइल एन्कोड हो रही है…","sv":"Kodar slutlig fil…",
  },
  "FILE_LAB_BTN_ADD_FILES": {
    "value":"➕ Add Files","dynamic":False,
    "en":"➕ Add Files","es":"➕ Agregar archivos","fr":"➕ Ajouter des fichiers","de":"➕ Dateien hinzufügen","pt-BR":"➕ Adicionar arquivos","it":"➕ Aggiungi file","nl":"➕ Bestanden toevoegen","ru":"➕ Добавить файлы","ja":"➕ ファイルを追加","zh-CN":"➕ 添加文件","ko":"➕ 파일 추가","pl":"➕ Dodaj pliki","tr":"➕ Dosya Ekle","ar":"➕ إضافة ملفات","hi":"➕ फ़ाइलें जोड़ें","sv":"➕ Lägg till filer",
  },
  "FILE_LAB_BTN_CLEAR_ALL": {
    "value":"🗑 Clear","dynamic":False,
    "en":"🗑 Clear","es":"🗑 Limpiar","fr":"🗑 Effacer","de":"🗑 Leeren","pt-BR":"🗑 Limpar","it":"🗑 Cancella","nl":"🗑 Wissen","ru":"🗑 Очистить","ja":"🗑 クリア","zh-CN":"🗑 清空","ko":"🗑 지우기","pl":"🗑 Wyczyść","tr":"🗑 Temizle","ar":"🗑 مسح","hi":"🗑 साफ़ करें","sv":"🗑 Rensa",
  },
  "FILE_LAB_BTN_EXPORT_AUDIOBOOK": {
    "value":"📚 Export Audiobook","dynamic":False,
    "en":"📚 Export Audiobook","es":"📚 Exportar audiolibro","fr":"📚 Exporter le livre audio","de":"📚 Hörbuch exportieren","pt-BR":"📚 Exportar audiobook","it":"📚 Esporta audiolibro","nl":"📚 Luisterboek exporteren","ru":"📚 Экспортировать аудиокнигу","ja":"📚 オーディオブックを出力","zh-CN":"📚 导出有声书","ko":"📚 오디오북 내보내기","pl":"📚 Eksportuj audiobook","tr":"📚 Sesli kitap dışa aktar","ar":"📚 تصدير كتاب صوتي","hi":"📚 ऑडियोबुक निर्यात करें","sv":"📚 Exportera ljudbok",
  },

  # ── Listen Lab ──────────────────────────────────────────────────────
  "LISTEN_LAB_HEADER": {
    "value":"🎧  Listen Lab","dynamic":False,
    "en":"🎧  Listen Lab","es":"🎧  Laboratorio de escucha","fr":"🎧  Labo d'écoute","de":"🎧  Hörlabor","pt-BR":"🎧  Lab de escuta","it":"🎧  Lab di ascolto","nl":"🎧  Luisterlaboratorium","ru":"🎧  Лаборатория прослушивания","ja":"🎧  リッスン・ラボ","zh-CN":"🎧  收听工坊","ko":"🎧  청취 랩","pl":"🎧  Laboratorium odsłuchu","tr":"🎧  Dinleme Laboratuvarı","ar":"🎧  مختبر الاستماع","hi":"🎧  लिसन लैब","sv":"🎧  Lyssningslabb",
  },
  "LISTEN_LAB_BTN_TRANSLATE_REREAD": {
    "value":"Translate & Re-read","dynamic":False,
    "en":"Translate & Re-read","es":"Traducir y releer","fr":"Traduire et relire","de":"Übersetzen & neu vorlesen","pt-BR":"Traduzir e reler","it":"Traduci e rileggi","nl":"Vertalen en herlezen","ru":"Перевести и перечитать","ja":"翻訳して読み上げ","zh-CN":"翻译并重新朗读","ko":"번역 및 다시 읽기","pl":"Przetłumacz i przeczytaj ponownie","tr":"Çevir ve Yeniden Oku","ar":"ترجمة وإعادة القراءة","hi":"अनुवाद करें और दोबारा पढ़ें","sv":"Översätt och läs om",
  },
  "LISTEN_LAB_TARGET_LANG_LABEL": {
    "value":"Target Language","dynamic":False,
    "en":"Target Language","es":"Idioma destino","fr":"Langue cible","de":"Zielsprache","pt-BR":"Idioma de destino","it":"Lingua di destinazione","nl":"Doeltaal","ru":"Целевой язык","ja":"対象言語","zh-CN":"目标语言","ko":"대상 언어","pl":"Język docelowy","tr":"Hedef dil","ar":"اللغة المستهدفة","hi":"लक्षित भाषा","sv":"Målspråk",
  },
  "LISTEN_LAB_TTS_VOICE_LABEL": {
    "value":"TTS Voice","dynamic":False,
    "en":"TTS Voice","es":"Voz TTS","fr":"Voix TTS","de":"TTS-Stimme","pt-BR":"Voz TTS","it":"Voce TTS","nl":"TTS-stem","ru":"Голос TTS","ja":"TTS音声","zh-CN":"TTS 语音","ko":"TTS 음성","pl":"Głos TTS","tr":"TTS sesi","ar":"صوت TTS","hi":"TTS आवाज़","sv":"TTS-röst",
  },
  "LISTEN_LAB_BTN_ADD_FILES": {
    "value":"＋  Add Files","dynamic":False,
    "en":"＋  Add Files","es":"＋  Agregar archivos","fr":"＋  Ajouter des fichiers","de":"＋  Dateien hinzufügen","pt-BR":"＋  Adicionar arquivos","it":"＋  Aggiungi file","nl":"＋  Bestanden toevoegen","ru":"＋  Добавить файлы","ja":"＋  ファイルを追加","zh-CN":"＋  添加文件","ko":"＋  파일 추가","pl":"＋  Dodaj pliki","tr":"＋  Dosya Ekle","ar":"＋  إضافة ملفات","hi":"＋  फ़ाइलें जोड़ें","sv":"＋  Lägg till filer",
  },
  "LISTEN_LAB_DROP_HINT": {
    "value":"Drag & drop audio files here  (MP3, WAV, M4A, M4B, FLAC, OGG…)","dynamic":False,
    "en":"Drag & drop audio files here  (MP3, WAV, M4A, M4B, FLAC, OGG…)","es":"Arrastra y suelta archivos de audio aquí  (MP3, WAV, M4A, M4B, FLAC, OGG…)","fr":"Glissez-déposez des fichiers audio ici  (MP3, WAV, M4A, M4B, FLAC, OGG…)","de":"Audiodateien hier ablegen  (MP3, WAV, M4A, M4B, FLAC, OGG…)","pt-BR":"Arraste e solte arquivos de áudio aqui  (MP3, WAV, M4A, M4B, FLAC, OGG…)","it":"Trascina e rilascia i file audio qui  (MP3, WAV, M4A, M4B, FLAC, OGG…)","nl":"Sleep audiobestanden hier naartoe  (MP3, WAV, M4A, M4B, FLAC, OGG…)","ru":"Перетащите аудиофайлы сюда  (MP3, WAV, M4A, M4B, FLAC, OGG…)","ja":"オーディオファイルをここにドラッグ＆ドロップ  (MP3, WAV, M4A, M4B, FLAC, OGG…)","zh-CN":"将音频文件拖放至此  (MP3、WAV、M4A、M4B、FLAC、OGG…)","ko":"오디오 파일을 여기에 드래그 앤 드롭  (MP3, WAV, M4A, M4B, FLAC, OGG…)","pl":"Przeciągnij i upuść pliki audio tutaj  (MP3, WAV, M4A, M4B, FLAC, OGG…)","tr":"Ses dosyalarını buraya sürükleyip bırakın  (MP3, WAV, M4A, M4B, FLAC, OGG…)","ar":"اسحب وأفلت ملفات الصوت هنا  (MP3, WAV, M4A, M4B, FLAC, OGG…)","hi":"यहाँ ऑडियो फ़ाइलें खींचें और छोड़ें  (MP3, WAV, M4A, M4B, FLAC, OGG…)","sv":"Dra och släpp ljudfiler här  (MP3, WAV, M4A, M4B, FLAC, OGG…)",
  },
  "LISTEN_LAB_BTN_PLAY_SELECTED": {
    "value":"▶  Play Selected","dynamic":False,
    "en":"▶  Play Selected","es":"▶  Reproducir selección","fr":"▶  Lire la sélection","de":"▶  Auswahl abspielen","pt-BR":"▶  Reproduzir seleção","it":"▶  Riproduci selezione","nl":"▶  Selectie afspelen","ru":"▶  Воспроизвести выбранное","ja":"▶  選択を再生","zh-CN":"▶  播放选中项","ko":"▶  선택 재생","pl":"▶  Odtwórz zaznaczone","tr":"▶  Seçileni oynat","ar":"▶  تشغيل المحدد","hi":"▶  चयनित चलाएं","sv":"▶  Spela markerade",
  },
  "LISTEN_LAB_BTN_REMOVE_SELECTED": {
    "value":"🗑  Remove Selected","dynamic":False,
    "en":"🗑  Remove Selected","es":"🗑  Eliminar selección","fr":"🗑  Supprimer la sélection","de":"🗑  Auswahl entfernen","pt-BR":"🗑  Remover seleção","it":"🗑  Rimuovi selezione","nl":"🗑  Selectie verwijderen","ru":"🗑  Удалить выбранное","ja":"🗑  選択を削除","zh-CN":"🗑  删除选中项","ko":"🗑  선택 항목 제거","pl":"🗑  Usuń zaznaczone","tr":"🗑  Seçileni kaldır","ar":"🗑  إزالة المحدد","hi":"🗑  चयनित हटाएं","sv":"🗑  Ta bort markerade",
  },
  "LISTEN_LAB_BTN_SELECT_ALL": {
    "value":"☑  All","dynamic":False,
    "en":"☑  All","es":"☑  Todo","fr":"☑  Tout","de":"☑  Alle","pt-BR":"☑  Todos","it":"☑  Tutti","nl":"☑  Alles","ru":"☑  Все","ja":"☑  全て","zh-CN":"☑  全部","ko":"☑  전체","pl":"☑  Wszystko","tr":"☑  Tümü","ar":"☑  الكل","hi":"☑  सभी","sv":"☑  Alla",
  },
  "LISTEN_LAB_BTN_SELECT_NONE": {
    "value":"☐  None","dynamic":False,
    "en":"☐  None","es":"☐  Ninguno","fr":"☐  Aucun","de":"☐  Keine","pt-BR":"☐  Nenhum","it":"☐  Nessuno","nl":"☐  Geen","ru":"☐  Снять","ja":"☐  なし","zh-CN":"☐  无","ko":"☐  없음","pl":"☐  Żadne","tr":"☐  Hiçbiri","ar":"☐  لا شيء","hi":"☐  कोई नहीं","sv":"☐  Inget",
  },
  "LISTEN_LAB_SPEED_LABEL": {
    "value":"Speed","dynamic":False,
    "en":"Speed","es":"Velocidad","fr":"Vitesse","de":"Geschwindigkeit","pt-BR":"Velocidade","it":"Velocità","nl":"Snelheid","ru":"Скорость","ja":"速度","zh-CN":"速度","ko":"속도","pl":"Szybkość","tr":"Hız","ar":"السرعة","hi":"गति","sv":"Hastighet",
  },
  "LISTEN_LAB_VOL_LABEL": {
    "value":"Vol","dynamic":False,
    "en":"Vol","es":"Vol","fr":"Vol","de":"Laut","pt-BR":"Vol","it":"Vol","nl":"Vol","ru":"Гр","ja":"音量","zh-CN":"音量","ko":"음량","pl":"Gł","tr":"Ses","ar":"صوت","hi":"वॉल","sv":"Vol",
  },
  "LISTEN_LAB_MSG_NO_AUDIO_DROP": {
    "value":"No supported audio files found in drop","dynamic":False,
    "en":"No supported audio files found in drop","es":"No se encontraron archivos de audio compatibles","fr":"Aucun fichier audio pris en charge trouvé","de":"Keine unterstützten Audiodateien gefunden","pt-BR":"Nenhum arquivo de áudio compatível encontrado","it":"Nessun file audio supportato trovato","nl":"Geen ondersteunde audiobestanden gevonden","ru":"Поддерживаемые аудиофайлы не найдены","ja":"対応するオーディオファイルが見つかりません","zh-CN":"未找到支持的音频文件","ko":"지원되는 오디오 파일을 찾을 수 없음","pl":"Nie znaleziono obsługiwanych plików audio","tr":"Desteklenen ses dosyası bulunamadı","ar":"لم يتم العثور على ملفات صوتية مدعومة","hi":"समर्थित ऑडियो फ़ाइलें नहीं मिलीं","sv":"Inga stödda ljudfiler hittades",
  },
  "LISTEN_LAB_MSG_NO_FILES": {
    "value":"No files loaded — drag audio files here","dynamic":False,
    "en":"No files loaded — drag audio files here","es":"No hay archivos cargados — arrastra archivos de audio aquí","fr":"Aucun fichier chargé — glissez des fichiers audio ici","de":"Keine Dateien geladen — Audiodateien hier hineinziehen","pt-BR":"Nenhum arquivo carregado — arraste arquivos de áudio aqui","it":"Nessun file caricato — trascina file audio qui","nl":"Geen bestanden geladen — sleep audiobestanden hierheen","ru":"Нет загруженных файлов — перетащите аудиофайлы сюда","ja":"ファイルなし — オーディオファイルをここにドラッグ","zh-CN":"未加载文件 — 将音频文件拖至此处","ko":"파일 없음 — 여기에 오디오 파일을 드래그하세요","pl":"Nie załadowano plików — przeciągnij pliki audio tutaj","tr":"Dosya yüklenmedi — ses dosyalarını buraya sürükleyin","ar":"لم يتم تحميل ملفات — اسحب ملفات الصوت هنا","hi":"कोई फ़ाइल लोड नहीं — यहाँ ऑडियो फ़ाइलें खींचें","sv":"Inga filer laddade — dra ljudfiler hit",
  },
  "LISTEN_LAB_MSG_NO_SELECTION": {
    "value":"No items selected","dynamic":False,
    "en":"No items selected","es":"Ningún elemento seleccionado","fr":"Aucun élément sélectionné","de":"Keine Elemente ausgewählt","pt-BR":"Nenhum item selecionado","it":"Nessun elemento selezionato","nl":"Geen items geselecteerd","ru":"Нет выбранных элементов","ja":"アイテムが選択されていません","zh-CN":"未选中任何项目","ko":"선택된 항목 없음","pl":"Nie zaznaczono żadnych elementów","tr":"Öğe seçilmedi","ar":"لم يتم تحديد أي عنصر","hi":"कोई आइटम नहीं चुना गया","sv":"Inga objekt valda",
  },

  # ── Voice Lab – record section ────────────────────────────────────
  "VOICE_LAB_UPLOAD_HINT": {
    "value":"Upload a WAV reference clip to create a new voice. Zero-shot cloning — no fine-tuning required.","dynamic":False,
    "en":"Upload a WAV reference clip to create a new voice. Zero-shot cloning — no fine-tuning required.","es":"Sube un clip WAV de referencia para crear una nueva voz. Clonación zero-shot — sin ajuste fino.","fr":"Importez un clip WAV de référence pour créer une nouvelle voix. Clonage zéro-shot — aucun réglage fin requis.","de":"Laden Sie einen WAV-Referenzclip hoch, um eine neue Stimme zu erstellen. Zero-Shot-Klonierung — kein Fine-Tuning erforderlich.","pt-BR":"Faça upload de um clipe WAV de referência para criar uma nova voz. Clonagem zero-shot — sem ajuste fino.","it":"Carica un clip WAV di riferimento per creare una nuova voce. Clonazione zero-shot — nessuna messa a punto richiesta.","nl":"Upload een WAV-referentieclip om een nieuwe stem te maken. Zero-shot klonen — geen fine-tuning vereist.","ru":"Загрузите WAV-референс для создания нового голоса. Zero-shot клонирование — дообучение не требуется.","ja":"WAV参照クリップをアップロードして新しい音声を作成。ゼロショットクローン — ファインチューニング不要。","zh-CN":"上传 WAV 参考片段以创建新音色。零样本克隆 — 无需微调。","ko":"새 음성을 만들려면 WAV 참조 클립을 업로드하세요. 제로샷 클로닝 — 파인튜닝 불필요.","pl":"Prześlij plik WAV jako wzorzec, aby stworzyć nowy głos. Klonowanie zero-shot — bez dostrajania.","tr":"Yeni bir ses oluşturmak için bir WAV referans klibi yükleyin. Sıfır örnekli klonlama — ince ayar gerekmez.","ar":"ارفع مقطعاً مرجعياً بصيغة WAV لإنشاء صوت جديد. استنساخ بدون أمثلة — لا يلزم ضبط دقيق.","hi":"नई आवाज़ बनाने के लिए WAV संदर्भ क्लिप अपलोड करें। जीरो-शॉट क्लोनिंग — कोई फाइन-ट्यूनिंग नहीं।","sv":"Ladda upp ett WAV-referensklipp för att skapa en ny röst. Zero-shot kloning — ingen finjustering krävs.",
  },
  "VOICE_LAB_RECORD_HEADER": {
    "value":"🎙  Record Voice Sample","dynamic":False,
    "en":"🎙  Record Voice Sample","es":"🎙  Grabar muestra de voz","fr":"🎙  Enregistrer un échantillon vocal","de":"🎙  Sprachprobe aufnehmen","pt-BR":"🎙  Gravar amostra de voz","it":"🎙  Registra campione vocale","nl":"🎙  Spraakopname maken","ru":"🎙  Записать голосовой образец","ja":"🎙  音声サンプルを録音","zh-CN":"🎙  录制语音样本","ko":"🎙  음성 샘플 녹음","pl":"🎙  Nagraj próbkę głosu","tr":"🎙  Ses Örneği Kaydet","ar":"🎙  تسجيل عينة صوتية","hi":"🎙  आवाज़ नमूना रिकॉर्ड करें","sv":"🎙  Spela in röstprov",
  },
  "VOICE_LAB_MICROPHONE_LABEL": {
    "value":"Microphone:","dynamic":False,
    "en":"Microphone:","es":"Micrófono:","fr":"Microphone :","de":"Mikrofon:","pt-BR":"Microfone:","it":"Microfono:","nl":"Microfoon:","ru":"Микрофон:","ja":"マイク:","zh-CN":"麦克风:","ko":"마이크:","pl":"Mikrofon:","tr":"Mikrofon:","ar":"الميكروفون:","hi":"माइक्रोफ़ोन:","sv":"Mikrofon:",
  },
  "VOICE_LAB_BTN_RECORD": {
    "value":"●  Record","dynamic":False,
    "en":"●  Record","es":"●  Grabar","fr":"●  Enregistrer","de":"●  Aufnehmen","pt-BR":"●  Gravar","it":"●  Registra","nl":"●  Opnemen","ru":"●  Запись","ja":"●  録音","zh-CN":"●  录制","ko":"●  녹음","pl":"●  Nagraj","tr":"●  Kaydet","ar":"●  تسجيل","hi":"●  रिकॉर्ड","sv":"●  Spela in",
  },
  "VOICE_LAB_BTN_STOP_RECORD": {
    "value":"■  Stop","dynamic":False,
    "en":"■  Stop","es":"■  Detener","fr":"■  Arrêter","de":"■  Stopp","pt-BR":"■  Parar","it":"■  Ferma","nl":"■  Stoppen","ru":"■  Стоп","ja":"■  停止","zh-CN":"■  停止","ko":"■  중지","pl":"■  Zatrzymaj","tr":"■  Durdur","ar":"■  إيقاف","hi":"■  रोकें","sv":"■  Stopp",
  },
  "VOICE_LAB_STATUS_NO_RECORDING": {
    "value":"No recording","dynamic":False,
    "en":"No recording","es":"Sin grabación","fr":"Aucun enregistrement","de":"Keine Aufnahme","pt-BR":"Sem gravação","it":"Nessuna registrazione","nl":"Geen opname","ru":"Нет записи","ja":"録音なし","zh-CN":"无录音","ko":"녹음 없음","pl":"Brak nagrania","tr":"Kayıt yok","ar":"لا يوجد تسجيل","hi":"कोई रिकॉर्डिंग नहीं","sv":"Ingen inspelning",
  },
  "VOICE_LAB_STATUS_NO_RECORDING_YET": {
    "value":"No recording yet","dynamic":False,
    "en":"No recording yet","es":"Aún sin grabación","fr":"Pas encore d'enregistrement","de":"Noch keine Aufnahme","pt-BR":"Nenhuma gravação ainda","it":"Nessuna registrazione ancora","nl":"Nog geen opname","ru":"Запись отсутствует","ja":"まだ録音なし","zh-CN":"尚无录音","ko":"아직 녹음 없음","pl":"Jeszcze brak nagrania","tr":"Henüz kayıt yok","ar":"لا يوجد تسجيل حتى الآن","hi":"अभी कोई रिकॉर्डिंग नहीं","sv":"Ingen inspelning ännu",
  },
  "VOICE_LAB_BTN_CLONE_FROM_REC": {
    "value":"🧬  Clone Voice","dynamic":False,
    "en":"🧬  Clone Voice","es":"🧬  Clonar voz","fr":"🧬  Cloner la voix","de":"🧬  Stimme klonen","pt-BR":"🧬  Clonar voz","it":"🧬  Clona voce","nl":"🧬  Stem klonen","ru":"🧬  Клонировать голос","ja":"🧬  音声をクローン","zh-CN":"🧬  克隆声音","ko":"🧬  음성 복제","pl":"🧬  Sklonuj głos","tr":"🧬  Ses Klonla","ar":"🧬  استنساخ الصوت","hi":"🧬  आवाज़ क्लोन करें","sv":"🧬  Klona röst",
  },
  "VOICE_LAB_STATUS_RECORDING_ACTIVE": {
    "value":"Recording…","dynamic":False,
    "en":"Recording…","es":"Grabando…","fr":"Enregistrement…","de":"Aufnahme läuft…","pt-BR":"Gravando…","it":"Registrazione…","nl":"Opname…","ru":"Запись…","ja":"録音中…","zh-CN":"录制中…","ko":"녹음 중…","pl":"Nagrywanie…","tr":"Kaydediliyor…","ar":"جارٍ التسجيل…","hi":"रिकॉर्डिंग हो रही है…","sv":"Spelar in…",
  },
  "VOICE_LAB_STATUS_NOTHING_CAPTURED": {
    "value":"Nothing captured","dynamic":False,
    "en":"Nothing captured","es":"Nada capturado","fr":"Rien de capturé","de":"Nichts aufgenommen","pt-BR":"Nada capturado","it":"Nessun audio catturato","nl":"Niets opgenomen","ru":"Ничего не записано","ja":"音声が録音されませんでした","zh-CN":"未捕获任何内容","ko":"캡처된 내용 없음","pl":"Nie nagrano nic","tr":"Hiçbir şey yakalanmadı","ar":"لم يتم التقاط أي شيء","hi":"कुछ नहीं पकड़ा गया","sv":"Inget inspelat",
  },
  "VOICE_LAB_STATUS_TRANSCRIBING_REC": {
    "value":"Transcribing recording for voice conditioning…","dynamic":False,
    "en":"Transcribing recording for voice conditioning…","es":"Transcribiendo grabación para acondicionamiento de voz…","fr":"Transcription de l'enregistrement pour le conditionnement vocal…","de":"Aufnahme für Voice-Conditioning wird transkribiert…","pt-BR":"Transcrevendo gravação para condicionamento de voz…","it":"Trascrizione della registrazione per il condizionamento vocale…","nl":"Opname transcriberen voor stemconditionering…","ru":"Транскрипция записи для обработки голоса…","ja":"音声コンディショニング用に録音を文字起こし中…","zh-CN":"正在为语音调节转录录音…","ko":"음성 조건화를 위해 녹음 전사 중…","pl":"Transkrypcja nagrania do kondycjonowania głosu…","tr":"Ses koşullandırması için kayıt transkripsiyonu yapılıyor…","ar":"جارٍ نسخ التسجيل لتهيئة الصوت…","hi":"आवाज़ कंडीशनिंग के लिए रिकॉर्डिंग ट्रांसक्राइब हो रही है…","sv":"Transkriberar inspelning för röstanpassning…",
  },

  # ── AI Prompt Editor window ─────────────────────────────────────
  "PROMPT_EDITOR_TITLE": {
    "value":"AI Prompt Editor","dynamic":False,
    "en":"AI Prompt Editor","es":"Editor de prompts de IA","fr":"Éditeur de prompts IA","de":"KI-Prompt-Editor","pt-BR":"Editor de prompts de IA","it":"Editor prompt AI","nl":"AI-prompteditor","ru":"Редактор AI-запросов","ja":"AI プロンプト エディター","zh-CN":"AI 提示编辑器","ko":"AI 프롬프트 편집기","pl":"Edytor promptów AI","tr":"AI Komut Editörü","ar":"محرر موجهات الذكاء الاصطناعي","hi":"AI प्रॉम्प्ट एडिटर","sv":"AI-promptredigerare",
  },
  "PROMPT_EDITOR_HINT": {
    "value":"Changes take effect immediately — saved to prompts.json alongside the app.","dynamic":False,
    "en":"Changes take effect immediately — saved to prompts.json alongside the app.","es":"Los cambios surten efecto de inmediato — guardados en prompts.json junto a la app.","fr":"Les modifications prennent effet immédiatement — sauvegardées dans prompts.json à côté de l'application.","de":"Änderungen werden sofort übernommen — in prompts.json neben der App gespeichert.","pt-BR":"As alterações têm efeito imediato — salvas em prompts.json junto ao app.","it":"Le modifiche hanno effetto immediato — salvate in prompts.json accanto all'app.","nl":"Wijzigingen worden direct van kracht — opgeslagen in prompts.json naast de app.","ru":"Изменения вступают в силу немедленно — сохраняются в prompts.json рядом с приложением.","ja":"変更はすぐに反映されます — アプリと同じ場所の prompts.json に保存されます。","zh-CN":"更改立即生效 — 已保存到应用旁的 prompts.json。","ko":"변경 사항이 즉시 적용됩니다 — 앱 옆의 prompts.json에 저장됩니다.","pl":"Zmiany wchodzą w życie natychmiast — zapisane w prompts.json obok aplikacji.","tr":"Değişiklikler hemen geçerli olur — uygulamanın yanındaki prompts.json dosyasına kaydedilir.","ar":"تسري التغييرات فوراً — محفوظة في prompts.json بجانب التطبيق.","hi":"परिवर्तन तुरंत प्रभावी होते हैं — ऐप के साथ prompts.json में सहेजे जाते हैं।","sv":"Ändringar träder i kraft omedelbart — sparas i prompts.json bredvid appen.",
  },
  "PROMPT_EDITOR_STATUS_SAVED": {
    "value":"✅ Prompts saved","dynamic":False,
    "en":"✅ Prompts saved","es":"✅ Prompts guardados","fr":"✅ Prompts enregistrés","de":"✅ Prompts gespeichert","pt-BR":"✅ Prompts salvos","it":"✅ Prompt salvati","nl":"✅ Prompts opgeslagen","ru":"✅ Запросы сохранены","ja":"✅ プロンプト保存済み","zh-CN":"✅ 提示已保存","ko":"✅ 프롬프트 저장됨","pl":"✅ Prompty zapisane","tr":"✅ Komutlar kaydedildi","ar":"✅ تم حفظ الموجهات","hi":"✅ प्रॉम्प्ट सहेजे गए","sv":"✅ Prompter sparade",
  },
  "PROMPT_EDITOR_STATUS_RESET": {
    "value":"Prompts reset to defaults","dynamic":False,
    "en":"Prompts reset to defaults","es":"Prompts restablecidos a valores predeterminados","fr":"Prompts réinitialisés aux valeurs par défaut","de":"Prompts auf Standardwerte zurückgesetzt","pt-BR":"Prompts redefinidos para os padrões","it":"Prompt ripristinati ai valori predefiniti","nl":"Prompts teruggezet naar standaardwaarden","ru":"Запросы сброшены до значений по умолчанию","ja":"プロンプトをデフォルトにリセット","zh-CN":"提示已重置为默认值","ko":"프롬프트가 기본값으로 재설정됨","pl":"Prompty przywrócone do domyślnych","tr":"Komutlar varsayılanlara sıfırlandı","ar":"تمت إعادة ضبط الموجهات إلى الافتراضي","hi":"प्रॉम्प्ट डिफ़ॉल्ट पर रीसेट हुए","sv":"Prompter återställda till standard",
  },
  "PROMPT_EDITOR_BTN_SAVE": {
    "value":"💾  Save All","dynamic":False,
    "en":"💾  Save All","es":"💾  Guardar todo","fr":"💾  Tout enregistrer","de":"💾  Alle speichern","pt-BR":"💾  Salvar tudo","it":"💾  Salva tutto","nl":"💾  Alles opslaan","ru":"💾  Сохранить всё","ja":"💾  すべて保存","zh-CN":"💾  全部保存","ko":"💾  모두 저장","pl":"💾  Zapisz wszystko","tr":"💾  Tümünü Kaydet","ar":"💾  حفظ الكل","hi":"💾  सब सहेजें","sv":"💾  Spara alla",
  },
  "PROMPT_EDITOR_BTN_RESET": {
    "value":"↺  Reset to Defaults","dynamic":False,
    "en":"↺  Reset to Defaults","es":"↺  Restablecer valores predeterminados","fr":"↺  Réinitialiser aux valeurs par défaut","de":"↺  Auf Standard zurücksetzen","pt-BR":"↺  Restaurar padrões","it":"↺  Ripristina predefiniti","nl":"↺  Herstellen naar standaard","ru":"↺  Сбросить до стандартных","ja":"↺  デフォルトにリセット","zh-CN":"↺  重置为默认值","ko":"↺  기본값으로 초기화","pl":"↺  Przywróć domyślne","tr":"↺  Varsayılanlara sıfırla","ar":"↺  إعادة التعيين إلى الافتراضي","hi":"↺  डिफ़ॉल्ट पर रीसेट करें","sv":"↺  Återställ till standard",
  },

  # ── Settings extras ─────────────────────────────────────────────
  "SETTINGS_HF_TOKEN_LABEL": {
    "value":"HuggingFace Token:","dynamic":False,
    "en":"HuggingFace Token:","es":"Token de HuggingFace:","fr":"Jeton HuggingFace :","de":"HuggingFace-Token:","pt-BR":"Token do HuggingFace:","it":"Token HuggingFace:","nl":"HuggingFace-token:","ru":"Токен HuggingFace:","ja":"HuggingFace トークン:","zh-CN":"HuggingFace 令牌:","ko":"HuggingFace 토큰:","pl":"Token HuggingFace:","tr":"HuggingFace Tokeni:","ar":"رمز HuggingFace:","hi":"HuggingFace टोकन:","sv":"HuggingFace-token:",
  },
}

with open('translations.json', encoding='utf-8') as f:
    data = json.load(f)

strings = data['strings']
added = 0
skipped = 0
for key, entry in NEW_KEYS.items():
    if key in strings:
        skipped += 1
    else:
        strings[key] = entry
        added += 1

with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

with open('translations.json', encoding='utf-8') as f:
    json.load(f)

print(f"Added {added} new keys, skipped {skipped} existing. Total: {len(strings)}. File valid.")
