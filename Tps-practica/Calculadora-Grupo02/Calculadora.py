import kivy
from kivy.app import App, Builder

class CalculadoraApp(App):
    def build(self):
        return Builder.load_file("calculadora.kv")
    def calcular(self, expresion):
        self.root.ids.resultado.text = str(eval(expresion)) # type: ignore
    def limpiar(self):
        self.root.ids.resultado.text = "" # type: ignore
  

if __name__ == '__main__':
    CalculadoraApp().run()