from requests_html import HTMLSession
import json
import random

class Pokemon:
    def __init__(self, name, types, current_attacks, next_attacks, base_health=200, current_health=200,
                 level=1, current_exp=0):
        self.name = name
        self.types = types
        self.base_health = base_health
        self.current_health = current_health
        self.level = level
        self.current_exp = current_exp
        self.current_attacks = current_attacks
        self.next_attacks = next_attacks

    def attack(attacker, defender):
        attacks = list(attacker.current_attacks.items())  # lista de tuplas (nombre, poder)

        # Mostrar ataques disponibles
        print(f"\n¿Qué ataque quieres usar con {attacker.name}?")
        for i, (name, power) in enumerate(attacks, start=1):
            print(f"[{i}] {name} (Poder: {power})")

        # Bucle hasta entrada válida
        while True:
            try:
                choice = int(input("Elige el número del ataque: "))
                if 1 <= choice <= len(attacks):
                    break
                else:
                    print(f"Por favor elige un número entre 1 y {len(attacks)}.")
            except ValueError:
                print("Entrada inválida. Debes introducir un número.")

        # Ejecutar el ataque
        selected_attack, power = attacks[choice - 1]
        damage = int(power)  # suponemos que power es convertible a int

        defender.current_health -= damage
        defender.current_health = max(defender.current_health, 0)  # evitar valores negativos

        print(f"\n{attacker.name} usó {selected_attack} causando {damage} de daño.")
        print(f"{defender.name} ahora tiene {defender.current_health} de salud.")

    def defend(defender, attacker):
        input(f"Turno de {attacker.name}. Pulsa ENTER para continuar: ")
        attacks = list(attacker.current_attacks.items())
        selected_attack, power = random.choice(attacks)
        damage = int(power)  # suponemos que power es convertible a int

        defender.current_health -= damage
        defender.current_health = max(defender.current_health, 0)  # evitar valores negativos
        print(f"\n{attacker.name} usó {selected_attack} causando {damage} de daño.")
        print(f"{defender.name} ahora tiene {defender.current_health} de salud.")
        input("Pulsa ENTER para continuar: ")

    def potion_heal(self):
        self.current_health += 80
        if self.current_health > 200:
            self.current_health = 200

    def learn_next_attack(self):
        if self.next_attacks:
            # Convertimos dict en lista para acceder por índice
            next_attacks_list = list(self.next_attacks.items())
            next_move_name, next_move_power = next_attacks_list[0]

            print(f"{self.name} ha subido al nivel {self.level} y quiere aprender '{next_move_name, next_move_power}'.")
            print(f"Ataques actuales: {list(self.current_attacks.items())}")
            print(f"Pulsa un número del 1 al {len(self.current_attacks)} para sustituir un ataque.")
            print("Pulsa 0 para no aprender el nuevo ataque.")

            while True:
                try:
                    choice = int(input("¿Qué quieres hacer?: "))
                    if choice == 0:
                        print(f"{self.name} decidió no aprender {next_move_name}.")
                        break
                    elif 1 <= choice <= len(self.current_attacks):
                        current_moves = list(self.current_attacks.items())
                        # informamos al jugadior del cambio primero
                        print(f"{self.name} ha aprendido {next_move_name} en lugar de {current_moves[choice - 1][0]}.")
                        # Sustituye el ataque en la posición elegida
                        current_moves[choice - 1] = (next_move_name, next_move_power)
                        self.current_attacks = dict(current_moves)
                        # Elimina el ataque aprendido de next_attacks
                        del self.next_attacks[next_move_name]
                        break
                    else:
                        print("Número fuera de rango.")
                except ValueError:
                    print("Entrada inválida. Introduce un número.")

    def gain_exp(self, amount):
        self.current_exp += amount
        print(f"{self.name} ha ganado {amount} puntos de experiencia.")
        self.level_up()

    def level_up(self):
        if self.level == 1 and self.current_exp >= 100:
            self.level = 2
            print(f"{self.name} ha subido al nivel {self.level}")
            self.learn_next_attack()
        elif self.level == 2 and self.current_exp >= 125:
            self.level = 3
            print(f"{self.name} ha subido al nivel {self.level}")
            self.learn_next_attack()
        elif self.level == 3 and self.current_exp >= 150:
            self.level = 4
            print(f"{self.name} ha subido al nivel {self.level}")
            self.learn_next_attack()
        elif self.level == 4 and self.current_exp >= 175:
            self.level = 5
            print(f"{self.name} ha subido al nivel {self.level}")
            self.learn_next_attack()



    def __str__(self):
        tipos = ', '.join(self.types)
        current_atks = '\n  - ' + '\n  - '.join(
            f"{move} - Poder: {power}"
            for move, power in self.current_attacks.items()
        ) if hasattr(self, 'current_attacks') else "Sin ataques actuales"

        next_atks = '\n  - ' + '\n  - '.join(
            f"{name} - Poder: {power}"
            for name, power in self.next_attacks.items() if name != "learning_level"
        ) if hasattr(self, 'next_attacks') else "Sin próximos ataques"

        return (f"{self.name} (Nivel {self.level}) - Tipos: {tipos} - Salud: {self.current_health}/{self.base_health}, "
                f"Experiencia: {self.current_exp}\n"
                f"Ataques base:{current_atks}\n"
                f"Próximos ataques: {next_atks}")

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "types": self.types,
            "current_health": self.current_health,
            "base_health": self.base_health,
            "current_exp": self.current_exp,
            "current_attacks": self.current_attacks,
            "next_attacks": self.next_attacks
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            level=data["level"],
            types=data["types"],
            current_health=data["current_health"],
            base_health=data["base_health"],
            current_exp=data["current_exp"],
            current_attacks=data["current_attacks"],
            next_attacks=data["next_attacks"]
        )

