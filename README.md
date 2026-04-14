# Pi Tablet AI Assisted

> **ANA ÜRÜN TANIMI (DEĞİŞMEZ):**
>
> Bu proje öncelikle **çocuk için eğitici, eğlenceli, AI destekli yaşayan tablet uygulamasıdır.**
>
> Projenin merkezi hedefi:
>
> * çocuk dostu ana menü
> * YouTube Kids tabanlı güvenli video akışı
> * AI önerili mini oyunlar
> * eşya tanıma / nesne bulma
> * gördüğü şey hakkında konuşmaya teşvik
> * kamera ile gerçek dünyadan nesne buldurma
> * AI arkadaş ile konuşma
>
> **ÖNEMLİ KURAL:**
> Parent panel, layered scene editor, asset studio ve diğer tüm PC-side araçlar yalnızca bu ana ürün deneyimini BESLEYEN arka plan geliştirme araçlarıdır.
>
> Proje hiçbir aşamada yalnızca terapi materyali editörüne dönüşmeyecek.
>
> Geliştirilen tüm fonksiyonlar:
>
> * asset sistemi
> * layered scene sistemi
> * parent dashboard
> * orchestration
> * preload
> * analytics
>
> şu an korunacaktır; ancak ileride optimizasyon aşamasında ana çocuk tablet deneyimine hizmet etmeyen parçalar çıkarılabilir, sadeleştirilebilir veya tamamen değiştirilebilir.
>
> **ANA HEDEF HER ZAMAN:**
>
> > yaşayan AI çocuk tableti + eğitici eğlence + konuşma teşviki

## Misyon

Pi Tablet AI Assisted projesinin temel amacı, **konuşma gecikmesi yaşayan çocuklar için AI destekli, ebeveyn denetimli, terapi odaklı bir etkileşim sistemi** geliştirmektir.

Sistem özellikle:

* konuşmayı teşvik etme
* dikkat süresini artırma
* hedef kelime tekrarını doğal oyunlaştırma ile sunma
* ilgi alanına göre içerik uyarlama
* ebeveynin sürekli başında olmadan terapi akışını sürdürebilme
* gerektiğinde ebeveynin canlı müdahale edebilmesi

hedefleri üzerine kuruludur.

Bu proje klasik kart gösterim sisteminden farklı olarak:

> **AI destekli dinamik terapi sahneleri + ebeveyn kontrollü öğrenme orkestrasyonu**

mantığında ilerler.

---

# Vizyon

Uzun vadeli hedef, Raspberry Pi tabanlı çocuk dostu bir terapi cihazını aşağıdaki seviyeye taşımaktır:

* konuşmaya teşvik eden rehber avatar
* ağız hareketi animasyonları
* kamera tabanlı dikkat analizi
* ilgi alanı öğrenen asset sistemi
* otomatik seans zorluk ayarı
* ebeveyn dashboard üzerinden canlı kontrol
* ana PC üzerinde güçlü AI inference
* Pi tarafında hafif render ve cache
* medya üretimi için PC üstünden Hugging Face / dış AI servis entegrasyonu

Nihai vizyon:

> **Ev tipi kişisel AI terapi arkadaşı**

özellikle konuşma gecikmesi, dikkat zorlukları ve erken gelişim desteği için sürdürülebilir bir platform oluşturmak.

---

# Sistem Mimarisi

## A) Ana PC

Merkezi zeka burada çalışır.

Görevler:

* AI inference
* görsel / ses / video üretimi
* session orchestration
* asset learning
* layered scene üretimi
* parent dashboard
* scene editor
* payload queue yönetimi
* milestone / progress tracking

## B) Raspberry Pi 

Çocuk tarafındaki hafif istemci.

Görevler:

* ekran render
* mikrofon
* hoparlör
* kamera bridge
* preload edilmiş content pack oynatma
* layered scene render
* local cache

## C) Parent Dashboard

Ebeveyn ve terapist kontrol paneli.

Özellikler:

* canlı müdahale
* manuel asset ekleme
* thumbnail preview
* layered scene editor
* z-order layer yönetimi
* Pi’ye canlı gönderim
* draft ve payload preview
* otonom seans başlat/durdur

---

# Proje İlkeleri

## 1) Çocuk tarafı her zaman hafif kalacak

Pi tarafında AI inference minimum tutulur.

Pi’nin görevi:

* hazır sahneyi göstermek
* preload yapmak
* hızlı tepki vermek

## 2) Asıl zeka PC tarafında

Ana karar sistemi:

* asset seçimi
* ilgi analizi
* sahne oluşturma
* rehber avatar yönetimi
* session success scoring

PC tarafında kalır.

## 3) Ebeveyn her zaman müdahil olabilir

Sistem tamamen otonom çalışsa bile:

* canlı asset gönderme
* sahne düzenleme
* seans durdurma
* yeni hedef belirleme

her zaman panelden yapılabilir.

---

# Mevcut Final PC-Side Mimari

## Temel backend omurgası

## Aktif PC-Side Yapısı

README ile uyumlu sade PC-side omurgası aşağıdaki dosyalar etrafında tutulacaktır:

