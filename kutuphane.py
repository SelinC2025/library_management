from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from datetime import datetime
import sys
import json
import os

# ------------------ Kitap Sınıfı ------------------

class Kitap:
    def __init__(self, kitap_id, ad, yazar, mevcut_mu=True):
        self.__kitap_id = kitap_id
        self.__ad = ad
        self.__yazar = yazar
        self.__mevcut_mu = mevcut_mu

    def durum_guncelle(self, yeni_durum):
        self.__mevcut_mu = yeni_durum

    @staticmethod
    def kitap_ekle(kitaplar_dict, kitap_id, ad, yazar):
        if not kitap_id.strip() or not ad.strip() or not yazar.strip():
            QMessageBox.warning(None, "Eksik Bilgi", "Lütfen kitap ID, ad ve yazar bilgilerini eksiksiz giriniz!")
            return False

        if not kitap_id.isdigit():
            QMessageBox.warning(None, "Hata", "Kitap ID'si sadece rakamlardan oluşmalıdır!")
            return False

        if not yazar.replace(" ", "").isalpha():
            QMessageBox.warning(None, "Hata", "Yazar adı sadece harf ve boşluk içerebilir!")
            return False

        if kitap_id in kitaplar_dict:
            QMessageBox.warning(None, "Hata", "Bu ID'ye sahip bir kitap zaten var!")
            return False

        kitaplar_dict[kitap_id] = Kitap(kitap_id, ad, yazar)
        QMessageBox.information(None, "Başarılı", "Kitap başarıyla eklendi.")
        return True

    def kitap_bilgisi(self):
        durum = "Mevcut" if self.__mevcut_mu else "Ödünç Alınmış"
        return f"ID={self.__kitap_id}, Ad={self.__ad}, Yazar={self.__yazar}, Durum={durum}"

    def get_kitap_id(self):
        return self.__kitap_id

    def get_mevcut_mu(self):
        return self.__mevcut_mu


# ------------------ Üye Sınıfı ------------------

class Uye:
    def __init__(self, uye_id, ad):
        self.__uye_id = uye_id
        self.__ad = ad
        self.__odunc_kitaplar = []

    def kitap_odunc_al(self, kitap, odunc_listesi):
        if kitap.get_mevcut_mu():
            kitap.durum_guncelle(False)
            self.__odunc_kitaplar.append(kitap)
            odunc_olayi = Odunc(self, kitap)
            odunc_listesi.append(odunc_olayi)
            QMessageBox.information(None, "Başarılı", f"{self.__ad} şu kitabı ödünç aldı:\n{kitap.kitap_bilgisi()}")
            return True
        else:
            QMessageBox.warning(None, "Uyarı", "Bu kitap şu anda mevcut değil!")
            return False

    def kitap_iade_et(self, kitap):
        if kitap in self.__odunc_kitaplar:
            kitap.durum_guncelle(True)
            self.__odunc_kitaplar.remove(kitap)
            global odunc_listesi
            odunc_listesi = [odunc for odunc in odunc_listesi if not (odunc.uye == self and odunc.kitap == kitap)]
            QMessageBox.information(None, "İade", f"{self.__ad} şu kitabı iade etti:\n{kitap.kitap_bilgisi()}")
            return True
        else:
            QMessageBox.warning(None, "Hata", "Bu kitap sizde kayıtlı değil!")
            return False

    @staticmethod
    def uye_ekle(uyeler_dict, uye_id, ad):
        if not uye_id.strip() or not ad.strip():
            QMessageBox.warning(None, "Eksik Bilgi", "Lütfen üye ID ve adını eksiksiz giriniz!")
            return False

        if not uye_id.isdigit():
            QMessageBox.warning(None, "Hata", "Üye ID'si sadece rakamlardan oluşmalıdır!")
            return False

        if not ad.replace(" ", "").isalpha():
            QMessageBox.warning(None, "Hata", "Üye adı sadece harf ve boşluk içerebilir!")
            return False

        if uye_id in uyeler_dict:
            QMessageBox.warning(None, "Hata", "Bu ID'ye sahip bir üye zaten var!")
            return False

        uyeler_dict[uye_id] = Uye(uye_id, ad)
        QMessageBox.information(None, "Başarılı", "Üye başarıyla eklendi.")
        return True

    def uye_bilgisi(self):
        kitaplar = [k.kitap_bilgisi() for k in self.__odunc_kitaplar]
        kitaplar_str = "\n".join(kitaplar) if kitaplar else "Ödünç alınmış kitap yok."
        return f"Üye ID: {self.__uye_id}, Ad: {self.__ad}\nÖdünç Kitaplar:\n{kitaplar_str}"

    def get_uye_id(self):
        return self.__uye_id

    def get_odunc_kitaplar(self):
        return self.__odunc_kitaplar


