import webbrowser
import time
import pyautogui
import pyperclip

def main():
    # 1️⃣ Abrir o Google no navegador padrão
    webbrowser.open("https://www.google.com")

    # 2️⃣ Esperar a página carregar
    time.sleep(3)  # ajuste se necessário

    # 3️⃣ Texto da pesquisa (com acento)
    texto = "mauri Lico é foda"

    # 4️⃣ Copiar para clipboard
    pyperclip.copy(texto)

    # 5️⃣ Colar no navegador (Ctrl + V)
    pyautogui.hotkey("ctrl", "v")

    # 6️⃣ Pressionar Enter
    pyautogui.press("enter")

if __name__ == "__main__":
    main()
