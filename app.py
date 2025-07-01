import flet as ft
from config.db import connect_db, disconnect_db

def main(page: ft.Page):
    page.title = "MongoDB App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 300
    page.window.resizable = True
    page.window.maximizable = True
    page.window.minimizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Mensaje principal
    message_text = ft.Text(
        "🔌 Sin conexión",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="red"
    )
    
    def conectar_bd(e):
        message_text.value = "🔄 Conectando..."
        message_text.color = "orange"
        page.update()
        
        if connect_db():
            message_text.value = "🎉 ¡Bienvenido a la base de datos!"
            message_text.color = "green"
            btn_connect.disabled = True
            btn_disconnect.disabled = False
        else:
            message_text.value = "❌ Error de conexión"
            message_text.color = "red"
        
        page.update()
    
    def desconectar_bd(e):
        disconnect_db()
        message_text.value = "� Desconectado"
        message_text.color = "grey"
        btn_connect.disabled = False
        btn_disconnect.disabled = True
        page.update()
    
    # Botones
    btn_connect = ft.ElevatedButton(
        "Conectar",
        on_click=conectar_bd,
        bgcolor="blue",
        color="white",
        width=150
    )
    
    btn_disconnect = ft.ElevatedButton(
        "Desconectar",
        on_click=desconectar_bd,
        bgcolor="red",
        color="white",
        width=150,
        disabled=True
    )
    
    # Layout
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🗄️", size=60),
                ft.Text("MongoDB Connector", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=30),
                message_text,
                ft.Divider(height=30),
                btn_connect,
                btn_disconnect,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
            ),
            padding=40,
            border_radius=15,
            bgcolor="white",
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="grey400",
            )
        )
    )

if __name__ == "__main__":
    ft.app(target=main)