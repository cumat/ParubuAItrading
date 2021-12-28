import time
from pathlib import Path
from selenium import webdriver
from datetime import datetime
import pyautogui
import threading

driver_path = Path("C:\\seleniumbrowserdriver\\chromedriver.exe")
user_data_dir = Path("C:\\Users\\cumat\\AppData\\Local\\Google\\Chrome\\User Data")

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(executable_path=driver_path, options=options)
driver.maximize_window()

alinan_Birim_Degeri = 0
alinan_Birim_Miktari = 0
satilan_Birim_Miktari = 0
satilan_Birim_Degeri = 0
toplamKazac = 0
baslangic_Fiyat = 300
hataKontrol = 0
beklemeSayim = 0
alSatKontrol = True

# Satiş trade panelini açar
def satisTradePanel():
    global hataKontrol
    try:
        tradeFormSell = driver.find_element_by_xpath("//*[@id='app']/div[1]/div[1]/div[2]/div/div[1]/div[1]/div/div[1]/div[2]/div/a[2]")
        tradeFormSell.click()
    except Exception as e:
        print(f"Paneli açarken hata aldık\nHata: {e}")
        if hataKontrol == 8: exit()
        hataKontrol +=1
        driver.refresh()
        time.sleep(3)
        satisTradePanel()

# Alım trade panelini açar
def alimTradePanel():
    global hataKontrol
    try:
        driver.find_element_by_css_selector("a[href='#tradeFormBuy']").click()
    except Exception as e:
        print(f"Paneli açarken hata aldık\nHata: {e}")
        if hataKontrol == 8: exit()
        hataKontrol +=1
        driver.refresh()
        time.sleep(3)
        alimTradePanel()

def alim_Kontrol():
    global beklemeSayim
    global alSatKontrol
    print(f"Al-Sat Toplam kâr: {toplamKazac}TL")
    print(f"anlik satiş kontrol : {anlikSatisMiktarKontrol()} | satilan birim değeri: {satilan_Birim_Degeri}")
    #Genel kazanç durumunda zarar  belirlenen tutarın altına düştü ise programı kapatıyoruz.
    if toplamKazac < -20:
        print(f"Çok zarardayız, bot durduruluyor...\nZarar: {toplamKazac}")
        exit()
    anlikSatKontrol = anlikSatisMiktarKontrol() # anlık satılan kriptonun değeri
    kontrol_Satilan_Birim_Degeri = satilan_Birim_Degeri + ((satilan_Birim_Degeri/100)*5) # tekrar satın almadan önce sattığımız miktarın %2ini alıp aşşağıda anlık miktardan aşşağıdamı kontrol ediyoruz.
    anlikSatisTl = anlikSatKontrol*satilan_Birim_Miktari # son saatığımız miktar ile anlık kaç tlye denk geliyor ona bakıyoruz
    satilanMiktarTL = satilan_Birim_Degeri*satilan_Birim_Miktari # son miktar ve değerle kaç tlye sattık onu buluyoz.
    fark = anlikSatisTl < (satilanMiktarTL + ((satilanMiktarTL/100)*7)) # sattığımız TL ile anlık miktar arasında %7 ve daha üstünde fark var ise yükselişe geçtiği için al
    print(f"Fark:{fark}")
    print(f"anlıkSatKontrol: {anlikSatKontrol} | kontrolSatilanBirim: {kontrol_Satilan_Birim_Degeri}")
    if beklemeSayim >= 45: # her ?(3) saatte bir tutar ne olursa olsun alım yapar
        beklemeSayim = 0
        print("Alsat True yapıldı")
        return 'sat'
    # sattıktan sonra anlık satış tutarı sattığım değerin altına düşerse al veya yükselişe geçerek fark %7den yukardaysa al
    if anlikSatKontrol < kontrol_Satilan_Birim_Degeri:
        print("Crypto alınan değerin altına düştü")
        beklemeSayim = 0
        return True
    else:
        beklemeSayim += 1
        return False

def satis_Kontrol():
    satilan_TL= int(anlikAlimMiktarKontrol()*alinan_Birim_Miktari)
    alinan_TL = int(alinan_Birim_Degeri*alinan_Birim_Miktari)
    print(f"Satilan tl : {satilan_TL} | alinan TL : {alinan_TL} ")
    sonuc = satilan_TL - alinan_TL
    return int(sonuc)
    # ilk_alinanDeger_TL = int(alinan_Birim_Miktari * alinan_Birim_Degeri)
    # son_Satis_Tl = satilanMikariBul(anlikSatisMiktarKontrol(), alinan_Birim_Miktari)
    # print(f"Kontrol | {ilk_alinanDeger_TL}'TLye alındı - {son_Satis_Tl}'TLye satıldı")
    # kazanc = son_Satis_Tl - ilk_alinanDeger_TL
    # return int(kazanc)

#Anlık cripto birim fiyatı ile tutarı(100) hesaplayarak kaç birim aldığını hesaplar ve döndürü.
def alinanMikariBul(alinan_Deger,tutar=baslangic_Fiyat):
    return int(tutar/alinan_Deger)

