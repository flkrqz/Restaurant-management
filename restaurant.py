# restaurant.py
# Restorano Valdymo Sistema - OOP Kursinis Darbas
# Autorius: [Jaromir Koženevski]

from abc import ABC, abstractmethod  
import csv
import os
from datetime import datetime


# ============================================================
# 1. ABSTRAKTI KLASĖ - MenuItem (ABSTRAKCIJA + PAVELDĖJIMAS)
# ============================================================

class MenuItem(ABC):
    """
    Abstrakti bazinė klasė visiems meniu elementams.
    ABSTRAKCIJA: Negali sukurti MenuItem objekto tiesiogiai,
    tik per Food arba Drink subklases.
    """

    def __init__(self, item_id: str, name: str, price: float):
        self._item_id = item_id
        self._name = name
        self._price = price

    @property
    def item_id(self):
        return self._item_id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Kaina negali būti neigiama!")
        self._price = value

    @abstractmethod
    def display(self) -> str:
        """
        POLIMORFIZMAS: kiekviena subklasė įgyvendina šį metodą savaip.
        Abstraktus metodas - PRIVALO būti perrašytas subklasėse.
        """
        pass

    def __str__(self):
        return f"{self._name} - €{self._price:.2f}"


# ============================================================
# 2. FOOD KLASĖ - paveldima iš MenuItem (PAVELDĖJIMAS)
# ============================================================

class Food(MenuItem):
    """
    Maisto produktas meniu.
    PAVELDĖJIMAS: paveldi visus MenuItem atributus ir metodus.
    """

    def __init__(self, item_id: str, name: str, price: float, category: str):
        super().__init__(item_id, name, price)  
        self._category = category

    @property
    def category(self):
        return self._category

    def display(self) -> str:
        """POLIMORFIZMAS: Food rodo kitaip nei Drink"""
        return f"[MAISTAS] {self._name} ({self._category}) - €{self._price:.2f}"


# ============================================================
# 3. DRINK KLASĖ - paveldima iš MenuItem (PAVELDĖJIMAS)
# ============================================================

class Drink(MenuItem):
    """
    Gėrimas meniu.
    PAVELDĖJIMAS: paveldi visus MenuItem atributus ir metodus.
    """

    def __init__(self, item_id: str, name: str, price: float, is_alcoholic: bool = False):
        super().__init__(item_id, name, price)
        self._is_alcoholic = is_alcoholic

    @property
    def is_alcoholic(self):
        return self._is_alcoholic

    def display(self) -> str:
        """POLIMORFIZMAS: Drink rodo kitaip nei Food"""
        tipas = "Alkoholinis" if self._is_alcoholic else "Nealkoholinis"
        return f"[GERIMAS] {self._name} ({tipas}) - €{self._price:.2f}"


# ============================================================
# 4. ORDER KLASĖ - Užsakymas (KOMPOZICIJA)
# ============================================================

