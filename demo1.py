from dataclasses import field

import flet as ft


@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)


@ft.control
class DigitButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLACK
    color: ft.Colors = ft.Colors.WHITE
    


@ft.control
class ActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE
    color: ft.Colors = ft.Colors.WHITE
        


@ft.control
class ExtraActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE_GREY_100
    color: ft.Colors = ft.Colors.BLACK


@ft.control
class CalculatorApp(ft.Container):
    def init(self):
        self.width = 700
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        self.result = ft.Text(value="0", color=ft.Colors.BLACK, size=36)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[self.result],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(content="AC"),
                        ExtraActionButton(content="+/-"),
                        ExtraActionButton(content="%"),
                        ActionButton(content="/"),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content=ft.Text("7", size=30)),
                        DigitButton(content=ft.Text("8", size=30)),
                        DigitButton(content=ft.Text("9", size=30)),
                        ActionButton(content="*"),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content=ft.Text("4", size=30)),
                        DigitButton(content=ft.Text("5", size=30)),
                        DigitButton(content=ft.Text("6", size=30)),
                        ActionButton(content="-"),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content=ft.Text("1", size=30)),
                        DigitButton(content=ft.Text("2", size=30)),
                        DigitButton(content=ft.Text("3", size=30)),
                        ActionButton(content="+"),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="0", expand=2),
                        DigitButton(content="."),
                        ActionButton(content="="),
                    ]
                ),
            ]
        )


def main(page: ft.Page):
    page.title = "Calc App"
    # create application instance
    calc = CalculatorApp()

    # add application's root control to the page
    page.add(calc)


ft.run(main)