#Anlık cripto birim fiyatı ile elindeki birimi hesaplayarak kaç TL olduğunu bulup döndürür.
def satilanMikariBul(satilan_Deger,satilan_Adet):
    return int(satilan_Deger*satilan_Adet)
    # birim_Adet = float(birim_Adet.replace(',','.'))
    # print(f"Satış miktar bul = anlık satış tutar: {anlik_Satis_Tutari} | birim adet: {birim_Adet}")

#Satın alırken anlık satılan kripto değerini kontrol eder, alınan değer değişkeninde tutar ve döndürür
def anlikSatisMiktarKontrol():
    global hataKontrol
    global alinan_Deger
    try:
        buy_cryp_price = driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/div[2]/div/div[2]/div/div[3]/div[3]/div/div[2]/div/span/div[1]/div/span[1]').text
        # print(f"Satılan Criypto anlık fiyat:  {buy_cryp_price}")  # Alınacak   olan cryptonun  fiyatı
        buy_cryp_price = float(buy_cryp_price.replace(',', '.'))
        alinan_Deger = buy_cryp_price
    except Exception as e:
        print("Satın alırken anlık miktar kontrol edilemedi\nSayfa yenileniyor...")
        print(e)
        if hataKontrol == 8: exit()
        hataKontrol +=1
        driver.refresh()
        time.sleep(3)
        anlikSatisMiktarKontrol()
    return alinan_Deger

#Satış yaparken anlık kripto tutarını kontrol eder ve döndürür
def anlikAlimMiktarKontrol():
    global hataKontrol
    global cryfyt
    try:
        cryfyt = driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/div[2]/div/div[2]/div/div[3]/div[2]/div/div[2]/div/span/div[1]/div/span[1]').text
        cryfyt = float(cryfyt.replace(',','.'))
        # print(f"Alınan Criypto anlık fiyat:  {cryfyt}")  # satılacak  olan cryptonun  birim tutarı
    except Exception as e:
        print("Fiyat alınamadı\nSayfa yenileniyor...")
        print(e)
        if hataKontrol == 8:exit()
        hataKontrol += 1
        driver.refresh()
        time.sleep(5)
        anlikAlimMiktarKontrol()
    return cryfyt

