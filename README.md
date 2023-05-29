# Sharex site
Antud projekt on valminud programmeerimise kvalifikatsioonikursuse lõputööna.  
  
Valminud on:
* [Veebileht](https://wxcoy.cc)
* SQL ühenduse haldaja
* HTML template failid
* API, POST ja GET routeid
* Frontend, mis on loodud mugavaks kasutamiseks 

#Eelvaade
###Sisselogimine, pealeht ja profiil
<img src="https://i.imgur.com/oUdn679.png"  height="300">
<img src="https://i.imgur.com/yn367lL.png"  height="300">
<img src="https://i.imgur.com/240MVd8.png"  height="300">

# Setup
1. Lae repo endale arvutisse alla
2. Lae alla MYSql server (näiteks [MYSql Workbench](https://www.mysql.com/products/workbench/) või [XAMPP](https://www.apachefriends.org/download.html))  
2.1. Jooksuta SQL server (XAMPPiga näide)  
![XAMPP preview](https://wxcoy.cc/fail/9a1db3d6-1c28-4c33-88e3-c70215474cbb)
![XAMPP preview](https://wxcoy.cc/fail/f6062a04-70ff-4383-a007-3a57aadbb3cb)  
2.2. Jäta serveri kasutaja info meelde või loo uus meelepärane kasutaja
3. Muuda andmebaasi kasutajaandmed vastavaks 'sql_config.json'-s  
4. Pane veebileht käima jooksutades faili 'website.py'  
4.1. Esimese (nö. admin) veebilehe kasutaja saab luua kutsega 'admin_kutse'   
4.2. Et kasutada ShareX-i, peate navigeerima lehele 'Profiil' ning alla laadima ShareX-i konfiguratsiooni  
![Profiil](https://wxcoy.cc/fail/83f68c84-41bf-4f89-8d8e-f7019b57d6f5)  
![ShareX konfiguratsioon](https://wxcoy.cc/fail/6eb779eb-f593-484a-9fa8-582869d78cb6)
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