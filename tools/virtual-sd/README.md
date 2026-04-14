# Virtual SD Card

Bu klasor, Raspberry Pi icin Windows uzerinde kullanilabilecek sanal bir SD kart
olusturmak ve yonetmek icin kucuk yardimci scriptler icerir.

## Hedef

- Windows'ta baglanabilen bir `VHDX` dosyasi olusturmak
- Raspberry Pi Imager veya benzeri araclarla bu sanal diske temiz kurulum yapmak
- Sonrasinda ayni icerigi gercek SD karta yazmak

## Varsayilan Dosya

Scriptler varsayilan olarak su yolu kullanir:

- `C:\pitablet_virtual_sd\pi5-virtual-sd.vhdx`

## Scriptler

- `create_virtual_sd.ps1`
- `attach_virtual_sd.ps1`
- `detach_virtual_sd.ps1`

## Ornek Kullanim

Yonetici PowerShell ile:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\tools\\virtual-sd\\create_virtual_sd.ps1 -Attach
```

Sadece tekrar baglamak icin:

```powershell
.\\tools\\virtual-sd\\attach_virtual_sd.ps1
```

Ayirmak icin:

```powershell
.\\tools\\virtual-sd\\detach_virtual_sd.ps1
```

## Notlar

- Varsayilan boyut `110 GB` olarak ayarlanmistir. Bu, 128 GB sinifindaki pek cok
  kart icin guvenli bir ust sinirdir ve fiziksel karttan biraz daha kucuk tutularak
  geri yazma tarafinda uyumsuzluk riskini azaltir.
- Varsayilan hedef yol ASCII tutulmustur. Bu sayede `diskpart` tarafinda Turkce
  karakterli klasor yollarindan dogabilecek sorunlar azalir.
- Kurulumdan sonra istersen bu sanal diski ayri bir `img` akisina cevirmek icin
  ek script de hazirlayabiliriz.
