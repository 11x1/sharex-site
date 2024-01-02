# Sharex site
Antud projekt on valminud programmeerimise kvalifikatsioonikursuse lõputööna. Eestikeelsed muutujad on tingitud Tartu Ülikooli kvalifikatsioonikursuse lõputöö nõuetest.   
  
Valminud on:
* Veebileht
* SQL ühenduse haldaja
* HTML template failid
* API, POST ja GET routeid
* Frontend, mis on loodud mugavaks kasutamiseks 

# Eelvaade  
### Sisselogimine, pealeht ja profiil  
<img src="https://i.imgur.com/oUdn679.png"  height="300">
<img src="https://i.imgur.com/yn367lL.png"  height="300">
<img src="https://i.imgur.com/240MVd8.png"  height="300">

# Setup
1. Lae repo endale arvutisse alla
2. Lae alla MYSql server (näiteks [MYSql Workbench](https://www.mysql.com/products/workbench/) või [XAMPP](https://www.apachefriends.org/download.html))  
2.1. Jooksuta SQL server (XAMPPiga näide)  
![XAMPP preview](https://i.imgur.com/CDKynx2.png)
![XAMPP preview](https://i.imgur.com/wm3qjCI.png)  
2.2. Jäta serveri kasutaja info meelde või loo uus meelepärane kasutaja
3. Muuda andmebaasi kasutajaandmed vastavaks 'sql_config.json'-s  
4. Pane veebileht käima jooksutades faili 'website.py'  
4.1. Esimese (nö. admin) veebilehe kasutaja saab luua kutsega 'admin_kutse'   
4.2. Et kasutada ShareX-i, peate navigeerima lehele 'Profiil' ning alla laadima ShareX-i konfiguratsiooni  
![Profiil](https://i.imgur.com/9iaEOvW.png)  
![ShareX konfiguratsioon](https://i.imgur.com/s70ogxA.png)
5. Laadige alla [ShareX](https://getsharex.com/downloads)  
5.1. Ava ShareX ja navigeeri vasakul navigatsiooniribal nupule 'Destinations' ning vajuta seda  
![pilt](https://i.imgur.com/4QxbNKD.png)
5.2. Hüpikaknas navigeeri edasi nupule 'Custom uploader settings' ning vajuta sellele  
![pilt](https://i.imgur.com/A6Umvcg.png)
5.3. Uues hüpikaknas vajutake lehe vasaku serva keskel nupule 'Import' ning valike rippmenüüst 'From file'  
![pilt](https://i.imgur.com/UoFXQup.png)
5.4. Avage hüpikaknas (failinavigeerijas) oma allalaetud fail ('config.sxcu')  
![pilt](https://i.imgur.com/lIJkjGx.png)  
5.5. Navigeerige tagasi nupule 'Destinations' ning klõpsake valikul 'Image uploader'  
5.6. Rippmenüüst valige 'Custom image uploader'  
![pilt](https://i.imgur.com/Gywhueg.png)
6. Kõik on valmis! Saate luua ekraanipilte ja -videoid ShareX-iga ning need laetakse automaatselt üles (tavaline klahvikombinatsioon Ctrl+Prtsc).

# Todo
- [x] Parem (eestikeelsem(?)) frontend
- [x] Lihtsustatud andmebaasi sisselogimisandmete haldamine (ei pea website.py-d avama vaid eraldi failina)
- [x] Muuta frontendi pildid sisselogimisel ja registreerimisel (praegu suvaline pilt [unsplashist](https://source.unsplash.com/featured/500x500))
- [x] Võimalusel saada leht avalikult üles (nt. [PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/)) VÕI teha kõik see mida PythonAnywhere teeb aga ise wsgi ja nginx-iga
