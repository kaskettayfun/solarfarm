import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Sayfa Ayarları
st.set_page_config(page_title="Gelişmiş Solar Farm Simülasyonu", layout="wide")
st.title("☀️ Gelişmiş Güneş Tarlası Fizibilite Simülasyonu")
st.markdown("Panellerin teknik ve finansal parametrelerini değiştirerek sistem performansını, yatırım geri dönüşünü (ROI) ve çevresel etkiyi analiz edin.")

# --- YAN MENÜ: TEKNİK VE FİNANSAL PARAMETRELER ---
st.sidebar.header("🛠️ Teknik Parametreler")
panel_sayisi = st.sidebar.slider("Panel Sayısı (Adet)", min_value=50, max_value=2000, value=500, step=50)
panel_gucu = st.sidebar.slider("Birim Panel Gücü (Watt)", min_value=250, max_value=600, value=400, step=10)
panel_acisi = st.sidebar.slider("Panel Eğimi (Derece)", min_value=0, max_value=90, value=30, step=1)
hava_sicakligi = st.sidebar.slider("Ortalama Hava Sıcaklığı (°C)", min_value=-10, max_value=50, value=30, step=1)
sistem_kayiplari = st.sidebar.slider("Sistem Kayıpları (Toz, İnverter, Kablo) (%)", min_value=5, max_value=30, value=15, step=1)
guneslenme_suresi = st.sidebar.slider("Günlük Güneşlenme (Saat)", min_value=4.0, max_value=12.0, value=7.0, step=0.5)

st.sidebar.header("💰 Finansal Parametreler")
birim_maliyet = st.sidebar.number_input("Birim Panel Maliyeti ($)", value=150)
elektrik_fiyati = st.sidebar.number_input("Elektrik Satış Fiyatı ($/kWh)", value=0.12, format="%.3f")

# --- MÜHENDİSLİK VE FİNANS HESAPLAMALARI ---
OPTIMUM_ACI = 35 
SICAKLIK_KATSAYISI = -0.004 # 25°C üzerindeki her 1 derece için ortalama %0.4 verim kaybı

# Açı Kaybı
aci_farki = abs(OPTIMUM_ACI - panel_acisi)
aci_faktoru = math.cos(math.radians(aci_farki))

# Sıcaklık Kaybı (25 derece baz alınır)
sicaklik_farki = max(0, hava_sicakligi - 25)
sicaklik_faktoru = 1 + (sicaklik_farki * SICAKLIK_KATSAYISI)

# Üretim Hesaplamaları
ideal_guc_kW = (panel_sayisi * panel_gucu) / 1000
gercek_guc_kW = ideal_guc_kW * aci_faktoru * sicaklik_faktoru * (1 - sistem_kayiplari/100)

gunluk_uretim_kWh = gercek_guc_kW * guneslenme_suresi
yillik_uretim_kWh = gunluk_uretim_kWh * 365

# Finansal ve Çevresel Metrikler
toplam_yatirim = panel_sayisi * birim_maliyet
yillik_gelir = yillik_uretim_kWh * elektrik_fiyati
amortisman_yili = toplam_yatirim / yillik_gelir if yillik_gelir > 0 else 0
# Türkiye şebekesi için yaklaşık 1 kWh = 0.45 kg CO2 emisyonu engeller
engellenen_co2_ton = (yillik_uretim_kWh * 0.45) / 1000 
gerekli_arazi_m2 = panel_sayisi * 2.5 # Panel başı kapladığı alan + boşluklar

# --- EKRAN ÇIKTILARI (DASHBOARD) ---
st.subheader("📊 Fizibilite ve Üretim Sonuçları")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Kurulu İdeal Güç", f"{ideal_guc_kW:.1f} kW")
c2.metric("Gerçek Üretim Kapasitesi", f"{gercek_guc_kW:.1f} kW", delta=f"%{int((gercek_guc_kW/ideal_guc_kW)*100)} Verim", delta_color="normal")
c3.metric("Gerekli Arazi Alanı", f"{gerekli_arazi_m2:,.0f} m²")
c4.metric("Engellenen CO2 (Yıllık)", f"{engellenen_co2_ton:.1f} Ton 🌱")

st.markdown("---")

c5, c6, c7 = st.columns(3)
c5.metric("Toplam İlk Yatırım", f"${toplam_yatirim:,.0f}")
c6.metric("Yıllık Tahmini Gelir", f"${yillik_gelir:,.0f}")
c7.metric("Amortisman (ROI) Süresi", f"{amortisman_yili:.1f} Yıl")

# --- AMORTİSMAN (ROI) GRAFİĞİ ---
st.subheader("📈 20 Yıllık Nakit Akışı ve Amortisman Projeksiyonu")
yillar = np.arange(0, 21)
nakit_akisi = -toplam_yatirim + (yillar * yillik_gelir)

fig, ax = plt.subplots(figsize=(10, 3))
fig.patch.set_facecolor('#0e1117')
ax.set_facecolor('#0e1117')

ax.plot(yillar, nakit_akisi, color='#2ca02c', marker='o', linewidth=2, label="Net Nakit Akışı ($)")
ax.axhline(0, color='red', linestyle='--', linewidth=1) # Sıfır noktası (Amortisman anı)
ax.fill_between(yillar, nakit_akisi, 0, where=(nakit_akisi >= 0), facecolor='#2ca02c', alpha=0.3)
ax.fill_between(yillar, nakit_akisi, 0, where=(nakit_akisi < 0), facecolor='red', alpha=0.3)

ax.set_title("Yıllara Göre Kümülatif Kazanç / Zarar", color='white')
ax.set_xlabel("Yıl", color='white')
ax.set_ylabel("Dolar ($)", color='white')
ax.tick_params(colors='white')
ax.grid(color='gray', linestyle=':', alpha=0.5)

st.pyplot(fig)