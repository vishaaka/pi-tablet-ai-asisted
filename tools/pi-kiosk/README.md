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
- `kiosk.env`
- `labwc-autostart`
- `pitablet-kiosk-launcher.sh`
- `kiosk-home.html`

Varsayilan kiosk sayfasi yerel bir bekleme ekranidir:

- `file:///opt/pitablet/kiosk/home.html`

Gercek uygulama hazir oldugunda sadece `kiosk.env` icindeki
`KIOSK_URL` degeri degistirilir.
