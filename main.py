# main.py

from restaurant import Restaurant, Food, Drink, Table


def setup_restaurant():
    restaurant = Restaurant("Gero Apetito Restoranas")

    loaded = restaurant.load_menu_from_csv()

    if not loaded:

        print("Kuriamas pradinis meniu...")
        restaurant.add_to_menu(Food("F01", "Cepelinai", 8.50, "Pagrindinis"))
        restaurant.add_to_menu(Food("F02", "Saltibarsciai", 5.00, "Sriuba"))
        restaurant.add_to_menu(Food("F03", "Kepta duona", 3.50, "Uzkandziai"))
        restaurant.add_to_menu(Food("F04", "Blynai su grietine", 6.00, "Desertas"))
        restaurant.add_to_menu(Food("F05", "Bulviu sriuba", 4.50, "Sriuba"))
        restaurant.add_to_menu(Drink("D01", "Vanduo", 1.50, False))
        restaurant.add_to_menu(Drink("D02", "Sultys", 2.50, False))
        restaurant.add_to_menu(Drink("D03", "Kava", 2.00, False))
        restaurant.add_to_menu(Drink("D04", "Alus", 3.00, True))
        restaurant.add_to_menu(Drink("D05", "Vynas", 5.00, True))
        restaurant.save_menu_to_csv()
        print("Meniu issaugotas i menu.csv")

    for i in range(1, 7):  
        restaurant.add_table(Table(i, 4))

    return restaurant


def print_separator():
    print("\n" + "=" * 44)


def main():
    print_separator()
    print("  RESTORANO VALDYMO SISTEMA")
    print("  Kursinis darbas - OOP Python")
    print_separator()

    restaurant = setup_restaurant()

    while True:
        print("\n--- PAGRINDINIS MENIU ---")
        print("1. Rodyti meniu")
        print("2. Rodyti staliukus")
        print("3. Sukurti uzsakyma")
        print("4. Prideti patiekala prie uzsakymo")
        print("5. Rodyti uzsakymo saskalta")
        print("6. Uzdaryti uzsakyma (apmoketi)")
        print("7. Dienos pajamos")
        print("8. Valdyti menu (prideti/salinti)")
        print("9. Issaugoti uzsakymus i faila")
        print("0. Iseiti")
        print("-" * 44)

        choice = input("Pasirink (0-9): ").strip()

        if choice == "1":
            restaurant.display_menu()

        elif choice == "2":
            restaurant.display_tables()

        elif choice == "3":
            restaurant.display_tables()
            try:
                table_num = int(input("Staliuko numeris: "))
                order = restaurant.create_order(table_num)
                print(f"[OK] Sukurtas uzsakymas #{order.order_id} staliukui {table_num}")
            except ValueError as e:
                print(f"[KLAIDA] {e}")

        elif choice == "4":
            try:
                table_num = int(input("Staliuko numeris: "))
                table = restaurant.get_table(table_num)
                if not table:
                    print("[KLAIDA] Staliukas nerastas!")
                    continue
                if not table.current_order:
                    print("[KLAIDA] Siam staliukui nera aktyvaus uzsakymo! (Pirmiau pasirink 3)")
                    continue

                restaurant.display_menu()
                item_name = input("Patiekalo pavadinimas: ").strip()
                item = restaurant.find_menu_item(item_name)
                if not item:
                    print(f"[KLAIDA] '{item_name}' nerastas menuje!")
                    continue

                qty = int(input("Kiekis: "))
                table.current_order.add_item(item, qty)
                print(f"[OK] Prideta: {item.name} x{qty} (€{item.price * qty:.2f})")
            except ValueError as e:
                print(f"[KLAIDA] {e}")

        elif choice == "5":
            try:
                table_num = int(input("Staliuko numeris: "))
                table = restaurant.get_table(table_num)
                if table and table.current_order:
                    print(table.current_order.display_receipt())
                else:
                    print("[KLAIDA] Nera aktyvaus uzsakymo!")
            except ValueError:
                print("[KLAIDA] Neteisingas numeris!")

        elif choice == "6":
            try:
                table_num = int(input("Staliuko numeris: "))
                table = restaurant.get_table(table_num)
                if table and table.current_order:
                    print(table.current_order.display_receipt())
                    confirm = input("Patvirtinti apmokejima? (t/n): ").strip().lower()
                    if confirm == "t":
                        restaurant.close_order(table_num)
                        print(f"[OK] Staliukas {table_num} atlaisvintas. Aciu!")
                        restaurant.save_orders_to_csv()
                else:
                    print("[KLAIDA] Nera aktyvaus uzsakymo!")
            except ValueError:
                print("[KLAIDA] Neteisingas numeris!")

        elif choice == "7":
            revenue = restaurant.get_daily_revenue()
            paid_orders = [o for o in restaurant.get_all_orders() if o.is_paid]
            print_separator()
            print(f"  DIENOS ATASKAITA")
            print(f"  Apmoketu uzsakymu: {len(paid_orders)}")
            print(f"  Dienos pajamos:    EUR {revenue:.2f}")
            print_separator()

        elif choice == "8":
            print("\n1. Prideti maista")
            print("2. Prideti gerima")
            print("3. Salinti is menio")
            sub = input("Pasirink: ").strip()

            if sub == "1":
                try:
                    item_id = input("ID (pvz. F10): ").strip()
                    name = input("Pavadinimas: ").strip()
                    price = float(input("Kaina (EUR): "))
                    category = input("Kategorija: ").strip()
                    restaurant.add_to_menu(Food(item_id, name, price, category))
                    restaurant.save_menu_to_csv()
                    print(f"[OK] '{name}' pridetas i menu!")
                except ValueError as e:
                    print(f"[KLAIDA] {e}")

            elif sub == "2":
                try:
                    item_id = input("ID (pvz. D10): ").strip()
                    name = input("Pavadinimas: ").strip()
                    price = float(input("Kaina (EUR): "))
                    alc = input("Alkoholinis? (t/n): ").strip().lower() == "t"
                    restaurant.add_to_menu(Drink(item_id, name, price, alc))
                    restaurant.save_menu_to_csv()
                    print(f"[OK] '{name}' pridetas i menu!")
                except ValueError as e:
                    print(f"[KLAIDA] {e}")

            elif sub == "3":
                restaurant.display_menu()
                name = input("Kurį šalinti? (įvesk pavadinimą): ").strip()
                removed = restaurant.remove_from_menu(name)
                if removed:
                    restaurant.save_menu_to_csv()
                    print(f"[OK] '{name}' pasalintas is menio!")
                else:
                    print(f"[KLAIDA] '{name}' nerastas!")

        elif choice == "9":
            restaurant.save_orders_to_csv()
            print("[OK] Uzsakymai issaugoti i orders.csv")

        elif choice == "0":
            restaurant.save_orders_to_csv()
            print("\nIki pasimatymo! Viso gero!")
            break

        else:
            print("[KLAIDA] Neteisinga parinktis! Pasirink 0-9.")


if __name__ == "__main__":
    main()
