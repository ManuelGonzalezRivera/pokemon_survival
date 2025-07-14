import os
import random
import time
from pokedex import Pokemon
import json

def get_pokemon_from_json():
    pokemons_objects = {}
    with open("pokemons.json", "r", encoding="utf-8") as f:
        data = json.load(f)  # data es un dict {nombre: datos_pokemon_dict}

    for name, pokemon_data in data.items():
        p = Pokemon.from_dict(pokemon_data)
        pokemons_objects[name] = p

    return pokemons_objects

def show_player_data(player):
    print(f"""
       ----- Información del Jugador -----
       Nombre: {player['player_name']}
       Pokéballs: {player['pokeballs']}
       Pociones de salud: {player['health_potions']}
       Combates: {player['combats']}
       """)

    print("------ Pokémons del jugador: -------")
    for i in range(1, 4):
        print(f"""
    POKEMON {i}:
                    
    {player['pokemon_team'][f'pokemon_{i}']}""")

    print("------ Pokémons capturados: -------")
    try:
        with open(player["captured_pokemons"], "r", encoding="utf-8") as f:
            try:
                captured = json.load(f)
            except json.JSONDecodeError:
                captured = {}

        if captured:
            for name in captured:
                print(f"- {name}")
        else:
            print("Aún no has capturado ningún Pokémon.")
    except FileNotFoundError:
        print("No se encontró el archivo de Pokémon capturados.")
    print("------------------------------------------")

def use_potion(player):
    if player["health_potions"] <= 0:
        print("No tienes pociones disponibles.")
        return False

    else:
        print("Tus Pokémon actuales:")
        for key, pkmn in player["pokemon_team"].items():
            print(f"{key}: {pkmn.name} (Salud actual: {pkmn.current_health}/200)")

        while True:
            num = input("¿A qué Pokémon quieres darle una poción? Escribe 1, 2 o 3: ")
            while num not in ("1", "2", "3"):
                num = input("Entrada no válida. Escribe 1, 2 o 3: ")
            choice = "pokemon_" + num
            if choice in player["pokemon_team"]:
                pokemon = player["pokemon_team"][choice]
                pokemon.potion_heal()
                player["health_potions"] -= 1
                print(f"{pokemon.name} ha sido curado. Salud actual: {pokemon.current_health}/200")
                print(f"Te quedan {player['health_potions']} pociones.")
                return True
            else:
                print("Ese Pokemon no existe, escribe un número válido.")


def get_player(pokemons):
    player_pokemons = {}

    # Preguntar nombre del jugador
    player_name = input("¿Cuál es tu nombre de entrenador?: ")

    # Elegir 3 Pokémon aleatorios del diccionario 'pokemons'
    input(f"A continuación se te asignarán 3 pokemons random.Toca ENTER para ver tu nuevo inventario y tu nuevo "
          f"equipo: ")
    for i in range(3):
        pokemon = random.choice(list(pokemons.values()))
        player_pokemons[f"pokemon_{i+1}"] = pokemon

    # Crear archivo JSON para pokémons
    captured_file = "pokemons_captured.json"
    with open(captured_file, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4, ensure_ascii=False)

        # Crear el diccionario del jugador
    player = {
        "player_name": player_name,
        "pokemon_team": player_pokemons,
        "pokeballs": 0,
        "health_potions": 0,
        "combats": 0,
        "captured_pokemons": captured_file
    }
    show_player_data(player)
    return player

def player_receive_random_object(player):
    num = random.randint(1, 2)
    random_object= ""
    if num == 1:
        player["health_potions"] += 1
        random_object = "Poción"
    elif num == 2:
        player["pokeballs"] += 1
        random_object = "Pokeball"
    return random_object

def show_health_bar(pokemon):
    vida_actual = pokemon.current_health
    vida_total = 200
    longitud_barra = 20
    porcentaje = int((vida_actual / vida_total) * longitud_barra)
    barra = "#" * porcentaje + "-" * (longitud_barra - porcentaje)
    return f"[{barra}] {vida_actual}/{vida_total}"

def capture_pokemon(player, enemy):
    input("Pulsa ENTER para lanzar tu pokeball")
    player["pokeballs"] = - 1
    print(f"Pokeball lanzada, {enemy.name} se resiste!")
    for second in range(5):
        time.sleep(1)
        print("~")
    pokemon_captured = False
    if enemy.current_health >= 120:
        p = random.randint(1,4)
        if p == 1:
            pokemon_captured = True
    elif 50 >= enemy.current_health > 120:
        p = random.randint(1,2)
        if p == 2:
            pokemon_captured = True
    elif enemy.current_health < 50:
            pokemon_captured = True

    if pokemon_captured:
        print(f"¡Has capturado a {enemy.name}!")
        file_path = player["captured_pokemons"]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

            data[enemy.name] = enemy.to_dict()  # <- Ahora sí añadimos antes de guardar

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            print("El archivo de Pokémon capturados no existe.")

    else:
        print(f"{enemy.name} se ha escapado de la pokeball!")

    return pokemon_captured


