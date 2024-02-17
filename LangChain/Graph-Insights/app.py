from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64
import os
import time
import plotly.graph_objects as go
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# create image folder to stor imgaes of graphs made
if not os.path.exists("images"):
    os.mkdir("images")

df = pd.read_csv("domain-notable-ai-system.csv")
df = df[df.Entity != "Not specified"]


app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.layout = dbc.Container(
    [
        dcc.Markdown("## Domain of notable AI systems, by year of publication\n"
                     "###### Specific field, area, or category in which an AI system is designed to operate or solve problems."),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='domain-graph'),
                            dcc.Dropdown(id="year-slct",
                                         options=df['Year'].unique(),
                                         value='2020')
                        ]),
                        className="my-3"
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='line-graph'),
                            dcc.Dropdown(id="domain-slct",
                                         multi=True,
                                         options=sorted(df['Entity'].unique()),
                                         value=['Multimodal', 'Language']),
                        ]),
                        className="my-3"
                    ),
                    width=6
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Button(id='btn', children='Insights', className='mb-2'), width=1)
            ],
            justify='end'
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Spinner(html.Div(id='content', children=''), fullscreen=False), width=6)
            ],
            justify='end'
        ),
    ]
)


@callback(
    Output("domain-graph", "figure"),
    Input("year-slct", "value"),
)
def update_pie_chart(year_chosen):
    year_chosen = int(year_chosen)
    df_dom_filtrd = df[df['Year'] == year_chosen]
    pie_chart = px.pie(df_dom_filtrd, names='Entity', values='Annual number of AI systems by domain', template='plotly_dark')
    return pie_chart


@callback(
    Output("line-graph", "figure"),
    Input("domain-slct", "value"),
)
def update_line_graph(domains_chosen):
    df_filtrd = df[df['Year']>1999]
    df_filtrd = df_filtrd[df_filtrd['Entity'].isin(domains_chosen)]
    line_graph = px.line(df_filtrd, x='Year', y='Annual number of AI systems by domain', color='Entity', template='plotly_dark')
    return line_graph


@callback(
    Output('content','children'),
    Input('btn','n_clicks'),
    State('line-graph','figure'),
    prevent_initial_call=True
)
def graph_insights(_, fig):
    fig_object = go.Figure(fig)
    fig_object.write_image(f"images/fig{_}.png")
    time.sleep(2)

    chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=256, api_key="Enter-Your-Key")
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    image_path = f"images/fig{_}.png"
    base64_image = encode_image(image_path)
    result = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": "What data insight can we get from this graph"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "auto",    # https://platform.openai.com/docs/guides/vision
                        },
                    },
                ]
            )
        ]
    )
    return result.content


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

