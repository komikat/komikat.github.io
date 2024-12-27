# generated using claude 3.5 + github copilot
# use at your own risk

import pandas as pd
from datetime import datetime
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

with open("blr_chat.txt", "r", encoding="utf-8") as file:
    chat_lines = file.readlines()
    print("First 3 lines of chat:")
    for i in range(min(3, len(chat_lines))):
        print(chat_lines[i].strip())

messages = []
date_pattern = r"\[(\d{1,2}/\d{1,2}/\d{2})"
name_pattern = r"] (.+?):"

for line in chat_lines:
    try:
        date_match = re.search(date_pattern, line)
        name_match = re.search(name_pattern, line)

        if date_match and name_match:
            date_str = date_match.group(1)
            date = datetime.strptime(date_str, "%d/%m/%y").date()
            sender = name_match.group(1).strip()
            messages.append({"date": date, "sender": sender})
            if len(messages) == 1:  # Debug first successful parse
                print(f"\nFirst parsed message:")
                print(f"Date: {date}, Sender: {sender}")
    except Exception as e:
        print(f"Error parsing line: {line.strip()}")
        print(f"Error details: {str(e)}")
        continue

print(f"\nTotal messages parsed: {len(messages)}")

# Create DataFrame
df = pd.DataFrame(messages)
if not df.empty:
    daily_counts = df.groupby(["date", "sender"]).size().unstack(fill_value=0)

    # Create cumulative counts
    cumulative_counts = daily_counts.cumsum()

    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Daily Messages by Member", "Cumulative Messages over Time"),
    )

    # Add daily message traces
    for column in daily_counts.columns:
        fig.add_trace(
            go.Scatter(
                x=daily_counts.index,
                y=daily_counts[column],
                name=column,
                mode="lines+markers",
            ),
            row=1,
            col=1,
        )

    for column in cumulative_counts.columns:
        fig.add_trace(
            go.Scatter(
                x=cumulative_counts.index,
                y=cumulative_counts[column],
                name=f"{column} (cumulative)",
                line=dict(dash="dot"),
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        height=900,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.05),
        template="plotly_white",
    )

    fig.write_html("whatsapp_analysis.html")
    fig.show()
else:
    print("No messages found to analyze")