#Satış panelini açar ve tüm birimi anlık miktar ile satar. Satılan miktarın Tl karşılığını döndürür.
def sellCrypto():
    global hataKontrol
    global satilan_Birim_Miktari
    global satilan_Birim_Degeri
    global baslangic_Fiyat
    time.sleep(1)
    satisTradePanel()
    sell = driver.find_element_by_css_selector("div[id='tradeFormSell']")
    satilan_Birim_Tutari = anlikAlimMiktarKontrol()
    print(f"Satılan Criypto anlık fiyat:  {satilan_Birim_Tutari}")  # Alınacak   olan cryptonun  fiyatı
    try:
        time.sleep(0.5)
        driver.find_element_by_xpath('//*[@id="tradeFormSell"]/div/div[2]/form/div[1]/div/div/div[1]/div[2]/div/span[1]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath('//*[@id="tradeFormSell"]/div/div[2]/form/div[2]/div/div/div[1]/div[2]/div/span[1]').click()
        time.sleep(0.5)
        sell.find_element_by_css_selector("button[type='submit']").click()  # Satis button
        time.sleep(2)
        alimTradePanel()
        # pyautogui.hotkey('esc')
    except Exception:
        print("Input Error\nSayfa yenileniyor...")
        if hataKontrol == 5: exit()
        hataKontrol += 1
        driver.refresh()
        time.sleep(5)
    satilan_Birim_Miktari = alinan_Birim_Miktari
    satilan_Birim_Degeri = satilan_Birim_Tutari
    kazanilan_Tutar = int(satilan_Birim_Tutari*alinan_Birim_Miktari)
    baslangic_Fiyat = kazanilan_Tutar
    print(f"{satilan_Birim_Tutari} birim fiyatına {alinan_Birim_Miktari} adet satılarak {kazanilan_Tutar} TL kazanıldı")
    return True

#Alış panelini açar ve belirlenen tutar(100) ile anlık birim fiyatına crypto alır.
#Alınan birim miktarını hesaplar ve global değişkene aktarır.
def buyCrypto(al=baslangic_Fiyat):
    fyt = al
    global alinan_Birim_Miktari
    global alinan_Birim_Degeri
    global hataKontrol
    alimTradePanel()
    tradeFormBuy = driver.find_element_by_css_selector("div[id='tradeFormBuy']")
    time.sleep(1)
    # tst = anlikSatisMiktarKontrol()
    # kontrol = float(tst[:7]) #String olarak döndürüyor vce son virgülden sonra ayırmamız gerekiyor, ayırıp floata çevirdim
    kont = anlikSatisMiktarKontrol()
    alinan_Birim_Miktari = int(baslangic_Fiyat/kont) #alınan birimim birim başı fiyat ile tutarı hesaplar ve kaç birim olduğunu hesaplar.
    alinan_Birim_Degeri = kont
    fyt = baslangic_Fiyat if fyt >= baslangic_Fiyat  else (baslangic_Fiyat + toplamKazac)
    try:
        tradeFormBuy.find_element_by_css_selector("input[id^='input-']").send_keys(str(kont))
        # tradeFormBuy.find_element_by_xpath('//*[@id="tradeFormBuy"]/div/div[2]/form/div[1]/div/div/div[1]/div[2]/div/span[1]').click()
        # time.sleep(0.1)
        # pyautogui.press('tab')
        # time.sleep(0.1)
        # pyautogui.press('tab')
        # time.sleep(0.1)
        # pyautogui.write(str(fyt), 0.01)
        # time.sleep(0.1)
        toplamButton = tradeFormBuy.find_element_by_xpath('/html/body/div/div[1]/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div/div[2]/form/div[3]/div/div/div[1]/div[1]/input')
        toplamButton.send_keys(str(fyt))
        tradeFormBuy.find_element_by_css_selector("button[type='submit']").click()  # Alis button
        time.sleep(2)
        satisTradePanel()
    except Exception as e:
        print(f"Hata: {e}")
        print("Input Error")
        exit()

    print(f"{fyt}TL'ye {alinan_Birim_Degeri}'den {alinan_Birim_Miktari} adet alındı...")
    return False

def changeCrypto(cry):
    driver.get(f"https://www.paribu.com/#/market/{str(cry)}-tl")
    print(f"Cryto Changed --> {cry} ")
    time.sleep(0.1)

def main():
    global alSatKontrol
    global toplamKazac
    global beklemeSayim
    global driver
    driver.get("https://www.paribu.com/#/")
    # driver.find_element_by_css_selector("a[href='#/wallet/']").click()
    driver.find_element_by_css_selector("a[href='#/market/btc-tl']").click()
    time.sleep(2)
    # ------------  Change the Cripto ------------
    changeCrypto("reef")
    time.sleep(3)
    alSatKontrol = buyCrypto()  # kripto alır ve False değer döndürür
    try:
        while True:
            time.sleep(240)
            current_time = datetime.now().strftime("%H:%M:%S")
            driver.refresh()
            time.sleep(3)
            if alSatKontrol:
                print("---------------------------- Alım İşlem Kontrol ----------------------------")
                print(f"Zaman: {current_time}")
                karar = alim_Kontrol()
                if karar:
                    alSatKontrol = buyCrypto()  # kripto alır ve False değer döndürür
                elif karar == 'sat':
                    alSatKontrol = True
            else:
                print("---------------------------- Satış İşlem Kontrol ----------------------------")
                print(f"Zaman: {current_time}")
                satisTradePanel()  # satışı kontrol ederken sayda yenilendikten sonra satış panelini açarak bekler
                print(f"{alinan_Birim_Degeri} değeriyle {alinan_Birim_Miktari} adet birim alınmıştı")
                print(
                    f"Şuan Değer: {anlikAlimMiktarKontrol()}\nBu değerden {alinan_Birim_Miktari} alınan  adet {(anlikAlimMiktarKontrol() * alinan_Birim_Miktari)}TL eder")
                karar = satis_Kontrol()
                print(f"Kâr - Zarar Durumu: {karar}")
                print(f"Al-Sat Toplam kâr: {toplamKazac}TL")
                # beklemeSayim += 1
                # if beklemeSayim == 3: karar = 2
                if karar >= 2:
                    # beklemeSayim = 2
                    alSatKontrol = sellCrypto()  # satış işlemini yapar ve True değer döndürür
                    toplamKazac += karar
    except Exception as e:
        print(f"Main Hatası\nHata:{e}")
        print("Tarayıcı kapatılıp açılacak!")
        driver.close()
        time.sleep(5)
        print("Tarayıcı tekrardan açılıyor...")
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
        driver.maximize_window()
        main()

if __name__ == "__main__":
    main()


"""
# ------------------ Cryptolar ------------------ 

Bitcoin    : btc
Tether     : usdt
Chiliz     : chz
RavenCoin  : rvn
Ethereum   : eth
Waves      : waves
Bittorent  : btt
Holo       : hot
Stellar    : Xlm
Reef       : reef
Ripple     : xrp
Cardano    : ada
Neo        : neo
Bat        : bat
Tron       : trx
Litecoin   : ltc
Avalanche  : avax
BitcoinCash: bhc

  ---------- SATIS ----------
Fiyat = <input id = "input-224"> | <input id = "input-76">  tradeFormBuy.find_element_by_css_selector("input[id='input-224']").send_keys(300)
Miktar = <input id = "input-?">
Toplam TL = <input id = "input-233"> | <input id = "input-85"> 

  ---------- ALIS ----------
Fiyat = <input id = "input-101"> | <input id = "input-249"> | 265  tradeFormBuy.find_element_by_css_selector("input[id='input-101']").send_keys(300)
Miktar = <input id = "input-106"> | <input id = "input-254"> | 270
Toplam TL = <input id = "input-111"> | <input id = "input-259"> 275
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# print(soup.prettify())
"""
