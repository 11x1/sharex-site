# Sharex site
Antud projekt on valminud programmeerimise kvalifikatsioonikursuse lõputööna.  
  
Valminud on:
* SQL ühenduse haldaja
* HTML template failid
* API, POST ja GET routeid
* Frontend, mis on loodud mugavaks kasutamiseks 

# Setup
1. Lae repo endale arvutisse alla
2. Lae alla MYSql server (näiteks [MYSql Workbench](https://www.mysql.com/products/workbench/) või [XAMPP](https://www.apachefriends.org/download.html))  
2.1. Saa SQL server jooksma ning testi ühendust
2.2. Jäta serveri kasutaja info meelde või loo uus meelepärane kasutaja
3. Muuda andmebaasi kasutajaandmed vastavaks 'website.py'-s ridadel 15-18 (tbd kus täpselt, eraldi fail?) 
4. Pane veebileht käima jooksutades faili 'website.py'  
4.1. Registreeri ja logi sisse  
4.2. Vajuta nuppu 'Lae alla sharexi cfg'
5. Lae alla [ShareX](https://getsharex.com/downloads)  
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
6. Kõik on valmis! Saate luua ekraanipilte ja -videoid ShareX-iga ning need laetakse automaatselt üles.

# Todo
- [ ] Parem (eestikeelsem(?)) frontend
- [ ] Lihtsustatud andmebaasi sisselogimisandmete haldamine (ei pea website.py-d avama vaid eraldi failina)
- [ ] Muuta frontendi pildid sisselogimisel ja registreerimisel (praegu suvaline pilt [unsplashist](https://source.unsplash.com/featured/500x500))
- [ ] Võimalusel saada leht avalikult üles (nt. [PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/)) VÕI teha kõik see mida PythonAnywhere teeb aga ise wsgi ja nginx-iga