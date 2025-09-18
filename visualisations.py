import plotly.graph_objects as go
import textwrap
import pandas as pd

'''Data should only be filtered by indicator and ITL1 regions'''

def gauge(data, region, indicator, selected_year, bounds, fontsize=36):
    data = data.loc[data['year'] == int(selected_year), :]
    median = data[indicator].median()
    temp = data.loc[(data['name'] == region), :]
    value = temp[indicator].values[0]
    if value * 1.15 > bounds[1]:
        bounds[1] = value * 1.15
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': '<br>'.join(textwrap.wrap(f"{region} {indicator}, {selected_year}", width=40)),
            'font': {'size': 16}},
        number={'font': {'size': fontsize},
                'prefix': "£"},  # Adjust the number text size
        gauge={
            'axis': {'range': [bounds[0], bounds[1]]},  # Adjust range as needed
            'bar': {'color': "rgba(10, 10, 10, 0.6)"},  # Set bar color with 50% transparency
            'steps': [
                {'range': [bounds[0], median * 0.95], 'color': "#eb5f5f"},
                {'range': [median * 0.95, median * 1.05], 'color': "#fcbf0b"},
                {'range': [median * 1.05, data[indicator].max() * 1.2], 'color': "#00979e"}
            ],
        },
        domain={'x': [0.2, 0.8]}  # shrink gauge within figure
    ))
    fig.update_layout(
        autosize=True,
        height=290
    )
    return fig

def time_series(data, regions, uk_data):
    uk_data = uk_data[['name', 'year', 'GVA/H volume']].dropna()
    data = data[['name', 'year', 'GVA/H volume']].dropna()
    
    temp = data.loc[(data['name'] == regions[0]), :]

    # Create a time series plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=uk_data['year'],  # X-axis: Year
        y=uk_data['GVA/H volume'],  # Y-axis: Indicator values
        mode='lines',  # Line and markers
        name=f"United Kingdom",
        line=dict(color="rgba(85, 85, 85, 0.3)", width=2),  # Customize line color and width
        marker=dict(size=6),  # Customize marker size
    ))
    fig.add_trace(go.Scatter(
        x=temp['year'],  # X-axis: Year
        y=temp['GVA/H volume'],  # Y-axis: Indicator values
        mode='lines+markers',  # Line and markers
        name=f"{regions[0]}",
        line=dict(color="#eb5e5e", width=2),  # Customize line color and width
        marker=dict(size=6)  # Customize marker size
    ))
    temp = data.loc[(data['name'] == regions[1]), :]
    fig.add_trace(go.Scatter(
        x=temp['year'],  # X-axis: Year
        y=temp['GVA/H volume'],  # Y-axis: Indicator values
        mode='lines+markers',  # Line and markers
        name=f"{regions[1]}",
        line=dict(color="#9c4f8b", width=2),  # Customize line color and width
        marker=dict(size=6)  # Customize marker size
    ))

    # Update layout for better visualization
    fig.update_layout(
        title={
            'text': '<span style="font-weight:normal;">' + 
            '<br>'.join(textwrap.wrap(f"Time Series of {regions[0]} against {regions[1]} - <b>GVA per hour (chained 2008)</b>", width=100)) +
            '</span>',
            'font': {'size': 14},
            'x': 0.05,  # move slightly to the right (0=left, 1=right)
            'y': 0.9,  # move slightly up (1=top of plotting area)
            'xanchor': 'left',   # align title relative to x
            'yanchor': 'top',    # align title relative to y
        },
        xaxis_title="Year",
        yaxis_title=f"GVA per hour (chained 2008) (%)",
        autosize=True,
        template="plotly_white",  # Use a clean white background
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.3,  # Position below the chart
            x=-0.02,  # Center the legend horizontally
            xanchor="left",  # Anchor the legend
            font=dict(size=16)
        ),
        height=350
    )
    
    return fig