def main():

    def create_pokemon(index):
        url = f"https://pokexperto.net/index2.php?seccion=nds/nationaldex/movimientos_nivel&pk={index}"
        session = HTMLSession()
        response = session.get(url)

        # Extraer nombre desde el elemento con clase "mini"
        name_elem = response.html.find('.mini', first=True)
        name = name_elem.text.strip() if name_elem else f"Pokemon #{index}"

        # Buscar la caja con clase 'bordeambos' que contiene el texto 'Tipos'
        tipo_section = None
        bordeambos_elems = response.html.find('.bordeambos')
        for elem in bordeambos_elems:
            if 'Tipos' in elem.text or "Tipo" in elem.text:
                tipo_section = elem
                break

        types = []
        if tipo_section:
            # Buscar todas las imágenes dentro de ese bloque
            imgs = tipo_section.find('img')
            for img in imgs:
                alt = img.attrs.get('alt', '').capitalize()
                if alt:
                    types.append(alt)

        # Extraer ataques con poder
        attacks = {}
        pkmain_sections = response.html.find('.pkmain')
        for section in pkmain_sections:
            if section.find('.bordetodos'):
                attack_rows = section.find('tr.check3.bazul')
                for row in attack_rows:
                    columns = row.find('td')
                    if columns:
                        move = columns[0].text.split("\n")[0]
                        power = columns[3].text.strip()
                        if power and power != "--":
                            attacks.update({
                                move: power
                            })

                break

        current_attacks = {}
        next_attacks = {}
        count = 0

        for move, power in attacks.items():
            count += 1
            if count <= 4:
                current_attacks[move] = power
            elif 5 <= count <= 8:
                next_attacks[move] = power
            else:
                break

        return Pokemon(name, types, current_attacks, next_attacks)

    def create_json():
        pokemons_scrapped = {}
        for index in range(1, 11):
            p = create_pokemon(index)
            pokemons_scrapped[p.name] = p.to_dict()
            print (f"Pokemon {p.name} añadido. {index} de 150.")
        with open("pokemons.json", "w", encoding="utf-8") as f:
            json.dump(pokemons_scrapped, f, indent=4, ensure_ascii=False)

    create_json()

if __name__ == "__main__":
    main()