* `pc-side/services/parent_panel.py` — ebeveyn paneli API ve ana kontrol yüzeyi
* `pc-side/ui/parent_panel_ui.html` — üretim panel arayüzü
* `pc-side/core/scene_manager.py` — katmanlı sahne kayıt ve payload üretimi
* `pc-side/storage/asset_manager.py` — asset kayıt ve kullanım istatistikleri
* `pc-side/core/session_orchestrator.py` — otonom seans akışı ve pack üretimi
* `pc-side/core/content_pack_builder.py` — konuşma kartı / preload pack üretimi
* `pc-side/storage/command_queue.py` — Pi'ye gidecek komut kuyruğu
* `pc-side/system/server_manager.py` + `manage_servers.*` — servis başlatma / durdurma
* `pc-side/services/app.py` — dikkat, konuşma ve basit AI karar servisi
* `pc-side/services/middleware.py` — LM Studio tabanlı ara yönlendirme katmanı
* `pc-side/services/media_gateway.py` — Hugging Face tabanlı görsel / ses / video üretim katmanı
* `pc-side/services/dashboard.py` — milestone ve özet verileri
* `pc-side/storage/db.py`, `storage/speech.py`, `core/milestone_engine.py` — temel veri ve analiz katmanı
* `pc-side/config/settings.json` — port, yol, model ve API ayarları için merkezî dosya
* `pc-side/setup_pitablet.ps1` + `setup_pitablet.bat` — bu çalışma klasöründen `C:\pitablet` canlı kurulumuna güvenli aktarım
* `pc-side/data/` — çalışan sistemin runtime verileri
* `pc-side/assets/` — kayıtlı görseller

Bu çekirdek dışında kalan kopya klasörler, bozuk eski importer scriptleri ve kullanılmayan legacy yardımcılar mümkün olduğunca repodan temiz tutulacaktır.

## Ana Makine AI + Medya Yükü

Pi tarafının internete veya Hugging Face servislerine doğrudan bağlanmaması temel
tercihtir.

Bu nedenle:

* çocukla konuşma için ana LLM ve orkestrasyon PC-side üzerinde kalır
* görsel üretimi, TTS ve video üretimi yine PC-side üzerinde çalışır
* Pi yalnızca PC'den gelen komut, metadata ve dosya URL'lerini tüketir
* token, provider ve model ayarları sadece ana makinede tutulur

Bu akış için yeni medya üretim servisi:

* `pc-side/services/media_gateway.py`

üzerinden yönetilir ve middleware gerektiğinde bu servise araç çağrısı yapar.

## Deployment Akışı

PC-side çalışma klasörü kaynak paket olarak korunur.

Makinede canlı çalışan kurulum hedefi:

* `C:\pitablet`

Yedek hedefi:

* `C:\pitablet_backups`

Kurulum / senkron komutları:

* `pc-side\setup_pitablet.bat`
* `pc-side\setup_pitablet.ps1 -InstallRequirements`

Bu akışın amacı:

* mevcut workspace'i bozmadan canlı klasöre aktarım yapmak
* `C:\pitablet` içeriğini aktarım öncesi yedeklemek
* acil durumda eski çalışan kurulumlara hızlı dönebilmek
* farklı bilgisayarda aynı paket yapısını kolay taşımak

### `pc-side/storage/asset_manager.py`

Asset manifest yönetimi.

Sorumluluklar:

* manuel asset create/update
* image_base64 kayıt
* thumbnail path
* label_tr / tags_tr / interests_tr
* preferred
* history
* stats

## `pc-side/core/scene_manager.py`

Katmanlı sahne sistemi.

Sorumluluklar:

* scene create/update/delete
* layer normalization
* z-order sıralama
* layered scene payload üretimi
* Pi contract

## `pc-side/services/parent_panel.py`

API katmanı.

Ana endpoint grupları:

* `/assets/*`
* `/scenes/*`
* `/screen/layered_scene`
* `/autonomy/*`
* `/queue`
* `/server/*`

## `pc-side/ui/parent_panel_ui.html`

Üretim hazır ebeveyn paneli.

Özellikler:

* asset studio
* scene editor
* drag & drop layer preview
* öne getir / arkaya gönder
* ortada kalsın
* merkeze al
* Pi gönder
* kayıtlı sahneler

---

# Layered Scene Standard

Pi’ye giden standart payload:

```json
{
  "screen": "layered_speech_scene",
  "scene_id": "scene_top_001",
  "target_word": "top",
  "pronunciation": "to-p",
  "canvas": {
    "width": 1280,
    "height": 720,
    "background": "#ffffff"
  },
  "layers": []
}
```

Katman tipleri:

* background
* decor
* image
* avatar
* text
* guide

---

# Rehber Avatar Vizyonu

Standart rehber karakter:

* parlak kızıl dalgalı saç
* yeşil göz
* oval yüz
* sıcak ifade
* net ağız bölgesi
* çocuk dostu stil

İleriki sürüm:

* phoneme based mouth animation
* lip sync
* 1e1 konuşma yönlendirme
* dikkat düşüşünde jest/mimik destekleri

---

# Yakın Yol Haritası

## Faz 1 — Pi Renderer

* layered scene renderer
* z-order çizim
* avatar render
* guide text render
* preload next scene

## Faz 2 — Adaptive Learning

* camera attention feedback
* asset preferred scoring
* başarısız asset düşürme
* ilgi alanı kaydırma
* session success tracker

## Faz 3 — Therapy Intelligence

* konuşma analizi
* kelime bazlı başarı skoru
* ağız hareketi avatar
* ebeveyn öneri motoru
* otomatik günlük terapi planı

---

# Final Not

Bu README proje hafızası olarak kullanılacaktır.

Amaç:

> yeni sohbetlerde tekrar tekrar özet çıkarmadan doğrudan geliştirmeye devam edebilmek

Özellikle mimari kararlar, misyon, vizyon ve teknik kontratlar burada korunmalıdır.
