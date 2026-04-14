# AYDA Training

Bu klasor AYDA'nin Turkce, neseli ve cocuk dostu konusma tarzini egitmek icin
hazirlanan ilk seed veri ve egitim notlarini tutar.

## Hedef Persona

AYDA su davranislari guclendirmek icin egitilir:

- kisa ve sicak Turkce cumleler
- cesaret veren geri bildirim
- oyuna davet eden enerjik ton
- kisa hikaye baslatma ve surdurme
- hayal kirikliginda sakinlestirme
- cocugu utandirmadan tekrar denetme
- ebeveyn modunda daha net ve sinirli cevaplar

## Seed Set Kapsami

`ayda_seed_sft.jsonl` icindeki ornekler su kategorileri kapsar:

- greeting
- encouragement
- play_invite
- story
- speech_practice
- object_talk
- calming
- parent_boundary

Bu seed set final veri seti degildir. Ama ilk LoRA kosusunu baslatmak,
persona tonunu sabitlemek ve sonraki veri toplama turu icin taban olusturmak
icin yeterlidir.

## Hazir Egitim Scripti

Bu klasorde yer alan:

- `train_ayda_seed_qlora.py`
- `train_ayda_seed_gemma4_lora.py`
- `ayda_compare_prompts.json`

dosyasi, seed veri ile ilk Turkce AYDA QLoRA kosusu icin hazirlandi.

HF Jobs veya yerel GPU uzerinde calistirilabilir.

`ayda_compare_prompts.json` ise Qwen ve Gemma ciktilarini ayni mini soru seti ile
kiyaslamak icin tutulur.

## Onerilen Egitim Akisi

1. Seed set ile ilk QLoRA calistir.
2. Sonuclari Pi uzerinde hiz ve ton acisindan test et.
3. Kotu cevaplari ve eksik davranislari etiketle.
4. Veri setine yeni zorlayici ornekler ekle.
5. Ikinci tur LoRA ile kaliteyi arttir.

## Taban Model

Ilk kosu icin hedef model:

- `Qwen/Qwen2.5-1.5B-Instruct`
- `google/gemma-4-E2B-it`

Hedef cikti:

- `GGUF` cevrimine uygun LoRA / adapter cikti
- Pi 5 16GB ustunde hafif, kontrollu ve kisa cevaplar

## Pi 5 Hazirlik Plani

Egitim tamamlandiginda hedef akis su olacak:

1. Hub'daki LoRA adapter cikisini indir.
2. Adapter'i taban model ile merge et.
3. `llama.cpp` ile `GGUF` formata cevir.
4. `Q4_K_M` veya benzeri hafif bir quant olustur.
5. Pi 5 uzerinde `llama-server` ile servis et.
6. AYDA'yi `settings.yaml` icinden `local` backend ile calistir.

Bu repo icinde AYDA artik iki kaynaga baglanabilecek sekilde hazirlandi:

- PC tarafindaki middleware (`pc`)
- Pi uzerindeki `llama.cpp` sunucusu (`local`)

Varsayilan davranis `auto` modudur. Yani once PC'yi dener, o yoksa Pi
uzerindeki yerel modeli kullanir.

## Ornek Pi Runtime Ayari

`ayda/settings.yaml` dosyasindaki `bridge.local` bolumu Pi tarafi icin temel
ayar noktasi olacak:

- `base_url`: `llama-server` adresi
- `model`: yuklenecek GGUF model adi
- `max_tokens`: kisa ve kontrollu cevap limiti
- `temperature`: cevap sicakligi
- `system_prompt`: AYDA persona tanimi

Gerekirse su ortam degiskenleri ile hizli override yapilabilir:

- `AYDA_BRIDGE_BACKEND`
- `AYDA_LOCAL_BASE_URL`
- `AYDA_LOCAL_MODEL`
- `AYDA_LOCAL_MAX_TOKENS`
- `AYDA_LOCAL_TEMPERATURE`

## Karsilastirma Notu

Pratik karar verme akisi su sekilde olabilir:

1. Qwen LoRA ve Gemma LoRA ayni seed set ile kosulur.
2. `ayda_compare_prompts.json` icindeki sabit istemlerle iki model test edilir.
3. Asagidaki noktalara bakilir:
   - Turkce dogalligi
   - kisa cevap disiplini
   - cocuk dostu sicak ton
   - ebeveyn siniri koyma basarisi
   - Pi hedefi icin hiz ve bellek uygunlugu

Gemma 4 genelde kalite tarafinda avantajli olabilir. Qwen 2.5 ise Pi tarafina
merge ve GGUF cevrimi acisindan daha dusuk riskli bir taban olarak tutulur.

## GGUF Sonrasi Ornek Calistirma

Pi tarafinda hedeflenen servis komutu mantik olarak su sekilde olacak:

```bash
llama-server -m /opt/ayda/models/ayda-qwen2.5-1.5b-tr-seed-q4_k_m.gguf --port 8080 --ctx-size 2048 --threads 4
```

Ardindan AYDA metin omurgasi:

```bash
python -m ayda.main
```

Boylece hikaye, sohbet ve daha serbest istekler PC baglantisi yokken bile
yerelde cevaplanabilecek.

## Not

Hugging Face Jobs ile uzaktan egitim baslatmak istendiginde hesapta
yeterli pre-paid credit bulunmasi gerekir.
