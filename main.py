import os

def generar_dorks(email):
    dorks = {
        "Búsqueda exacta": [
            f'"{email}"'
        ],
        "Documentos": [
            f'filetype:pdf "{email}"',
            f'filetype:doc "{email}"',
            f'filetype:docx "{email}"',
            f'filetype:xls "{email}"',
            f'filetype:xlsx "{email}"',
            f'filetype:txt "{email}"',
            f'filetype:csv "{email}"'
        ],
        "Indexes expuestos": [
            f'intitle:"index of" "{email}"'
        ],
        "Leaks / Exposiciones": [
            f'"{email}" "password"',
            f'"{email}" "contraseña"',
            f'"{email}" "login"',
            f'"{email}" "user"'
        ],
        "Sitios específicos": [
            f'site:pastebin.com "{email}"',
            f'site:github.com "{email}"',
            f'site:reddit.com "{email}"',
            f'site:linkedin.com "{email}"',
            f'site:twitter.com "{email}"',
            f'site:facebook.com "{email}"'
        ],
        "Variaciones ofuscadas": [
            f'"{email.replace("@", " at ")}"',
            f'"{email.replace("@", " [at] ")}"',
            f'"{email.replace("@", "(at)")} "',
            f'"{email.replace("@", "[at]")}"'
        ]
    }
    return dorks


def mostrar_menu():
    print("\n=== MENÚ DE OPCIONES ===")
    print("1. Ver todos los Dorks")
    print("2. Ver solo una categoría")
    print("3. Exportar todos los Dorks a TXT")
    print("4. Salir")
    return input("\nElige una opción: ")


def exportar_txt(email, dorks):
    nombre_archivo = f"dorks_{email.replace('@','_').replace('.','_')}.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(f"GOOGLE DORKS PARA: {email}\n")
        f.write("=" * 50 + "\n\n")

        for categoria, lista in dorks.items():
            f.write(f"### {categoria} ###\n")
            for d in lista:
                f.write(d + "\n")
            f.write("\n")

    print(f"\n✔ Archivo generado: {nombre_archivo}\n")


if __name__ == "__main__":
    email = input("Introduce el correo a investigar: ")

    dorks = generar_dorks(email)

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            print("\n=== TODOS LOS DORKS ===\n")
            for categoria, lista in dorks.items():
                print(f"\n--- {categoria} ---")
                for d in lista:
                    print(d)

        elif opcion == "2":
            print("\nCategorías disponibles:")
            for i, categoria in enumerate(dorks.keys(), 1):
                print(f"{i}. {categoria}")

            seleccion = int(input("\nElige categoría: "))
            categoria = list(dorks.keys())[seleccion - 1]

            print(f"\n=== {categoria} ===")
            for d in dorks[categoria]:
                print(d)

        elif opcion == "3":
            exportar_txt(email, dorks)

        elif opcion == "4":
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")
