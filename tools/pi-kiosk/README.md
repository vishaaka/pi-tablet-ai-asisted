## Pi Kiosk Setup

Bu klasor Raspberry Pi imajini hafif bir kiosk tablete cevirmek icin
kullanilan dosyalari tutar.

Amac:

- `pi` kullanicisina otomatik giris
- tam masaustu yerine yalniz kiosk oturumu
- panel ve masaustu yoneticisini kapatma
- Chromium'u tam ekran kiosk olarak acma
- URL ve browser ayarlarini tek dosyadan degistirebilme
- gereksiz arka plan servislerini azaltma

Ana dosyalar:

- `apply_pi_kiosk.ps1`
- `apply_pi_kiosk_linux.sh`
- `kiosk.env`
- `ayda-web.env`
- `ayda-web.service`
- `labwc-autostart`
- `pitablet-kiosk-launcher.sh`
- `pitablet-install-runtime.sh`
- `kiosk-home.html`

Varsayilan kiosk hedefi AYDA'nin yerel web arayuzudur:

- `http://127.0.0.1:8090`

AYDA web servisi:

- `python3 -m ayda.web.app`
- `ayda-web.service` ile `multi-user.target` altinda acilir
- Chromium kiosk dogrudan bu arayuze gider

## Onerilen Modifikasyon Yolu

Pi OS'i x86 sanal makinede dogrudan boot etmeye calismak yerine:

1. VHD / imaj dosyasini Ubuntu VM veya WSL icinde mount et
2. `apply_pi_kiosk_linux.sh` scriptini rootfs'e uygula
3. Ilk acilista Pi uzerinde `pitablet-install-runtime.sh` ile eksik paketleri kur

Bu yol ARM boot / donanim emulasyonu zorluklarini atlar ve imaji dogrudan
dosya sistemi seviyesinde sekillendirmenizi saglar.
