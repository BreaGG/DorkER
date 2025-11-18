import os
from colorama import Fore, Style, init

init(autoreset=True)

# ========================================================
# GENERADORES DE DORKS SEGÚN TIPO DE OBJETIVO
# ========================================================

def dorks_email(email):
    return {
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
            f'filetype:csv "{email}"',
        ],
        "Leaks / Exposiciones": [
            f'"{email}" "password"',
            f'"{email}" "contraseña"',
            f'"{email}" "login"',
            f'"{email}" "user"',
        ],
        "Sitios específicos": [
            f'site:pastebin.com "{email}"',
            f'site:github.com "{email}"',
            f'site:reddit.com "{email}"',
            f'site:linkedin.com "{email}"',
            f'site:twitter.com "{email}"',
        ],
        "Variaciones ofuscadas": [
            f'"{email.replace("@", " at ")}"',
            f'"{email.replace("@", " [at] ")}"',
            f'"{email.replace("@", "(at)")} "',
            f'"{email.replace("@", "[at]")}"',
        ],
    }


def dorks_usuario(username):
    return {
        "Perfiles / usernames": [
            f'"{username}"',
            f'"{username}" site:github.com',
            f'"{username}" site:gitlab.com',
            f'"{username}" site:twitter.com',
            f'"{username}" site:linkedin.com',
            f'"{username}" site:instagram.com',
        ],
        "Leaks": [
            f'"{username}" "password"',
            f'"{username}" "login"',
            f'"{username}" "credentials"',
        ],
        "Combinaciones útiles": [
            f'"{username}" "@gmail.com"',
            f'"{username}" "email"',
        ]
    }


def dorks_dominio(domain):
    return {
        "Información general": [
            f'site:{domain}',
            f'"{domain}"',
            f'"{domain}" -www',
        ],
        "Subdominios": [
            f'site:{domain} -www.{domain}',
            f'"*.{domain}"',
        ],
        "Documentos": [
            f'site:{domain} filetype:pdf',
            f'site:{domain} filetype:xls',
            f'site:{domain} filetype:doc',
        ],
        "Leaks": [
            f'"{domain}" "password"',
            f'"{domain}" "database"',
            f'"{domain}" "index of"',
        ]
    }


def dorks_subdominio(subdomain):
    domain = subdomain.split(".", 1)[-1]
    return {
        "Búsqueda básica": [
            f'site:{subdomain}',
            f'"{subdomain}"',
        ],
        "Infraestructura": [
            f'site:{subdomain} "server"',
            f'site:{subdomain} "Apache"',
            f'site:{subdomain} "nginx"',
            f'site:{subdomain} "port"',
        ],
        "Relación con el dominio": [
            f'"{subdomain}" "{domain}"',
            f'site:{domain} "{subdomain}"',
        ],
        "Archivos expuestos": [
            f'site:{subdomain} filetype:env',
            f'site:{subdomain} filetype:log',
            f'site:{subdomain} filetype:txt',
        ]
    }

# ========================================================
# MENÚ
# ========================================================

def mostrar_menu():
    print(Fore.CYAN + "\n=== MENÚ PRINCIPAL ===")
    print(Fore.YELLOW + "1." + Fore.WHITE + " Correos electrónicos")
    print(Fore.YELLOW + "2." + Fore.WHITE + " Usernames / aliases")
    print(Fore.YELLOW + "3." + Fore.WHITE + " Dominios")
    print(Fore.YELLOW + "4." + Fore.WHITE + " Subdominios")
    print(Fore.YELLOW + "5." + Fore.WHITE + " Salir")
    return input(Fore.GREEN + "\nElige una opción: ")


def exportar_txt(nombre, dorks):
    archivo = f"dorks_{nombre.replace('@','_').replace('.', '_')}.txt"

    with open(archivo, "w", encoding="utf-8") as f:
        f.write(f"GOOGLE DORKS PARA: {nombre}\n")
        f.write("=" * 60 + "\n\n")

        for cat, contenido in dorks.items():
            f.write(f"### {cat} ###\n")
            for d in contenido:
                f.write(f"{d}\n")
            f.write("\n")

    print(Fore.GREEN + f"\n✔ Archivo exportado como: {archivo}\n")


# ========================================================
# MAIN
# ========================================================

if __name__ == "__main__":
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            objetivo = input("Introduce el correo: ")
            dorks = dorks_email(objetivo)

        elif opcion == "2":
            objetivo = input("Introduce el username: ")
            dorks = dorks_usuario(objetivo)

        elif opcion == "3":
            objetivo = input("Introduce el dominio (ej: acme.com): ")
            dorks = dorks_dominio(objetivo)

        elif opcion == "4":
            objetivo = input("Introduce el subdominio (ej: dev.acme.com): ")
            dorks = dorks_subdominio(objetivo)

        elif opcion == "5":
            print(Fore.RED + "Saliendo...")
            break

        else:
            print(Fore.RED + "Opción inválida.")
            continue

        # Mostrar resultados
        print(Fore.CYAN + "\n=== RESULTADOS ===\n")
        for cat, lista in dorks.items():
            print(Fore.YELLOW + f"\n--- {cat} ---")
            for d in lista:
                print(Fore.WHITE + d)

        # Exportar
        exportar = input(Fore.GREEN + "\n¿Quieres exportar los dorks a un .txt? (s/n): ")
        if exportar.lower() == "s":
            exportar_txt(objetivo, dorks)
