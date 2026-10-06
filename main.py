import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import HTTPException
from typing import Optional
from fastapi import FastAPI, HTTPException

app = FastAPI(title="SubTrack TR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("subtrack.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/services")
def list_services():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM services ORDER BY category, name ASC")
    services = [dict(r) for r in c.fetchall()]
    
    # Her servisin planlarını iliştir
    for s in services:
        c.execute("SELECT id, plan_name, current_price, billing_cycle FROM service_plans WHERE service_id = ?", (s["id"],))
        s["plans"] = [dict(p) for p in c.fetchall()]
        
    conn.close()
    return services

class CalculateRequest(BaseModel):
    selected_plan_ids: List[int]
    custom_items: Optional[List[dict]] = []

@app.post("/api/calculate")
def calculate_expenses(req: CalculateRequest):
    conn = get_db()
    c = conn.cursor()
    
    total_monthly = 0.0
    category_totals = {}
    detailed_list = []
    
    if req.selected_plan_ids:
        placeholders = ",".join(["?"] * len(req.selected_plan_ids))
        query = f"""
            SELECT p.id as plan_id, p.plan_name, p.current_price, s.name as service_name, 
                   s.category, s.brand_color, s.icon_class
            FROM service_plans p
            JOIN services s ON p.service_id = s.id
            WHERE p.id IN ({placeholders})
        """
        c.execute(query, req.selected_plan_ids)
        rows = c.fetchall()
        for r in rows:
            item = dict(r)
            price = item["current_price"]
            total_monthly += price
            cat = item["category"]
            category_totals[cat] = category_totals.get(cat, 0.0) + price
            detailed_list.append(item)
            
    # Kullanıcı özel abonelik eklediyse
    for custom in req.custom_items or []:
        price = float(custom.get("price", 0))
        name = custom.get("name", "Özel Servis")
        cat = custom.get("category", "Diğer")
        total_monthly += price
        category_totals[cat] = category_totals.get(cat, 0.0) + price
        detailed_list.append({
            "plan_id": None,
            "plan_name": "Özel Plan",
            "current_price": price,
            "service_name": name,
            "category": cat,
            "brand_color": "#64748B",
            "icon_class": "fa-solid fa-credit-card"
        })

    conn.close()

    total_yearly = total_monthly * 12
    # Zam Simülasyonu (%25 ve %40 enflasyon zammı senaryosu)
    sim_zam_25 = round(total_monthly * 1.25, 2)
    sim_zam_40 = round(total_monthly * 1.40, 2)

    return {
        "total_monthly": round(total_monthly, 2),
        "total_yearly": round(total_yearly, 2),
        "item_count": len(detailed_list),
        "category_distribution": {k: round(v, 2) for k, v in category_totals.items()},
        "inflation_simulation": {
            "plus_25_percent": sim_zam_25,
            "plus_40_percent": sim_zam_40,
            "monthly_increase_at_25": round(sim_zam_25 - total_monthly, 2)
        },
        "items": detailed_list
    }
class CustomSubscriptionCreate(BaseModel):
    name:str
    price:float
    category:str

@app.post("/api/custom-subscriptions")
def create_custom_subscription(item:CustomSubscriptionCreate):
    return{
        "durum":"basarili",
        "isim":item.name,
        "fiyat":item.price,
        "kategori":item.category
    }
class InflationSimRequest(BaseModel):
    mevcut_tutar:float
    zam_yuzdesi:float=25.0
@app.post("/api/simulate-inflation")
def simulate_inflation(item:InflationSimRequest):
    fark=item.mevcut_tutar*(item.zam_yuzdesi/100)
    yeni_tutar=item.mevcut_tutar+fark
    return{
        "mevcut_tutar":round(item.mevcut_tutar, 2),
        "zam_yuzdesi":round(item.zam_yuzdesi, 2),
        "yeni_tutar":round(yeni_tutar, 2),
        "artis_miktari":round(fark, 2)
    }
class CancelSavingRequest(BaseModel):
    abonelik_adi:str
    aylik_tutar:float
    sure_ay:int=12
@app.post("/api/cancel-saving")
def calculate_cancellation_savings(item:CancelSavingRequest):
    toplam_tasarruf=item.aylik_tutar*item.sure_ay
    kahve_karsiliği=int(toplam_tasarruf/30)
    return{
        "abonelik_adi":item.abonelik_adi,
        "aylik_tutar":round(item.aylik_tutar, 2),
        "sure_ay":item.sure_ay,
        "toplam_tasarruf":round(toplam_tasarruf, 2),
        "kahve_karsiligi":kahve_karsiliği
    }
class NewServiceRequest(BaseModel):
    name:str
    category:str
    brand_color:str="#6366F1"
    icon_class:str="fa-solid fa-cube"
@app.post("/api/services/new")
def add_new_service(item:NewServiceRequest):
    conn=get_db()
    c=conn.cursor()
    slug=item.name.lower().replace(" ","-")
    c.execute("SELECT id FROM services WHERE slug = ?", (slug,))
    existing_service = c.fetchone()
    if existing_service:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"'{item.name}' servisi (slug: '{slug}') zaten sistemde kayıtlı!"
        )

    c.execute("""
        INSERT INTO services (slug,name,category,brand_color,icon_class)
        VALUES(?,?,?,?,?)
    """,(slug,item.name,item.category,item.brand_color,item.icon_class)
    )
    conn.commit()
    yeni_id=c.lastrowid
    conn.close()
    return{
        "durum":"basarili",
        "yeni_id":yeni_id,
        "slug":slug
    }        
