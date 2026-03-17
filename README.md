# Mancala
Mancala je jedna z nejstarších a nejoblíbenějších abstraktních strategických her pro dva hráče, často označovaná jako „kalaha“. Cílem hry je přerozdělovat kameny v jamkách na herní desce a nasbírat jich do své pokladnice co nejvíce
## O projektu
Projekt obsahuje hru v pygame, která je propojena s lokální databází. Výsledky se zobrazují na webu udělaném ve Flasku.
## Instalace a spuštění 
Doporučuje se spustit projekt ve virtuálním prostředí, aby nedocházelo k ovlivnění systémových knihoven.
1. **Vytvoření virtuálního prostředí:**
```bash
python -m venv venv
```
**Příkaz pro aktivaci**
```bash
.\venv\Scripts\activate
```
2. **Instalace potřebných knihoven**
```bash
pip install -r requirements.txt
```
3. **Spuštění serveru**
Ve složce `web` spusť:
```bash
python web_portal.py
```

Poté otevři prohlížeč na: http://127.0.0.1:5000


## Jak hrát
<p align="center">
<img src="/web/imgs/pravidla1.jpg" width="80%" height="60%">
<img src="/web/imgs/pravidla2.jpg" width="80%" height="60%">
</p>


## Licence

MIT