def pokemon_fight(pokemons, player):
    play = True
    while play:
        main_pokemon = random.choice(list(player["pokemon_team"].values()))
        enemy = random.choice(list(pokemons.values()))
        enemy.current_health = 200

        input(f"Toca ENTER para iniciar tu combate número {player["combats"] + 1}.")
        print(f"Has recibido 1 {player_receive_random_object(player)} extra al inicio del combate!")

        while True:
            print("""                   ------------------------
            Tu equipo:""")
            for i in range(1, 4):
                pokemon = player["pokemon_team"][f"pokemon_{i}"]
                print(f"{i}: {pokemon.name} - {show_health_bar(pokemon)}")
            choice = input(f"¿A qué pokemon envías a combatir? Pulsa el número del pokemon (1-3) para continuar: ")
            if choice in ("1", "2", "3"):
                main_pokemon = player["pokemon_team"][f"pokemon_{choice}"]
                break
            else:
                print("Entrada no válida.")

        while main_pokemon == enemy:
            enemy = random.choice(list(pokemons.values()))

        input(f"Un {enemy.name} salvaje apareció. Toca ENTER para iniciar el combate.")
        print(f"\n¡{main_pokemon.name} se enfrenta a {enemy.name}!")
        print("¡Comienza el combate!")
        combat_active = True  # bandera para controlar si sigue el combate
        while combat_active:
            print("\n--- ESTADO ACTUAL ---")
            print(f"{main_pokemon.name}: {show_health_bar(main_pokemon)}")
            print(f"{enemy.name}: {show_health_bar(enemy)}")
            turn_choice = input("""
            Opciones en tu turno:
            [C] Combatir
            [H] Usar Poción
            [P] Usar Pokeball
            [I] Revisar tu inventario [No consume turno]
    
            ¿Qué quieres hacer?: """).upper()

            if turn_choice == "C":
                main_pokemon.attack(enemy)
                if enemy.current_health <= 0:
                    print(f"\n¡{enemy.name} ha sido derrotado!")
                    player["combats"] += 1
                    main_pokemon.gain_exp(100)
                    print(f"¡{main_pokemon} ha ganado 100 de experiencia!")
                    combat_active = False
                else:
                    main_pokemon.defend(enemy)

                if main_pokemon.current_health <= 0:
                    print(f"\n¡{main_pokemon.name} ha sido derrotado!")
                    print("Este es el resumen de tu partida:")
                    show_player_data(player)
                    captured_file = player["captured_pokemons"]
                    if os.path.exists(captured_file):
                        os.remove(captured_file)
                    combat_active = False
                    play = False

            elif turn_choice == "H":
                if use_potion(player):
                    main_pokemon.defend(enemy)
                    if main_pokemon.current_health <= 0:
                        print(f"\n¡{main_pokemon.name} ha sido derrotado!")
                        print("Este es el resumen de tu partida:")
                        show_player_data(player)
                        captured_file = player["captured_pokemons"]
                        if os.path.exists(captured_file):
                            os.remove(captured_file)
                        combat_active = False
                        play = False
                else:
                    pass


            elif turn_choice == "P":
                if player["pokeballs"] > 0:
                    pokemon_captured = capture_pokemon(player, enemy)
                    if pokemon_captured:
                        player["combats"] += 1
                        combat_active = False
                    else:
                        main_pokemon.defend(enemy)  # El enemigo ataca si no se captura
                        if main_pokemon.current_health <= 0:
                            print(f"\n¡{main_pokemon.name} ha sido derrotado!")
                            print("Este es el resumen de tu partida:")
                            show_player_data(player)
                            captured_file = player["captured_pokemons"]
                            if os.path.exists(captured_file):
                                os.remove(captured_file)
                            combat_active = False
                            play = False
                else:
                    print("No tienes pokeballs")

            elif turn_choice == "I":
                print(f"""
                ----- Información del Jugador -----
                Nombre: {player['player_name']}
                Pokéballs: {player['pokeballs']}
                Pociones de salud: {player['health_potions']}
                Combates: {player['combats']}
                """)
                print("------ Pokémons capturados: -------")
                try:
                    with open(player["captured_pokemons"], "r", encoding="utf-8") as f:
                        captured = json.load(f)
                    if captured:
                        for name, poke_data in captured.items():
                            print(f"\n{name}")
                    else:
                        print("Aún no has capturado ningún Pokémon.")
                except FileNotFoundError:
                    print("No se encontró el archivo de Pokémon capturados.")
                print("------------------------------------------")

            else:
                    print("Comando no válido")


def main():

    pokemons = get_pokemon_from_json()
    player = get_player(pokemons)
    pokemon_fight(pokemons, player)


if __name__ == "__main__":
    main()

# to fix:
# pokeballs en negativo
# no puede haber 2 pokemon iguales en el equipo (mismo objeto)
# problema al crear el json de captured_pokemon