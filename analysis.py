import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")


def generate_sales_data():
    np.random.seed(42)

    products = {
        "Notebook":  (800, 300),
        "Telefón":   (600, 200),
        "Tablet":    (400, 150),
        "Slúchadlá": (120,  50),
        "Myš":       ( 35,  15),
    }
    regions = ["Bratislava", "Košice", "Žilina", "Nitra", "Banská Bystrica"]
    start = datetime(2024, 1, 1)

    rows = []
    for _ in range(500):
        product = np.random.choice(list(products))
        mean, std = products[product]
        price = max(10, np.random.normal(mean, std))
        qty = np.random.randint(1, 6)
        date = start + timedelta(days=np.random.randint(0, 365))
        region = np.random.choice(regions)
        discount = np.random.choice([0, 0, 0, 0.05, 0.10, 0.15])
        revenue = price * qty * (1 - discount)

        rows.append({
            "date":     date,
            "product":  product,
            "region":   region,
            "price":    round(price, 2),
            "quantity": qty,
            "discount": discount,
            "revenue":  round(revenue, 2),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    df["quarter"] = df["date"].dt.to_period("Q")
    return df


def print_stats(df):
    print(f"Záznamy:       {len(df)}")
    print(f"Celkové tržby: {df['revenue'].sum():,.0f} €")
    print(f"Priemer:       {df['revenue'].mean():,.2f} €")

    print("\nTržby podľa produktu:")
    print(df.groupby("product")["revenue"].sum().sort_values(ascending=False).to_string())

    print("\nTržby podľa regiónu:")
    print(df.groupby("region")["revenue"].sum().sort_values(ascending=False).to_string())


def build_dashboard(df):
    PALETTE = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 10), facecolor="#F8FAFC")
    fig.suptitle("Sales Analytics Dashboard  •  2024", fontsize=18, fontweight="bold")
    gs = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.35,
                           left=0.07, right=0.96, top=0.92, bottom=0.07)

    # Panel 1: mesačné tržby
    ax1 = fig.add_subplot(gs[0, 0])
    monthly = df.groupby("month")["revenue"].sum().reset_index()
    monthly["month"] = monthly["month"].dt.to_timestamp()
    ax1.plot(monthly["month"], monthly["revenue"], color=PALETTE[0], linewidth=2.5, marker="o")
    ax1.fill_between(monthly["month"], monthly["revenue"], alpha=0.12, color=PALETTE[0])
    ax1.set_title("Mesačné tržby", fontweight="bold")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k €"))
    ax1.tick_params(axis="x", rotation=30)

    # Panel 2: tržby podľa produktu
    ax2 = fig.add_subplot(gs[0, 1])
    prod = df.groupby("product")["revenue"].sum().sort_values()
    bars = ax2.barh(prod.index, prod.values, color=PALETTE[:len(prod)], edgecolor="none")
    for bar, val in zip(bars, prod.values):
        ax2.text(val + prod.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f} €", va="center", fontsize=9)
    ax2.set_title("Tržby podľa produktu", fontweight="bold")
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    ax2.set_xlim(0, prod.max() * 1.2)

    # Panel 3: heatmapa región x kvartál
    ax3 = fig.add_subplot(gs[1, 0])
    pivot = df.groupby(["region", "quarter"])["revenue"].sum().unstack(fill_value=0)
    pivot.columns = [str(c) for c in pivot.columns]
    sns.heatmap(pivot / 1000, ax=ax3, cmap="Blues", annot=True, fmt=".0f",
                linewidths=0.5, cbar_kws={"label": "tis. €"}, annot_kws={"size": 8})
    ax3.set_title("Región × Kvartál (tis. €)", fontweight="bold")
    ax3.tick_params(axis="x", rotation=20)

    # Panel 4: histogram
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.hist(df["revenue"], bins=40, color=PALETTE[0], alpha=0.6, edgecolor="white")
    ax4.axvline(df["revenue"].mean(), color=PALETTE[3], linestyle="--",
                label=f"Priemer: {df['revenue'].mean():.0f} €")
    ax4.axvline(df["revenue"].median(), color=PALETTE[2], linestyle="--",
                label=f"Medián: {df['revenue'].median():.0f} €")
    ax4.set_title("Distribúcia objednávok", fontweight="bold")
    ax4.legend(fontsize=9)

    plt.savefig("dashboard.png", dpi=150, bbox_inches="tight")
    print("Dashboard uložený: dashboard.png")
    plt.close()


def export_csv(df):
    summary = (df.groupby(["month", "product"])
                 .agg(celkove_trzby=("revenue", "sum"),
                      pocet=("revenue", "count"),
                      priemer=("revenue", "mean"))
                 .round(2)
                 .reset_index())
    summary["month"] = summary["month"].astype(str)
    summary.to_csv("summary.csv", index=False, encoding="utf-8-sig")
    print("Súhrn uložený: summary.csv")


df = generate_sales_data()
print_stats(df)
build_dashboard(df)
export_csv(df)