class NewPlanRequest(BaseModel):
    service_id:int
    plan_name:str
    current_price:float
@app.post("/api/service-plans/new")
def add_new_plan(item: NewPlanRequest):
    conn = get_db()
    c = conn.cursor()
    
    # 1. Kontrol: Bu service_id veritabanında gerçekten var mı?
    c.execute("SELECT id FROM services WHERE id = ?", (item.service_id,))
    service = c.fetchone()
    
    if not service:
        conn.close()
        raise HTTPException(
            status_code=404, 
            detail=f"service_id={item.service_id} olan bir servis bulunamadı!"
        )
    
    # 2. Servis varsa planı güvenle ekle
    c.execute("""
        INSERT INTO service_plans (service_id, name, current_price, currency, billing_cycle)
        VALUES (?, ?, ?, ?, ?)
    """, (item.service_id, item.name, item.current_price, item.currency, item.billing_cycle))
    
    conn.commit()
    yeni_id = c.lastrowid
    conn.close()
    
    return {
        "durum": "basarili",
        "yeni_plan_id": yeni_id
    }

@app.delete("/api/service-plans/{plan_id}")
def delete_plan(plan_id:int):
    conn=get_db()
    c=conn.cursor()
    c.execute("DELETE FROM service_plans WHERE id=?",(plan_id,))
    conn.commit()
    silinen_adet = c.rowcount
    conn.close()
    if silinen_adet == 0:
        raise HTTPException(status_code=404, detail="Plan bulunamadi")
    return{
        "durum":"basarili",
        "silinen_plan_id":plan_id
    }
class UpdatePlanPriceRequest(BaseModel):
    new_price:float
@app.put("/api/service-plans/{plan_id}/update-price")
def update_plan_price(plan_id:int, item:UpdatePlanPriceRequest):
    conn=get_db()
    c=conn.cursor()
    c.execute("UPDATE service_plans SET current_price=? WHERE id=?",(item.new_price,plan_id))
    conn.commit()
    guncellenen_adet = c.rowcount
    conn.close()
    if guncellenen_adet == 0:
        raise HTTPException(status_code=404, detail="Plan bulunamadi")
    return{
        "durum":"basarili",
        "guncellenen_plan_id":plan_id,
        "yeni_fiyat":item.new_price
    }   

