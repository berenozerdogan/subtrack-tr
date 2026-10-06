# SubTrack TR - Dijital Harcama ve Zam Simulatörü

Turkiye'deki populer dijital aboneliklerin (dizi, film, muzik, depolama, yapay zeka vb.) guncel fiyatlarini takip eden, kisisel harcama sepeti olusturan ve olasi enflasyon senaryolarini canli simule eden full-stack web uygulamasidir.

---

## Ozellikler

- **Full-Stack Mimari:** FastAPI (Python) tabanli RESTful backend ve Vanilla JS, Tailwind CSS, Chart.js tabanli frontend.
- **Iliskisel Veritabani Modeli:** SQLite uzerinde `services` ve `service_plans` tablolari arasinda kurulan bire-cok (1:N) iliski mimarisi.
- **Dinamik Zam Simulatoru:** Arayuzdeki kaydirma cubugu (slider) uzerinden %5 ile %100 arasindaki artislarin aylik ve yillik toplam yuk uzerindeki etkisinin anlik hesaplanmasi.
- **Backend Is Mantigi ve Guvenlik:**
  - SQL alt sorgulari (subquery) ile kategori bazli ya da genel toplu fiyat guncelleme destegi (`PUT`).
  - Mukerrer servis kayitlarini onleyen `slug` denetimi ve `400 Bad Request` mekanizmasi.
  - Var olmayan servislere plan eklenmesini engelleyen yabanci anahtar (Foreign Key) dogrulamasi ve `404 Not Found` yonetimi.
  - Veritabani seviyesinde agregasyon sorgulari (`SUM`, `AVG`, `COUNT`).
  - Dinamik kategori filtreleme uclari (`GET /api/services/filter`).
- **Veri Gorsellestirme:** Kullanicinin sectigi servislerin butce payini dinamik olarak cizen Chart.js halka grafigi (Doughnut Chart).
- **Arayuzden Veri Girisi:** Swagger bagimliligini ortadan kaldiran, kullanicinin yeni servis ve plan tanimlayabildigi form modali.

---

## Teknoloji Yigini

- **Backend:** Python 3, FastAPI, Uvicorn, SQLite3, Pydantic
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Fetch API), Chart.js, FontAwesome

---

## Kurulum ve Calistirma

### 1. Gereksinimleri Yukleyin

Proje kok dizininde yer alan gereksinimleri yukleyin:

```bash
pip install -r requirements.txt
```

### 2. Backend Sunucusunu Baslatin

Uvicorn sunucusunu 8001 portunda calistirin:

```bash
uvicorn main:app --reload --port 8001
```

Sunucu baslatildiktan sonra asagidaki adreslerden erisim saglanabilir:
- **API Kok Adres:** `http://127.0.0.1:8001`
- **Swagger UI Dokumantasyonu:** `http://127.0.0.1:8001/docs`
- **ReDoc Dokumantasyonu:** `http://127.0.0.1:8001/redoc`

### 3. Kullanici Arayuzunu Acin

`frontend/index.html` dosyasini herhangi bir web tarayicisinda (Chrome, Safari, Firefox) acarak uygulamayi kullanmaya baslayabilirsiniz.

---

## API Uclari Ozeti

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/api/services` | Tum servisleri ve bagli planlarini listeler |
| `GET` | `/api/services/filter` | Kategoriye gore servisleri filtreler |
| `POST` | `/api/services/new` | Yeni servis kaydi ekler (Mukerrer kontrolu icerir) |
| `POST` | `/api/service-plans/new` | Belirtilen servise yeni plan baglar (FK kontrolu icerir) |
| `POST` | `/api/calculate` | Secili planlarin aylik/yillik toplam ve kategori dagilimini hesaplar |
| `PUT` | `/api/service-plans/batch-update-price` | Kategori veya tum planlara yuzdelik zam uygular |
| `GET` | `/api/stats/summary` | Toplam servis, plan ve ortalama fiyat istatistiklerini getirir |