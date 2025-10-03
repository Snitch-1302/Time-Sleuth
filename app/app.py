import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from datetime import datetime
import plotly.express as px
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scripts.clustering import cluster_events
 
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw_timeline.csv")
ABSTRACT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "abstracted_timeline.csv")

# Load datasets
def load_data(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return pd.DataFrame()

raw_df = load_data(RAW_PATH)
abstract_df = load_data(ABSTRACT_PATH)

# Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "TimeSleuth: Forensic Timeline"

# Layout
app.layout = html.Div([
    html.H1("⏳ TimeSleuth: Forensic Timeline", style={"textAlign": "center"}),

    dcc.Tabs(id="tabs", value="raw", children=[
        dcc.Tab(label="Raw Timeline", value="raw"),
        dcc.Tab(label="Abstracted Timeline", value="abstract"),
    ]),

    # Controls section - moved to main layout
    html.Div(id="controls-container", style={"margin": "20px"}),

    dcc.Graph(id="timeline_graph", style={"height": "70vh"}),

    html.Div(id="click-data", style={
        "marginTop": "20px", "padding": "10px",
        "border": "1px solid #ccc", "borderRadius": "8px"
    })
])

# ================= Controls Rendering =================
@app.callback(
    Output("controls-container", "children"),
    Input("tabs", "value")
)
def render_controls(tab):
    df = raw_df if tab == "raw" else abstract_df
    if df.empty:
        return html.Div("⚠️ No data available.")

    # Normalize event type column
    if tab == "raw":
        event_type_col = df["action"] if "action" in df.columns else df.get("event_type", pd.Series([], dtype=str))
    else:
        event_type_col = df["abstracted_action"] if "abstracted_action" in df.columns else df.get("event_type", pd.Series([], dtype=str))
    
    # Prepare slider values
    min_ts = df["timestamp"].min().timestamp()
    max_ts = df["timestamp"].max().timestamp()

    # Create human-readable marks (5 evenly spaced)
    marks = {
        int(ts.timestamp()): ts.strftime("%Y-%m-%d %H:%M:%S")
        for ts in pd.date_range(df["timestamp"].min(), df["timestamp"].max(), periods=5)
    }

    controls = [
        html.H3("🔍 Forensic Analysis Controls", style={"color": "#2c3e50"}),
        html.Label("Filter by Event Type:"),
        dcc.Dropdown(
            id="event-filter",
            options=[{"label": evt, "value": evt} for evt in event_type_col.unique()],
            multi=True,
            value=[],
            placeholder="Select event types to analyze..."
        ),
        html.Br(),
        html.Label("Select Time Range:"),
        dcc.RangeSlider(
            id="time-slider",
            min=min_ts,
            max=max_ts,
            step=60,
            value=[min_ts, max_ts],
            marks=marks,
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),
        dcc.Checklist(
            id="cluster-toggle",
            options=[{"label": "🔗 Enable Clustering (group nearby events)", "value": "cluster"}],
            value=[]
        ),
        html.Hr(),
        html.Div([
            html.P("📊 Total Events: " + str(len(df)), style={"fontWeight": "bold"}),
            html.P("⏱️ Time Span: " + str((df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 60) + " minutes", style={"fontWeight": "bold"}),
        ], style={"backgroundColor": "#ecf0f1", "padding": "10px", "borderRadius": "5px"})
    ]
    return controls

@app.callback(
    Output("timeline_graph", "figure"),
    Output("click-data", "children"),
    Input("tabs", "value"),
    Input("event-filter", "value"),
    Input("time-slider", "value"),
    Input("timeline_graph", "clickData"),
    Input("cluster-toggle", "value"),
    prevent_initial_call=True
)
def update_graph(tab, event_filter, time_range, click_data, cluster_toggle):
    df = raw_df if tab == "raw" else abstract_df
    if df.empty:
        return px.scatter(title="No Data Available"), "⚠️ No data to display."

    # Normalized y-axis column
    if tab == "raw":
        df["event_type"] = df["action"] if "action" in df.columns else df.get("event_type", "Unknown")
    else:
        df["event_type"] = df["abstracted_action"] if "abstracted_action" in df.columns else df.get("event_type", "Unknown")
    
    # Handle time filter - provide defaults if not initialized
    if time_range is None or len(time_range) != 2:
        time_range = [df["timestamp"].min().timestamp(), df["timestamp"].max().timestamp()]
    
    start, end = [datetime.fromtimestamp(t) for t in time_range]
    df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]

    # Event filter - handle None case
    if event_filter is None:
        event_filter = []
    if event_filter:
        df = df[df["event_type"].isin(event_filter)]

    # Apply clustering if enabled - handle None case
    y_col = "event_type"
    if cluster_toggle is None:
        cluster_toggle = []
    if "cluster" in cluster_toggle:
        df = cluster_events(df)
        y_col = "cluster"

    # Create forensic timeline plot
    fig = px.scatter(
        df,
        x="timestamp",
        y=y_col,
        color=y_col,
        hover_data=df.columns,
        title="🔍 Forensic Timeline Analysis",
        labels={
            "timestamp": "Time",
            "event_type": "Event Type",
            "cluster": "Event Cluster"
        }
    )
    
    # Enhance the plot for forensic analysis
    fig.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Event Categories",
        showlegend=True,
        height=600,
        font=dict(size=12),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add forensic-specific styling
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color='black')),
        opacity=0.7
    )

    # Forensic event inspection
    details = "ℹ️ Click a point to see forensic event details."
    if click_data:
        point = click_data["points"][0]
        row = df.iloc[point["pointIndex"]]
        
        # Determine threat level based on event type
        threat_events = ["file_encrypt", "data_exfiltration", "process_create", "connection_outbound"]
        threat_level = "🔴 HIGH" if row["action"] in threat_events else "🟡 MEDIUM" if "network" in str(row["source"]) else "🟢 LOW"
        
        details = html.Div([
            html.H4("🔍 Forensic Event Analysis"),
            html.Div([
                html.P([html.B("Threat Level: "), threat_level]),
                html.P([html.B("Event Type: "), str(row["event_type"])]),
                html.P([html.B("Action: "), str(row["action"])]),
                html.P([html.B("Source: "), str(row["source"])]),
                html.P([html.B("Timestamp: "), str(row["timestamp"])]),
                html.P([html.B("Artifact: "), str(row["artifact"])]),
                html.P([html.B("Details: "), str(row.get("details", 'N/A'))]),
                html.P([html.B("Cluster: "), str(row.get("cluster", 'N/A'))]),
            ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "5px", "backgroundColor": "#f9f9f9"})
        ])

    return fig, details

