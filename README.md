# Restorano Valdymo Sistema

**Autorius:** [Jaromir Koženevski]  
**Studijų programa:** [EDIf25/1]  
**Akademiniai metai:** 2025–2026  
**Kursinis darbas:** Objektinis Programavimas (OOP)

---

## Turinys

1. [Įvadas](#1-įvadas)
2. [Analizė ir įgyvendinimas](#2-analizė-ir-įgyvendinimas)
3. [Rezultatai ir išvados](#3-rezultatai-ir-išvados)
4. [Naudoti šaltiniai](#4-naudoti-šaltiniai)

---

## 1. Įvadas

### Kas yra ši programa?

Restorano Valdymo Sistema yra konsolės programa, skirta valdyti restorano veiklą. Sistema leidžia:

- Peržiūrėti ir valdyti restorano **meniu** (maisto ir gėrimų sąrašas)
- Stebėti **staliukų** užimtumą
- Priimti ir valdyti **užsakymus**
- Generuoti **sąskaitas** su PVM
- Skaičiuoti **dienos pajamas**
- **Saugoti** ir **nuskaityti** duomenis iš CSV failų

### Kaip paleisti programą?

**Reikalavimai:** Python 3.8+

```bash

git clone https://github.com/[vardas]/restaurant-management.git
cd restaurant-management


python main.py


python -m pytest test_restaurant.py -v
# arba
python test_restaurant.py
```

### Kaip naudotis programa?

Paleidus programą, pasirodo pagrindinis meniu su skaičiais (0–9). Tipiška darbo eiga:

1. Pasirink `1` → peržiūrėk meniu
2. Pasirink `3` → sukurk užsakymą staliukui (pvz. staliukas nr. 1)
3. Pasirink `4` → pridėk patiekalus prie užsakymo
4. Pasirink `5` → peržiūrėk sąskaitą
5. Pasirink `6` → apmokėk ir atlaisvink staliuką

---

## 2. Analizė ir įgyvendinimas

### 2.1 OOP 4 pagrindiniai principai

#### 1. Inkapsuliacija (Encapsulation)

Inkapsuliacija – tai duomenų slėpimas klasės viduje. Atributai žymimi `__` (privatus) arba `_` (apsaugotas), o prieiga prie jų – per `@property` dekoratorius.

```python
class Order:
    def __init__(self, order_id: int, table_number: int):
        self.__order_id = order_id       
        self.__is_paid = False           

    @property
    def order_id(self):
        return self.__order_id          

    @property
    def is_paid(self):
        return self.__is_paid

    def mark_as_paid(self):
        self.__is_paid = True            
```

Taip užtikrinama, kad `__is_paid` negalima pakeisti tiesiogiai iš išorės – tik per `mark_as_paid()` metodą.

---

#### 2. Paveldėjimas (Inheritance)

`Food` ir `Drink` klasės paveldi iš abstrakčios `MenuItem` bazinės klasės. Jos perima visus bazinės klasės atributus ir metodus.

```python
class MenuItem(ABC):              
    def __init__(self, item_id, name, price):
        self._name = name
        self._price = price

class Food(MenuItem):             
    def __init__(self, item_id, name, price, category):
        super().__init__(item_id, name, price) 
        self._category = category

class Drink(MenuItem):            
    def __init__(self, item_id, name, price, is_alcoholic=False):
        super().__init__(item_id, name, price)
        self._is_alcoholic = is_alcoholic
```

---

#### 3. Polimorfizmas (Polymorphism)

`display()` metodas įgyvendinamas skirtingai `Food` ir `Drink` klasėse – tas pats metodo pavadinimas, bet skirtingas elgesys.

```python
class Food(MenuItem):
    def display(self) -> str:
        return f"[MAISTAS] {self._name} ({self._category}) - €{self._price:.2f}"

class Drink(MenuItem):
    def display(self) -> str:
        tipas = "Alkoholinis" if self._is_alcoholic else "Nealkoholinis"
        return f"[GERIMAS] {self._name} ({tipas}) - €{self._price:.2f}"
```

Praktinis naudojimas – galima kviesti `display()` bet kuriam `MenuItem` objektui:

```python
for item in menu:
    print(item.display())  
```

---

#### 4. Abstrakcija (Abstraction)

`MenuItem` yra abstrakti klasė (naudoja `ABC`). Negali sukurti `MenuItem` objekto tiesiogiai – tik per subklases.

```python
from abc import ABC, abstractmethod

class MenuItem(ABC):
    @abstractmethod
    def display(self) -> str:
        pass  


food = Food("F01", "Cepelinai", 8.50, "Pagrindinis")
```

---

### 2.2 Dizaino šablonas – Singleton

**Singleton** šablonas užtikrina, kad egzistuoja tik VIENAS `Restaurant` klasės objektas. Tai logiška – fiziškai restoranas yra vienas.

```python
class Restaurant:
    _instance = None  

    def __new__(cls, name="Mano Restoranas"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  
        return cls._instance  
```

Kodėl Singleton yra tinkamiausias šiam atvejui:

- Restoranui nereikia kelių instancijų – tai vienas centralizuotas valdiklis
- Visi meniu, staliukai ir užsakymai valdomi per vieną objektą
- Factory šablonas būtų per sudėtingas paprastai valdymo sistemai

---

### 2.3 Kompozicija ir Agregacija

**Kompozicija** – `Order` klasė saugo `MenuItem` objektų sąrašą. Jei `Order` ištrinamas, jo items taip pat ištrinami.

```python
class Order:
    def __init__(self, order_id, table_number):
        self.__items = []  

    def add_item(self, item: MenuItem, quantity: int = 1):
        self.__items.append((item, quantity))
```

**Agregacija** – `Table` klasė turi *nuorodą* į `Order` objektą, bet `Order` egzistuoja nepriklausomai (saugomas `Restaurant` sąraše).

```python
class Table:
    def __init__(self, table_number, capacity):
        self.__current_order = None  

    def assign_order(self, order: Order):
        self.__current_order = order  

    def clear_table(self):
        self.__current_order = None  
```

---

### 2.4 Failų skaitymas ir rašymas

Programa naudoja **CSV** formato failus duomenų saugojimui.

**Meniu rašymas į failą:**

```python
def save_menu_to_csv(self, filename="menu.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "type", "name", "price", "extra"])
        for item in self.__menu:
            if isinstance(item, Food):
                writer.writerow([item.item_id, "food", item.name,
                                  item.price, item.category])
```

**Meniu skaitymas iš failo:**

```python
def load_menu_from_csv(self, filename="menu.csv"):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "food":
                item = Food(row["id"], row["name"],
                            float(row["price"]), row["extra"])
            self.__menu.append(item)
```

Taip pat rašomi `orders.csv` failai su visų užsakymų istorija.

---

### 2.5 Testavimas

Programos branduolinė logika dengta `unittest` testais. Testuojamos klasės: `Food`, `Drink`, `Order`, `Table`, `Restaurant`.

```python
class TestOrder(unittest.TestCase):
    def setUp(self):
        self.order = Order(1, 3)
        self.food = Food("F01", "Cepelinai", 8.50, "Pagrindinis")

    def test_total_calculation(self):
        self.order.add_item(self.food, 2)  
        self.assertAlmostEqual(self.order.get_total(), 17.00, places=2)

    def test_mark_as_paid(self):
        self.assertFalse(self.order.is_paid)
        self.order.mark_as_paid()
        self.assertTrue(self.order.is_paid)
```

Iš viso parašyta **20+** testų, dengiantys pagrindines funkcijas.

---

## 3. Rezultatai ir išvados

### Rezultatai

- Sėkmingai įgyvendinta pilna restorano valdymo sistema Python kalba su OOP principais
- Programa demonstruoja visus 4 OOP ramsčius: inkapsuliaciją, paveldėjimą, polimorfizmą ir abstrakciją
- Singleton dizaino šablonas užtikrina, kad sistema turi vieną centralizuotą valdiklį
- CSV failo įrašymas ir nuskaitymas leidžia meniu ir užsakymų duomenis išsaugoti tarp programos paleidimų
- Visi unit testai sėkmingai praeina, patvirtinant pagrindinės logikos teisingumą

### Išvados

Šio kursinio darbo metu sukurta funkcionali Restorano Valdymo Sistema, demonstruojanti objektinio programavimo galimybes. Programa leidžia valdyti meniu, staliukus ir užsakymus. Darbas parodė, kaip OOP principai padeda struktūrizuoti kodą – kiekviena klasė turi aiškią atsakomybę.

Ateityje programą galima plėsti:

- **Grafine sąsaja** naudojant `tkinter` arba `PyQt5`
- **Duomenų baze** (`SQLite`) vietoj CSV failų
- **Darbuotojų valdymo** moduliu (padavėjai, virtuvės darbuotojai)
- **Rezervacijų sistema** su data ir laiku

---

## 4. Naudoti šaltiniai

- Python dokumentacija: <https://docs.python.org/3/>
- PEP8 stiliaus gairės: <https://pep8.org/>
- ABC modulis: <https://docs.python.org/3/library/abc.html>
- CSV modulis: <https://docs.python.org/3/library/csv.html>
- unittest: <https://docs.python.org/3/library/unittest.html>
- Design Patterns: <https://refactoring.guru/design-patterns/singleton/python/example>