@app.get("/api/services/filter")
def filter_services(category: Optional[str] = None, search: Optional[str] = None):
    conn=get_db()
    c=conn.cursor()
    query="SELECT id,slug,name,category,brand_color,icon_class FROM services WHERE 1=1"
    params=[]
    if category:
        query+=" AND category=?"
        params.append(category)
    if search:
        query+=" AND name LIKE ?"
        params.append(f"%{search}%")
    c.execute(query, params)
    rows=c.fetchall()
    conn.close()
    sonuc=[]
    for row in rows:
        sonuc.append({
            "id":row["id"],
            "slug":row["slug"],
            "name":row["name"],
            "category":row["category"],
            "brand_color":row["brand_color"],
            "icon_class":row["icon_class"]
        })
    return sonuc
    
@app.get("/api/stats/summary")
def get_summary_stats():
    conn=get_db()
    c=conn.cursor()
    c.execute("SELECT COUNT(*) FROM services")
    total_services=c.fetchone()[0]
    c.execute("""
    SELECT COUNT(*) ,AVG(current_price),MIN(current_price),MAX(current_price) FROM service_plans
    """)
    plan_stats=c.fetchone()
    total_plans=plan_stats[0]
    avg_price=round(plan_stats[1],2)if plan_stats[1] is not None else 0.0
    min_price=round(plan_stats[2],2)if plan_stats[2] is not None else 0.0
    max_price=round(plan_stats[3],2)if plan_stats[3] is not None else 0.0
    conn.close()
    return{
        "toplam_servis":total_services,
        "toplam_plan":total_plans,
        "ortalama_plan_fiyati":avg_price,
        "en_dusuk_fiyat":min_price,
        "en_yuksek_fiyat":max_price
    }
@app.get("/api/stats/categories")
def get_category_stats():
    conn=get_db()
    c=conn.cursor()
    c.execute("""
    SELECT category,COUNT(*)as servis_sayisi FROM services GROUP BY category ORDER BY servis_sayisi DESC
    """)
    rows=c.fetchall()
    conn.close()
    sonuc=[]
    for row in rows:
        sonuc.append({
            "category":row["category"],
            "servis_sayisi":row["servis_sayisi"]
        })
    return sonuc
@app.get("/api/stats/categories-pricing")
def get_category_pricing_stats():
    conn=get_db()
    c=conn.cursor()
    c.execute("""
    SELECT s.category,COUNT(p.id)as toplam_plan,
    ROUND(AVG(p.current_price),2)as ortalama_fiyat
    FROM services s
    JOIN service_plans p ON s.id=p.service_id
    GROUP BY s.category
    ORDER BY ortalama_fiyat DESC
    """)
    rows=c.fetchall()
    conn.close()
    sonuc=[]
    for row in rows:
        sonuc.append({
            "category":row["category"],
            "toplam_plan":row["toplam_plan"],
            "ortalama_fiyat":row["ortalama_fiyat"]
        })
    return sonuc

class BatchPriceUpdate(BaseModel):
    percentage: float
    category: Optional[str] = None

@app.put("/api/service-plans/batch-update-price")
def batch_update_prices(data: BatchPriceUpdate):
    conn = get_db()
    c = conn.cursor()
    
    if data.category:
        query = """
            UPDATE service_plans 
            SET current_price = ROUND(current_price * (1 + ? / 100.0), 2)
            WHERE service_id IN (SELECT id FROM services WHERE category = ?)
        """
        c.execute(query, (data.percentage, data.category))
    else:
        query = """
            UPDATE service_plans 
            SET current_price = ROUND(current_price * (1 + ? / 100.0), 2)
        """
        c.execute(query, (data.percentage,))
    
    # DİKKAT: Buradan sonrası if/else'in dışında, def'in doğrudan içinde olmalı!
    affected_rows = c.rowcount
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "oran": f"%{data.percentage}",
        "kategori": data.category if data.category else "Tümü",
        "etkilenen_plan_sayisi": affected_rows
    }