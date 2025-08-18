import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
import plotly.express as px

VULN_INDICATORS = [
    "Total Damage, Adjusted ('000 US$)",
    "No. Affected",
    "Total Deaths",
    "GDP growth (annual %)",
    "Inflation, consumer prices (annual %)",
    "ShockImpact",
    "ResilienceScore",
]

def heatmap(df, iso3, fw=14, fh=6):
    country = df[df["ISO3"] == iso3].copy()
    data = country[["Year"] + [c for c in VULN_INDICATORS if c in df.columns]].set_index("Year")
    norm = (data - data.min()) / (data.max() - data.min())
    fig, ax = plt.subplots(figsize=(fw, fh))
    sns.heatmap(norm.T, cmap="RdYlBu_r", cbar_kws={'label': 'Normalized Vulnerability'}, ax=ax)
    ax.set_title(f"Vulnerability Heatmap – {iso3}")
    return fig



def shock_panels(df, iso3, fw=12, fh=8):
    cols = [c for c in ["Total Damage, Adjusted ('000 US$)","No. Affected","Total Deaths","ShockImpact"] if c in df.columns]
    country = df[df["ISO3"] == iso3]
    fig, axes = plt.subplots(2, 2, figsize=(fw, fh))
    axes = axes.flatten()
    for i, col in enumerate(cols):
        axes[i].plot(country["Year"], country[col], marker="o")
        axes[i].set_title(col)
    plt.suptitle(f"Shock Impact – {iso3}")
    plt.tight_layout()
    return fig

def top_vulnerabilities(df, iso3, n=3):
    """
    Return top n vulnerabilities for a given country (latest year),
    based on normalized values of vulnerability indicators.
    """
    if iso3 not in df["ISO3"].values:
        return []

    indicators = [c for c in VULN_INDICATORS if c in df.columns]

    norm_df = df.copy()
    for ind in indicators:
        col = norm_df[ind]
        if col.notna().sum() > 0:
            norm_df[ind] = (col - col.min()) / (col.max() - col.min() + 1e-9)

    country = norm_df[norm_df["ISO3"] == iso3].sort_values("Year").tail(1)
    if country.empty:
        return []

    row = country.iloc[0]

    results = [(ind, row[ind]) for ind in indicators if pd.notna(row[ind])]

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:n]


def trade_network(df, iso3, year=None, top_n=10, fw=12, fh=8):
    """
    Clean trade network visualization without numbers on the edges.
    Edge thickness represents trade volume (normalized).
    """
    trade_cols = [c for c in df.columns if c.endswith("_Export") or c.endswith("_Import")]

    if year is None:
        row = df[df["ISO3"] == iso3].sort_values("Year").tail(1)
        if row.empty: return None
        row = row.iloc[0]
        year = int(row["Year"])
    else:
        row = df[(df["ISO3"] == iso3) & (df["Year"] == year)]
        if row.empty: return None
        row = row.iloc[0]

    trade_data = {}
    for col in trade_cols:
        partner, flow = col.split("_")[0], col.split("_")[1]
        val = row[col]
        if pd.notna(val) and val > 0 and partner != iso3:
            trade_data.setdefault(partner, {"export": 0, "import": 0})
            trade_data[partner][flow.lower()] = val

    top = sorted(
        trade_data.items(),
        key=lambda x: x[1]["export"] + x[1]["import"],
        reverse=True
    )[:top_n]

    G = nx.Graph()
    G.add_node(iso3, size=1800, color="crimson")

    edge_weights = []
    for partner, vals in top:
        tot = vals["export"] + vals["import"]
        if tot > 0:
            size = 600 + (tot / max(1, max(v["export"] + v["import"] for _, v in top))) * 1000
            G.add_node(partner, size=size, color="skyblue")
            G.add_edge(iso3, partner, weight=tot)
            edge_weights.append(tot)

    if edge_weights:
        min_w, max_w = min(edge_weights), max(edge_weights)
        norm_widths = {
            (u, v): 1 + 7 * ((G[u][v]["weight"] - min_w) / (max_w - min_w + 1e-9))
            for u, v in G.edges()
        }
    else:
        norm_widths = {}

    pos = nx.spring_layout(G, seed=42, k=1.5)

    fig, ax = plt.subplots(figsize=(fw, fh))
    nx.draw_networkx_nodes(
        G, pos,
        node_size=[G.nodes[n]["size"] for n in G],
        node_color=[G.nodes[n]["color"] for n in G],
        alpha=0.9, ax=ax
    )
    nx.draw_networkx_edges(
        G, pos,
        width=[norm_widths.get((u, v), 2) for u, v in G.edges()],
        alpha=0.6, edge_color="gray", ax=ax
    )
    nx.draw_networkx_labels(
        G, pos,
        font_size=11, font_weight="bold", ax=ax
    )

    ax.set_title(f"Top {top_n} Trade Partners – {iso3} ({year})",
                 fontsize=14, fontweight="bold")
    ax.axis("off")
    return fig

def plot_top_countries_by_indicator(df, indicator: str, top_n: int = 10):
    """
    Plot top N vulnerable countries for a given indicator.
    Example: Top 10 countries with highest unemployment.
    """
    if indicator not in df.columns:
        raise ValueError(f"{indicator} not found in dataframe")

    ranked = (
        df.groupby("ISO3")[indicator]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig = px.bar(
        ranked, x="ISO3", y=indicator,
        title=f"Top {top_n} vulnerable countries – {indicator}",
        color=indicator, color_continuous_scale="Reds"
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def plot_top_vulnerabilities_for_country(df, iso3: str, top_n: int = 3):
    """
    Plot top N vulnerability indicators for a given country as a bar chart.
    Example: Top 3 vulnerabilities of India in latest year.
    """
    vulns = top_vulnerabilities(df, iso3, n=top_n)
    if not vulns:
        return None

    labels, scores = zip(*vulns)

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(labels, scores, color="crimson", alpha=0.8)
    ax.set_xlabel("Vulnerability Score")
    ax.set_title(f"Top {top_n} Vulnerabilities – {iso3}")
    ax.invert_yaxis()

    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f"{score:.2f}", va="center", fontsize=10)

    fig.tight_layout()
    return fig