from collections import defaultdict, deque
import heapq
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional

# İstasyon sınıfı: Metro istasyonlarını temsil eder
class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        """İstasyon oluşturma.
        Args:
            idx: İstasyon ID.
            ad: İstasyon adı.
            hat: İstasyon hattı.
        """
        self.idx = idx  # İstasyon ID'si
        self.ad = ad  # İstasyon adı
        self.hat = hat  # İstasyon hattı
        self.komsular: List[Tuple['Istasyon', int]] = []  # Komşu istasyonlar ve seyahat süreleri

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        """İstasyona komşu ekleme.
        Args:
            istasyon: Komşu istasyon.
            sure: Seyahat süresi.
        """
        self.komsular.append((istasyon, sure))  # Komşuyu ve süreyi listeye ekle

# MetroAgi sınıfı: Metro ağını temsil eder
class MetroAgi:
    def __init__(self):
        """Metro ağı oluşturma."""
        # İstasyonları saklamak için sözlük (ID: İstasyon nesnesi)
        self.istasyonlar: Dict[str, Istasyon] = {}
        # Hatları saklamak için sözlük (Hat adı: İstasyon listesi)
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)
        # Ağı görselleştirmek için NetworkX grafiği
        self.graph = nx.Graph()

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        """Metro ağına istasyon ekleme.
        Args:
            idx: İstasyon ID.
            ad: İstasyon adı.
            hat: İstasyon hattı.
        """
        if idx not in self.istasyonlar:  # Aynı ID'de istasyon varsa ekleme
            istasyon = Istasyon(idx, ad, hat)  # Yeni istasyon oluştur
            self.istasyonlar[idx] = istasyon  # İstasyonu sözlüğe ekle
            self.hatlar[hat].append(istasyon)  # Hattı listeye ekle
            self.graph.add_node(idx, label=ad)  # Grafiğe düğüm ekle

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        """İki istasyon arasına bağlantı ekleme.
        Args:
            istasyon1_id: İlk istasyon ID.
            istasyon2_id: İkinci istasyon ID.
            sure: Seyahat süresi.
        """
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)  # İstasyonları komşu olarak ekle
        istasyon2.komsu_ekle(istasyon1, sure)  # Çift yönlü bağlantı
        self.graph.add_edge(istasyon1_id, istasyon2_id, weight=sure)  # Grafiğe kenar ekle

    # BFS algoritması: En az aktarmayla rotayı bulur
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        """En az aktarmayla rotayı bulan BFS algoritması.
        Args:
            baslangic_id: Başlangıç istasyonu ID.
            hedef_id: Hedef istasyonu ID.
        Returns:
            Rota (istasyon listesi).
        """
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        kuyruk = deque([(baslangic, [baslangic])])  # Kuyruk: (istasyon, rota)
        ziyaret_edildi = {baslangic}  # Ziyaret edilen istasyonlar
        while kuyruk:
            istasyon, rota = kuyruk.popleft()  # Kuyruktan istasyon al
            if istasyon == hedef:  # Hedefe ulaşıldıysa
                return rota
            for komsu, _ in istasyon.komsular:  # Komşuları dolaş
                if komsu not in ziyaret_edildi:  # Ziyaret edilmediyse
                    ziyaret_edildi.add(komsu)  # Ziyaret edildi olarak işaretle
                    kuyruk.append((komsu, rota + [komsu]))  # Kuyruğa ekle
        return None

    # A* algoritması: En hızlı rotayı bulur
    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        """En hızlı rotayı bulan A* algoritması.
        Args:
            baslangic_id: Başlangıç istasyonu ID.
            hedef_id: Hedef istasyonu ID.
        Returns:
            Rota (istasyon listesi) ve toplam süre.
        """
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        # Öncelik kuyruğu: (toplam süre, istasyon ID, istasyon, rota)
        pq = [(0, id(baslangic), baslangic, [baslangic])]
        ziyaret_edildi = set()
        while pq:
            toplam_sure, _, istasyon, rota = heapq.heappop(pq)  # En küçük süreli istasyonu al
            if istasyon == hedef:  # Hedefe ulaşıldıysa
                return (rota, toplam_sure)
            for komsu, sure in istasyon.komsular:  # Komşuları dolaş
                if komsu not in ziyaret_edildi:  # Ziyaret edilmediyse
                    ziyaret_edildi.add(komsu)  # Ziyaret edildi olarak işaretle
                    yeni_toplam_sure = toplam_sure + sure  # Yeni süreyi hesapla
                    pq.append((yeni_toplam_sure, id(komsu), komsu, rota + [komsu]))  # Kuyruğa ekle
                    heapq.heapify(pq)  # Öncelik kuyruğunu güncelle
        return None

    # Grafiksel görselleştirme
    def grafik_goster(self, rota: List[Istasyon]) -> None:
        """Metro ağını görselleştirme.
        Args:
            rota: Gösterilecek rota.
        """
        pos = nx.spring_layout(self.graph, seed=42, k=0.3)  # Düğüm pozisyonları
        labels = nx.get_node_attributes(self.graph, 'label')  # Düğüm etiketleri
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')  # Kenar etiketleri

        hat_renkleri = {  # Hat renkleri
            "Kırmızı Hat": "red",
            "Mavi Hat": "blue",
            "Turuncu Hat": "orange"
        }

        plt.figure(figsize=(12, 10))  # Boyut

        node_colors = []  # Düğüm renkleri
        for node in self.graph.nodes():
            istasyon = self.istasyonlar[node]
            hat_rengi = hat_renkleri.get(istasyon.hat, "gray")  # Hat rengi
            node_colors.append(hat_rengi)

        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color=node_colors, font_size=12, font_weight='bold', font_color='black', edge_color='gray')

        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=14, font_color='blue')  # Kenar etiketleri

        for node, (x, y) in pos.items():  # Düğüm etiketlerini hizala
            plt.text(x, y + 0.05, f"{labels[node]} ({node})", fontsize=10, ha='center', color='black')

        plt.title("Metro Durakları ve Mesafeler")
        plt.axis('off')
        plt.show()


