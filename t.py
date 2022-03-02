import dash
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")

app = dash.Dash(__name__)


style_data_conditional = [
    {
        "if": {"state": "active"},
        "backgroundColor": "rgba(150, 180, 225, 0.2)",
        "border": "1px solid blue",
    },
    {
        "if": {"state": "selected"},
        "backgroundColor": "rgba(0, 116, 217, .03)",
        "border": "1px solid blue",
    },
]

app.layout = dash_table.DataTable(
    id="table",
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("records"),
    style_data_conditional=style_data_conditional,
)


@app.callback(
    Output("table", "style_data_conditional"),
    Output('table', 'active_cell'),
    [Input("table", "active_cell")]
)
def update_selected_row_color(active):
    print(active)
    style = style_data_conditional.copy()
    if active:
        style.append(
            {
                "if": {"row_index": active["row"]},
                "backgroundColor": "rgba(150, 180, 225, 0.2)",
                "border": "1px solid blue",
            },
        )
    return style, {'row': 2, 'column': 2}


if __name__ == "__main__":
    app.run_server(debug=True)