# ------------------ Ödünç Sınıfı ------------------

class Odunc:
    def __init__(self, uye, kitap, tarih=None):
        self.uye = uye
        self.kitap = kitap
        self.tarih = datetime.now() if tarih is None else datetime.strptime(tarih, "%d.%m.%Y %H:%M")

    def odunc_bilgisi(self):
        return f"{self.uye.get_uye_id()} numaralı üye, {self.kitap.get_kitap_id()} numaralı kitabı {self.tarih.strftime('%d %B %Y, %H:%M')} tarihinde ödünç aldı."


# ------------------ JSON Veri İşlemleri ------------------

def verileri_yukle():
    global kitaplar, uyeler, odunc_listesi
    try:
        if os.path.exists("kitaplar.json"):
            with open("kitaplar.json", "r", encoding="utf-8") as f:
                kitap_data = json.load(f)
                kitaplar = {k["kitap_id"]: Kitap(k["kitap_id"], k["ad"], k["yazar"], k.get("mevcut_mu", True)) for k in kitap_data}

        if os.path.exists("uyeler.json"):
            with open("uyeler.json", "r", encoding="utf-8") as f:
                uye_data = json.load(f)
                uyeler = {u["uye_id"]: Uye(u["uye_id"], u["ad"]) for u in uye_data}

        if os.path.exists("odunc.json"):
            with open("odunc.json", "r", encoding="utf-8") as f:
                odunc_data = json.load(f)
                for o in odunc_data:
                    uye = uyeler.get(o["uye_id"])
                    kitap = kitaplar.get(o["kitap_id"])
                    if uye and kitap:
                        kitap.durum_guncelle(False)
                        uye.get_odunc_kitaplar().append(kitap)
                        odunc_listesi.append(Odunc(uye, kitap, o["tarih"]))
    except Exception as e:
        QMessageBox.warning(None, "Hata", f"Veri yükleme hatası: {str(e)}")


def verileri_kaydet():
    try:
        with open("kitaplar.json", "w", encoding="utf-8") as f:
            json.dump([{
                "kitap_id": k.get_kitap_id(),
                "ad": k._Kitap__ad,
                "yazar": k._Kitap__yazar,
                "mevcut_mu": k.get_mevcut_mu()
            } for k in kitaplar.values()], f, indent=4, ensure_ascii=False)

        with open("uyeler.json", "w", encoding="utf-8") as f:
            json.dump([{
                "uye_id": u.get_uye_id(),
                "ad": u._Uye__ad
            } for u in uyeler.values()], f, indent=4, ensure_ascii=False)

        with open("odunc.json", "w", encoding="utf-8") as f:
            json.dump([{
                "uye_id": o.uye.get_uye_id(),
                "kitap_id": o.kitap.get_kitap_id(),
                "tarih": o.tarih.strftime("%d.%m.%Y %H:%M")
            } for o in odunc_listesi], f, indent=4, ensure_ascii=False)
    except Exception as e:
        QMessageBox.warning(None, "Hata", f"Veri kaydetme hatası: {str(e)}")


# ------------------ Global Veri Tabanı ------------------

kitaplar = {}
uyeler = {}
odunc_listesi = []


# ------------------ Arayüz Sınıfı ------------------