def spider(data, indicators, region, colour, driver):
    # Build the output DataFrame
    row = pd.DataFrame({'name': data['name'].unique()})
    for indicator, years in driver.items():
        # Get the year for this period
        year_val = int(years[1])
        # Subset data for this year and column
        sub = data.loc[data['year'] == year_val, ['name', indicator]]
        # Merge so values align by code
        row = row.merge(sub, on='name', how='left')
    
    # Compute percentile ranks for each indicator
    percentile_ranks = pd.DataFrame({'name': data['name'].unique()})

    for ind in indicators:
        # For each indicator, get the series
        series = row[ind]

        # Compute percentile rank of each value
        ranks = series.rank(pct=True) * 100  # gives 0–100
        percentile_ranks[ind] = ranks

    # Subset to your region of interest
    temp = percentile_ranks.loc[percentile_ranks['name'] == region, indicators].copy()

    # Handle "opposite indicators" (lower values = better)
    opposite_indicators = ['Low Skilled', 'Inactive due to Illness']
    for ind in opposite_indicators:
        if ind in temp.columns:
            temp[ind] = 100 - temp[ind]  # invert percentile so "lower = better"
    # Handle missing data by filtering out NaN values
    temp = temp.dropna(axis=1)  # Drop columns with NaN values
    # Compute real values for the region
    real_values = row.loc[row['name'] == region, indicators].copy()

    # Compute medians for each indicator 
    medians = row[indicators].median()

    # Handle missing values consistently
    valid_indicators = [ind for ind in indicators if ind in temp.columns]

    # Close the loop
    r_values = temp[valid_indicators].values.flatten().tolist()
    r_values.append(r_values[0])

    theta_values = ['<br>'.join(textwrap.wrap(ind, width=10)) for ind in valid_indicators]
    theta_values.append(theta_values[0])

    # Build custom hover text
    hover_texts = []
    for ind in valid_indicators:
        raw_val = real_values[ind].values[0]
        median_val = medians[ind]
        percentile_val = temp[ind].values[0]
        if ind in ['GVA per hour worked', 'GFCF per job', 'ICT per job', 'Intangibles per job']:
            hover_texts.append(
                f"<b>Indicator:</b> {ind}<br>"
                f"<b>Value:</b> £{raw_val:,.2f}<br>"
                f"<b>UK Median:</b> £{median_val:,.2f}<br>"
                f"<b>Percentile:</b> {percentile_val:.2f}%"
            )
        else:
            hover_texts.append(
                f"<b>Indicator:</b> {ind}<br>"
                f"<b>Value:</b> {raw_val:,.2%}<br>"
                f"<b>UK Median:</b> {median_val:,.2%}<br>"
                f"<b>Percentile:</b> {percentile_val:.2f}%"
            )
    # Close the loop
    hover_texts.append(hover_texts[0])

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        text=hover_texts,         # supply custom hover text
        hoverinfo="text",         # only show text
        fill='toself',
        name=region,
        line=dict(color=colour, width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=[50]*len(r_values),  # Values for the radar plot
        theta=theta_values,  # Categories (indicators)
        fill='toself',  # Fill the area under the curve
        name=f"UK median",
        mode="lines",  # Only draw lines, no markers
        line=dict(color="rgba(128, 128, 128, 0.5)", width=1),  # Grey line with transparency
        fillcolor="rgba(128, 128, 128, 0.3)",  # Transparent grey fill
        hoverinfo="skip"
    ))

    # Update layout for better visualization
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],  # Adjust the range as needed
                showticklabels=False,  # Remove radial axis ticks
            ),
            angularaxis=dict(
                tickfont=dict(size=10),
            ),
            domain=dict(x=[0.2, 0.8]),  # shrink spider within figure
        ),
        title={
            'text': '<span style="font-weight:normal;">' + 
            '<br>'.join(textwrap.wrap(f"Spider Plot of <b>Productivity Indicators</b> {region} - <i>latest available data",width=55)) +
            '</span>',
            'font': {'size': 14},
        },
        autosize=True,
        template="plotly_white",  # Use a clean white background
        showlegend=False,
        margin=dict(l=10, r=10, t=66, b=80)
    )
    
    return fig

def bar(data, indicator, regions, driver):
    temp = data.loc[(data['name'] == regions[0]), ['year', indicator]].dropna()
    if indicator not in ['GVA per hour worked', 'GFCF per job', 'ICT per job', 'Intangibles per job']:
        temp[indicator] = temp[indicator] * 100  # Multiply indicator values by 100
        unit = '%'
    else:
        unit = '£'
    # Create a bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Indicator values
        name=f"{regions[0]}",
        marker=dict(color="#eb5e5e")  # Customize bar color
    ))
    temp = data.loc[(data['name'] == regions[1]), ['year', indicator]].dropna()
    if indicator not in ['GVA per hour worked', 'GFCF per job', 'ICT per job', 'Intangibles per job']:
        temp[indicator] = temp[indicator] * 100  # Multiply indicator values by 100
    fig.add_trace(go.Bar(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Indicator values
        name=f"{regions[1]}",
        marker=dict(color="#9c4f8b")  # Customize bar color
    ))

    # Update layout for better visualization
    fig.update_layout(
        title={
            'text': '<br>'.join(textwrap.wrap(f"Bar Chart for {regions[0]} against {regions[1]} - <b>{driver}</b>", width=80)),
            'font': {'size': 14},
        },
        xaxis_title="Year",
        yaxis_title=f"{indicator} ({unit})",
        autosize=True,
        template="plotly_white",  # Use a clean white background
        showlegend=False,
        height=450,
        margin=dict(l=100, r=40, t=100, b=100)
    )
    
    return fig