class Order:
    """
    Kliento užsakymas.
    KOMPOZICIJA: Order TURI MenuItem objektų sąrašą.
    Jei Order ištrinamas - visi jo items taip pat ištrinami.
    INKAPSULIACIJA: naudojame __ (private) atributus.
    """

    def __init__(self, order_id: int, table_number: int):
        self.__order_id = order_id          
        self.__table_number = table_number  
        self.__items = []                   
        self.__created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.__is_paid = False

    @property
    def order_id(self):
        return self.__order_id

    @property
    def table_number(self):
        return self.__table_number

    @property
    def is_paid(self):
        return self.__is_paid

    @property
    def created_at(self):
        return self.__created_at

    def add_item(self, item: MenuItem, quantity: int = 1):
        """Prideda patiekalą į užsakymą"""
        if quantity <= 0:
            raise ValueError("Kiekis turi būti teigiamas!")
        
        for i, (existing_item, qty) in enumerate(self.__items):
            if existing_item.item_id == item.item_id:
                self.__items[i] = (existing_item, qty + quantity)
                return
        self.__items.append((item, quantity))

    def remove_item(self, item_name: str):
        """Šalina patiekalą iš užsakymo pagal pavadinimą"""
        self.__items = [
            (item, qty) for item, qty in self.__items
            if item.name.lower() != item_name.lower()
        ]

    def get_total(self) -> float:
        """Skaičiuoja bendrą sumą"""
        return sum(item.price * qty for item, qty in self.__items)

    def mark_as_paid(self):
        """Pažymi užsakymą kaip apmokėtą"""
        self.__is_paid = True

    def get_items(self):
        """Grąžina items sąrašo kopiją"""
        return list(self.__items)

    def display_receipt(self) -> str:
        """Rodo sąskaitą"""
        lines = [
            "=" * 42,
            f"  UŽSAKYMAS #{self.__order_id} | Staliukas {self.__table_number}",
            f"  Laikas: {self.__created_at}",
            "-" * 42
        ]
        if not self.__items:
            lines.append("  (Tuščias užsakymas)")
        for item, qty in self.__items:
            suma = item.price * qty
            lines.append(f"  {item.name:<20} x{qty}  €{suma:.2f}")
        lines.append("-" * 42)
        lines.append(f"  VISO:                      €{self.get_total():.2f}")
        vat = self.get_total() * 0.21
        lines.append(f"  PVM (21%):                 €{vat:.2f}")
        lines.append("=" * 42)
        return "\n".join(lines)


# ============================================================
# 5. TABLE KLASĖ - Staliukas (AGREGACIJA)
# ============================================================

class Table:
    """
    Restorano staliukas.
    AGREGACIJA: Table TURI nuorodą į Order objektą,
    bet Order egzistuoja nepriklausomai nuo Table.
    """

    def __init__(self, table_number: int, capacity: int):
        self.__table_number = table_number
        self.__capacity = capacity
        self.__current_order = None   
        self.__is_occupied = False

    @property
    def table_number(self):
        return self.__table_number

    @property
    def capacity(self):
        return self.__capacity

    @property
    def is_occupied(self):
        return self.__is_occupied

    @property
    def current_order(self):
        return self.__current_order

    def assign_order(self, order: Order):
        """Priskiria užsakymą prie staliuko"""
        self.__current_order = order
        self.__is_occupied = True

    def clear_table(self):
        """Atlaisvina staliuką po apmokėjimo"""
        self.__current_order = None
        self.__is_occupied = False

    def status(self) -> str:
        busena = "UZIMTAS" if self.__is_occupied else "LAISVAS"
        return f"Staliukas {self.__table_number} (vietų: {self.__capacity}) [{busena}]"


# ============================================================
# 6. RESTAURANT KLASĖ - Singleton dizaino šablonas
# ============================================================

