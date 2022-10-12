from dash import Dash
from callback_graph import register_graph
from callback_price import register_price
from prime_api import prime_calls
from layout import layout

app = Dash(__name__)
app.title = 'Insto trading app'

app.layout = layout
register_graph(app)
register_price(app)
prime_calls(app)

if __name__ == '__main__':
    app.run_server(debug=True)