class KutuphaneArayuz(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("kutuphane.ui", self)
        self.setWindowTitle("Kütüphane Yönetim Sistemi")
        verileri_yukle()

        self.pushButton.clicked.connect(self.kitap_ekle)
        self.pushButton_2.clicked.connect(self.kitap_odunc_al)
        self.pushButton_3.clicked.connect(self.uye_ekle)
        self.pushButton_4.clicked.connect(self.kitap_iade)
        self.pushButton_5.clicked.connect(self.kitap_bilgisi_goster)
        self.pushButton_6.clicked.connect(self.odunc_kitaplari_goster)
        self.pushButton_7.clicked.connect(self.uye_bilgisi_goster)

    def temizle_alanlar(self):
        self.lineEdit.clear()
        self.lineEdit_7.clear()
        self.lineEdit_6.clear()
        self.lineEdit_5.clear()
        self.lineEdit_4.clear()

    def kitap_ekle(self):
        kitap_id = self.lineEdit.text()
        ad = self.lineEdit_7.text()
        yazar = self.lineEdit_6.text()
        if Kitap.kitap_ekle(kitaplar, kitap_id, ad, yazar):
            verileri_kaydet()
            self.temizle_alanlar()

    def uye_ekle(self):
        uye_id = self.lineEdit_5.text()
        ad = self.lineEdit_4.text()
        if Uye.uye_ekle(uyeler, uye_id, ad):
            verileri_kaydet()
            self.temizle_alanlar()

    def kitap_odunc_al(self):
        uye_id = self.lineEdit_2.text().strip()
        kitap_id = self.lineEdit_3.text().strip()
        if not uye_id or not kitap_id:
            QMessageBox.warning(self, "Hata", "Üye ID ve Kitap ID alanları boş bırakılamaz!")
            return
        if uye_id not in uyeler or kitap_id not in kitaplar:
            QMessageBox.warning(self, "Hata", "Üye veya kitap bulunamadı!")
            return
        if not kitaplar[kitap_id].get_mevcut_mu():
            QMessageBox.warning(self, "Hata", "Bu kitap başka bir üyede!")
            return
        if uyeler[uye_id].kitap_odunc_al(kitaplar[kitap_id], odunc_listesi):
            verileri_kaydet()
            self.temizle_alanlar()

    def kitap_iade(self):
        uye_id = self.lineEdit_2.text().strip()
        kitap_id = self.lineEdit_3.text().strip()
        if not uye_id or not kitap_id:
            QMessageBox.warning(self, "Hata", "Üye ID ve Kitap ID alanları boş bırakılamaz!")
            return
        if uye_id not in uyeler or kitap_id not in kitaplar:
            QMessageBox.warning(self, "Hata", "Üye veya kitap bulunamadı!")
            return
        if kitaplar[kitap_id] not in uyeler[uye_id].get_odunc_kitaplar():
            QMessageBox.warning(self, "Hata", "Bu kitap bu üyede kayıtlı değil!")
            return
        if uyeler[uye_id].kitap_iade_et(kitaplar[kitap_id]):
            verileri_kaydet()
            self.temizle_alanlar()

    def kitap_bilgisi_goster(self):
        kitap_id = self.lineEdit.text()
        if not kitap_id:
            if kitaplar:
                bilgi = "Kütüphanedeki Tüm Kitaplar:\n\n" + "\n\n".join([k.kitap_bilgisi() for k in kitaplar.values()])
                QMessageBox.information(self, "Kitap Bilgileri", bilgi)
            else:
                QMessageBox.information(self, "Bilgi", "Kütüphanede kayıtlı kitap yok.")
        else:
            if kitap_id in kitaplar:
                QMessageBox.information(self, "Kitap Bilgisi", kitaplar[kitap_id].kitap_bilgisi())
            else:
                QMessageBox.warning(self, "Hata", "Kitap bulunamadı!")

    def uye_bilgisi_goster(self):
        uye_id = self.lineEdit_5.text()
        if not uye_id:
            if uyeler:
                bilgi = "Tüm Üyeler:\n\n" + "\n\n".join([u.uye_bilgisi() for u in uyeler.values()])
                QMessageBox.information(self, "Üye Bilgileri", bilgi)
            else:
                QMessageBox.information(self, "Bilgi", "Kayıtlı üye bulunmamaktadır.")
        else:
            if uye_id in uyeler:
                QMessageBox.information(self, "Üye Bilgisi", uyeler[uye_id].uye_bilgisi())
            else:
                QMessageBox.warning(self, "Hata", "Üye bulunamadı!")

    def odunc_kitaplari_goster(self):
        if odunc_listesi:
            mesaj = "Ödünç Alınan Kitaplar:\n\n" + "\n\n".join([o.odunc_bilgisi() for o in odunc_listesi])
            QMessageBox.information(self, "Ödünç Bilgileri", mesaj)
        else:
            QMessageBox.information(self, "Bilgi", "Henüz ödünç alınmış kitap yok.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = KutuphaneArayuz()
    pencere.show()
    sys.exit(app.exec_())