class Restaurant:
    """
    Pagrindinis restorano valdiklis.

    SINGLETON DIZAINO ŠABLONAS:
    Užtikrina, kad egzistuoja TIK VIENAS Restaurant objektas.
    Tai logiška - restoranas yra vienas!

    Kaip veikia: __new__ metodas tikrina ar instance jau yra.
    Jei taip - grąžina tą patį objektą, nekuria naujo.
    """

    _instance = None  
    def __new__(cls, name: str = "Mano Restoranas"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, name: str = "Mano Restoranas"):
        if self._initialized:
            return  
        self._initialized = True
        self.__name = name
        self.__menu = []        
        self.__tables = []     
        self.__orders = []      
        self.__order_counter = 1

    @property
    def name(self):
        return self.__name

    # ---- MENIU VALDYMAS ----

    def add_to_menu(self, item: MenuItem):
        """Prideda patiekalą į meniu"""
        self.__menu.append(item)

    def remove_from_menu(self, item_name: str):
        """Šalina patiekalą iš meniu"""
        before = len(self.__menu)
        self.__menu = [item for item in self.__menu
                       if item.name.lower() != item_name.lower()]
        return len(self.__menu) < before  

    def get_menu(self):
        return list(self.__menu)

    def find_menu_item(self, name: str):
        """Ieško patiekalo pagal pavadinimą"""
        for item in self.__menu:
            if item.name.lower() == name.lower():
                return item
        return None

    def display_menu(self):
        """Rodo visą meniu konsolėje"""
        print(f"\n{'='*44}")
        print(f"  {self.__name} - MENIU")
        print(f"{'='*44}")
        foods = [i for i in self.__menu if isinstance(i, Food)]
        drinks = [i for i in self.__menu if isinstance(i, Drink)]
        if foods:
            print("  --- MAISTAS ---")
            for item in foods:
                print(f"  {item.display()}")
        if drinks:
            print("  --- GERIMAI ---")
            for item in drinks:
                print(f"  {item.display()}")
        print(f"{'='*44}\n")

    # ---- STALIUKŲ VALDYMAS ----

    def add_table(self, table: Table):
        self.__tables.append(table)

    def get_table(self, table_number: int):
        for table in self.__tables:
            if table.table_number == table_number:
                return table
        return None

    def get_all_tables(self):
        return list(self.__tables)

    def display_tables(self):
        """Rodo staliukų būsenas"""
        print(f"\n{'='*44}")
        print("  STALIUKŲ BŪSENOS")
        print(f"{'='*44}")
        for table in self.__tables:
            print(f"  {table.status()}")
        print(f"{'='*44}\n")

    # ---- UŽSAKYMŲ VALDYMAS ----

    def create_order(self, table_number: int) -> Order:
        """Sukuria naują užsakymą prie staliuko"""
        table = self.get_table(table_number)
        if table is None:
            raise ValueError(f"Staliukas {table_number} nerastas!")
        if table.is_occupied:
            raise ValueError(f"Staliukas {table_number} jau užimtas!")

        order = Order(self.__order_counter, table_number)
        self.__order_counter += 1
        self.__orders.append(order)
        table.assign_order(order)
        return order

    def close_order(self, table_number: int) -> bool:
        """Uždaro užsakymą ir atlaisvina staliuką"""
        table = self.get_table(table_number)
        if table and table.current_order:
            table.current_order.mark_as_paid()
            table.clear_table()
            return True
        return False

    def get_all_orders(self):
        return list(self.__orders)

    def get_daily_revenue(self) -> float:
        """Skaičiuoja dienos pajamas (tik apmokėti užsakymai)"""
        return sum(order.get_total() for order in self.__orders if order.is_paid)

    # ---- FAILŲ SKAITYMAS IR RAŠYMAS ----

    def save_menu_to_csv(self, filename: str = "menu.csv"):
        """Išsaugo meniu į CSV failą"""
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "type", "name", "price", "extra"])
            for item in self.__menu:
                if isinstance(item, Food):
                    writer.writerow([item.item_id, "food", item.name,
                                     item.price, item.category])
                elif isinstance(item, Drink):
                    writer.writerow([item.item_id, "drink", item.name,
                                     item.price, item.is_alcoholic])

    def load_menu_from_csv(self, filename: str = "menu.csv"):
        """Nuskaito meniu iš CSV failo"""
        if not os.path.exists(filename):
            return False
        self.__menu = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["type"] == "food":
                    item = Food(row["id"], row["name"],
                                float(row["price"]), row["extra"])
                elif row["type"] == "drink":
                    item = Drink(row["id"], row["name"],
                                 float(row["price"]), row["extra"] == "True")
                else:
                    continue
                self.__menu.append(item)
        return True

    def save_orders_to_csv(self, filename: str = "orders.csv"):
        """Išsaugo užsakymus į CSV failą"""
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["order_id", "table", "items", "total", "paid", "time"])
            for order in self.__orders:
                items_str = "; ".join(
                    [f"{item.name}x{qty}" for item, qty in order.get_items()]
                )
                writer.writerow([
                    order.order_id,
                    order.table_number,
                    items_str,
                    f"{order.get_total():.2f}",
                    order.is_paid,
                    order.created_at
                ])