# Initial graph rendering callback
@app.callback(
    Output("timeline_graph", "figure", allow_duplicate=True),
    Output("click-data", "children", allow_duplicate=True),
    Input("tabs", "value"),
    prevent_initial_call='initial_duplicate'
)
def initial_graph_render(tab):
    df = raw_df if tab == "raw" else abstract_df
    if df.empty:
        return px.scatter(title="No Data Available"), "⚠️ No data to display."

    # Normalized y-axis column
    if tab == "raw":
        df["event_type"] = df["action"] if "action" in df.columns else df.get("event_type", "Unknown")
    else:
        df["event_type"] = df["abstracted_action"] if "abstracted_action" in df.columns else df.get("event_type", "Unknown")
    
    # Create forensic timeline plot
    fig = px.scatter(
        df,
        x="timestamp",
        y="event_type",
        color="event_type",
        hover_data=df.columns,
        title="🔍 Forensic Timeline Analysis",
        labels={
            "timestamp": "Time",
            "event_type": "Event Type"
        }
    )
    
    # Enhance the plot for forensic analysis
    fig.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Event Categories",
        showlegend=True,
        height=600,
        font=dict(size=12),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add forensic-specific styling
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color='black')),
        opacity=0.7
    )

    return fig, "ℹ️ Click a point to see forensic event details."

if __name__ == "__main__":
    app.run(debug=True)