# Örnek kullanım
if __name__ == "__main__":
    metro = MetroAgi()  # Metro ağı oluştur

    # İstasyonlar
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat")
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat")
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")

    # Bağlantılar
    metro.baglanti_ekle("K1", "K2", 4)
    metro.baglanti_ekle("K2", "K3", 6)
    metro.baglanti_ekle("K3", "K4", 8)
    metro.baglanti_ekle("M1", "M2", 5)
    metro.baglanti_ekle("M2", "M3", 3)
    metro.baglanti_ekle("M3", "M4", 4)
    metro.baglanti_ekle("T1", "T2", 7)
    metro.baglanti_ekle("T2", "T3", 9)
    metro.baglanti_ekle("T3", "T4", 5)
    metro.baglanti_ekle("K1", "M2", 2)
    metro.baglanti_ekle("K3", "T2", 3)
    metro.baglanti_ekle("M4", "T3", 2)

    # Test Senaryoları
    print("\n=== Test Senaryoları ===")

    # Senaryo 1: AŞTİ'den OSB'ye
    print("\n1. AŞTİ'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 2: Batıkent'ten Keçiören'e
    print("\n2. Batıkent'ten Keçiören'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 3: Keçiören'den AŞTİ'ye
    print("\n3. Keçiören'den AŞTİ'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 4: Ulus'tan Gar'a
    print("\n4. Ulus'tan Gar'a:")
    rota = metro.en_az_aktarma_bul("K2", "M4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("K2", "M4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 5: Kızılay'dan Batıkent'e
    print("\n5. Kızılay'dan Batıkent'e:")
    rota = metro.en_az_aktarma_bul("K1", "T1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("K1", "T1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 6: AŞTİ'den Keçiören'e
    print("\n6. AŞTİ'den Keçiören'e:")
    rota = metro.en_az_aktarma_bul("M1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("M1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 7: Demetevler'den Sıhhiye'ye
    print("\n7. Demetevler'den Sıhhiye'ye:")
    rota = metro.en_az_aktarma_bul("K3", "M3")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("K3", "M3")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Senaryo 8: Keçiören'den OSB'ye
    print("\n8. Keçiören'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("T4", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("T4", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    metro.grafik_goster(rota)
    
  

       



