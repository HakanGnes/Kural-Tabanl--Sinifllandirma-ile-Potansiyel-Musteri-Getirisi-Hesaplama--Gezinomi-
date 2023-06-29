#########################################################
# Kural Tabanlı Sınıflandırma ile Potansiyel Müşteri Getirisi Hesaplama (Gezinomi)
#########################################################



##########################################
# İş Problemi

# Gezinomi yaptığı satışların bazı özelliklerini kullanarak seviye tabanlı
# (level based) yeni satış tanımları oluşturmak ve bu yeni satış
# tanımlarına göre segmentler oluşturup bu segmentlere göre yeni
# gelebilecek müşterilerin şirkete ortalama ne kadar kazandırabileceğini
# tahmin etmek istemektedir.
# Örneğin:
# Antalya’dan Herşey Dahil bir otele yoğun bir dönemde gitmek isteyen
# bir müşterinin ortalama ne kadar kazandırabileceği belirlenmek
# isteniyor.
##########################################

#########################################
# Veri Seti Hikayesi

# Gezinomi_miuul.xlsx veri seti Gezinomi şirketinin yaptığı satışların fiyatlarını ve bu
# satışlara ait bilgiler içermektedir. Veri seti her satış işleminde oluşan kayıtlardan
# meydana gelmektedir. Bunun anlamı tablo tekilleştirilmemiştir. Diğer bir ifade ile
# müşteri birden fazla alışverişyapmış olabilir.
#########################################

#######################################
# Değişkenler

# SaleId: Satış id
# SaleDate : Satış Tarihi
# Price: Satış için ödenen fiyat
# ConceptName:Otel konsept bilgisi
# SaleCityName: Otelin bulunduğu şehir bilgisi
# CheckInDate: Müşterininotelegirişitarihi
# CInDay:Müşterinin otele giriş günü
# SaleCheckInDayDiff: Check in ile giriş tarihi gün farkı
# Season:Otele giriş tarihindeki sezon bilgisi
###########################################

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)

df = pd.read_excel("miuul_gezinomi.xlsx")
df.head()


# Görev 1: Aşağıdaki Soruları Yanıtlayınız.

# Soru1 : miuul_gezinomi.xlsx dosyasını okutunuz ve veri seti ile ilgili genel bilgileri gösteriniz.

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(head))
    print("##################### Tail #####################")
    print(dataframe.tail(head))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T)


check_df(df)

# Fiyat değişkeninde 13 adet boş değer bulunuyor.
# Bu çalışmada yeterli olacağını düşündüğüm için mean() ile o boş değerleri doldurabiliriz.

df["Price"].isnull().sum() # 13
df["Price"].fillna((df["Price"].mean()), inplace=True)
df["Price"].isnull().sum() # 0


# Soru 2 : Kaç unique şehir vardır? Frekansları nedir?

df["SaleCityName"].nunique()
df["SaleCityName"].value_counts()

# Soru 3 : Kaç unique Concept vardır?

df["ConceptName"].nunique()

# Soru 4 : Hangi Concept’den kaçar tane satış gerçekleşmiş?

df["ConceptName"].value_counts()

# Soru 5 : Şehirlere göre satışlardan toplam ne kadar kazanılmış?

df.groupby(["SaleCityName"]).agg({"Price":"sum"})

# Soru 6 : Concept türlerine göre göre ne kadar kazanılmış?

df.groupby(["ConceptName"]).agg({"Price":"sum"})

# Soru7: Şehirlere göre PRICE ortalamaları nedir?

df.groupby(["SaleCityName"]).agg({"Price":"mean"})

# Soru 8: Conceptlere göre PRICE ortalamaları nedir?

df.groupby(["ConceptName"]).agg({"Price":"mean"})

# Soru 9: Şehir-Concept kırılımında PRICE ortalamaları nedir?

df.groupby(["ConceptName", "SaleCityName"]).agg({"Price": "mean"})


# Görev 2 : SaleCheckInDayDiff değişkenini kategorik bir değişkene çeviriniz.
# SaleCheckInDayDiff değişkeni müşterinin CheckIn tarihinden ne kadar önce satin alımını tamamladığını gösterir.
# Aralıkları ikna edici şekilde oluşturunuz.
# Örneğin: ‘0_7’, ‘7_30', ‘30_90', ‘90_max’ aralıklarını kullanabilirsiniz.
# Bu aralıklar için "Last Minuters", "Potential Planners", "Planners", "Early Bookers“ isimlerini kullanabilirsiniz

df["SaleCheckInDayDiff"].nunique()
df["SaleCheckInDayDiff"].max()
intervals = [-1,7,30,90,630]
new_labels = ["Last_Minuters","Potential_Planners","Planners","Early_Bookers"]
df["EB_Score"] = pd.cut(df["SaleCheckInDayDiff"], intervals, labels=new_labels)
df.head()
df["EB_Score"].value_counts()

# Görev 3: Şehir-Concept-EB Score, Şehir-Concept- Sezon, Şehir-Concept-CInDay
# kırılımında ortalama ödenen ücret ve yapılan işlem sayısı cinsinden inceleyiniz ?

df.groupby(["SaleCityName", "ConceptName", "EB_Score"]).agg({"Price": ["mean","count"]})

# Görev 4: City-Concept-Season kırılımının çıktısını PRICE'a göre sıralayınız.

agg_df = df.groupby(["SaleCityName", "ConceptName", "Seasons"]).agg({"Price": "mean"}).sort_values("Price", ascending=False)

# Görev 5: Indekste yer alan isimleri değişken ismine çeviriniz.

agg_df.reset_index(inplace=True)
agg_df.head()


# Görev 6: Yeni seviye tabanlı müşterileri (persona) tanımlayınız.

# Yeni seviye tabanlı satışları tanımlayınız ve veri setine değişken olarak ekleyiniz.
# Yeni eklenecek değişkenin adı: sales_level_based
# Önceki soruda elde edeceğiniz çıktıdaki gözlemleri bir araya getirerek sales_level_based değişkenini oluşturmanız gerekmektedir.

agg_df["sales_level_based"] = agg_df[["SaleCityName", "ConceptName", "Seasons"]].agg(lambda x: "_".join(x).upper(), axis=1)
# agg_df = agg_df[["sales_level_based", "Price"]]
agg_df.head()

# Görev 7: Yeni müşterileri (personaları) segmentlere ayırınız.

# Yeni personaları PRICE’a göre 4 segmente ayırınız.
# Segmentleri SEGMENT isimlendirmesi ile değişken olarak agg_df’e ekleyiniz.
# Segmentleri betimleyiniz (Segmentlere göre group by yapıp price mean, max, sum’larını alınız).

agg_df["SEGMENT"] = pd.qcut(agg_df["Price"], 4, labels=["D", "C", "B", "A"])
agg_df.head()

agg_df.groupby("SEGMENT").agg({"Price": ["mean", "max", "sum"]})


# Görev 8: Yeni gelen müşterileri sınıflandırıp, ne kadar gelir getirebileceklerini tahmin ediniz.

# Antalya’da herşey dahil ve yüksek sezonda tatil yapmak isteyen bir kişinin ortalama ne kadar gelir kazandırması beklenir?

new_user = "ANTALYA_HERŞEY DAHIL_HIGH"
agg_df[agg_df["sales_level_based"] == new_user]

# Girne’de yarım pansiyon bir otele düşük sezonda giden bir tatilci hangi segmentte yer alacaktır?

new_user2 = "GIRNE_YARIM PANSIYON_LOW"
agg_df[agg_df["sales_level_based"] == new_user2]








