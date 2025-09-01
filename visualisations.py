import plotly.graph_objects as go
import textwrap

'''Data should only be filtered by indicator and ITL1 regions'''

def gauge(data, region, indicator, selected_year, bounds):
    data = data.loc[data['year'] == int(selected_year), :]
    median = data[indicator].median()
    temp = data.loc[(data['name'] == region), :]
    value = temp[indicator].values[0]
    if value * 1.15 > bounds[1]:
        bounds[1] = value * 1.15
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': '<br>'.join(textwrap.wrap(f"{region} {indicator}, {selected_year}", width=50)),
            'font': {'size': 16}},
        number={'font': {'size': 36},
                'prefix': "£"},  # Adjust the number text size
        gauge={
            'axis': {'range': [bounds[0], bounds[1]]},  # Adjust range as needed
            'bar': {'color': "rgba(10, 10, 10, 0.6)"},  # Set bar color with 50% transparency
            'steps': [
                {'range': [bounds[0], median * 0.95], 'color': "#eb5f5f"},
                {'range': [median * 0.95, median * 1.05], 'color': "#fcbf0b"},
                {'range': [median * 1.05, data[indicator].max() * 1.2], 'color': "#00979e"}
            ],
        }
    ))
    fig.update_layout(
        width=400,  # Set the desired width in pixels
        height=275  # Set the desired height in pixels
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
            '<br>'.join(textwrap.wrap(f"Time Series for {regions[0]} against {regions[1]} - <b>GVA per hour (chained 2022)</b>", width=100)) +
            '</span>',
            'font': {'size': 14},
        },
        xaxis_title="Year",
        yaxis_title=f"GVA per hour (chained 2022) (%)",
        width=800,  # Set the desired width
        height=400,  # Set the desired height
        template="plotly_white",  # Use a clean white background
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.3,  # Position below the chart
            x=0.5,  # Center the legend horizontally
            xanchor="center",  # Anchor the legend at the center
            font=dict(size=16)
        )
    )
    
    return fig

def spider(data, indicators, region, selected_year, colour):
    # Filter the data for the selected region and year
    data = data.loc[data['year'] == int(selected_year), :]
    
    # Compute the medians for each column in the indicators
    medians = data.drop(columns='name').median()[indicators]
    
    # Get the relative values for each indicator
    temp = data.loc[data['name'] == region, indicators]
    temp = (temp / medians) * 100

    # Handle missing data by filtering out NaN values
    temp = temp.dropna(axis=1)  # Drop columns with NaN values
    valid_indicators = temp.columns.tolist()  # Get the corresponding valid indicators

    # Close the loop by appending the first value to the end
    r_values = temp.values.flatten().tolist()
    r_values.append(r_values[0])  # Append the first value to close the loop

    theta_values = valid_indicators
    theta_values.append(theta_values[0])  # Append the first category to close the loop

    # Create a time series plot
    fig = go.Figure()
    # Add the trace for the selected region
    fig.add_trace(go.Scatterpolar(
        r=r_values,  # Values for the radar plot
        theta=theta_values,  # Categories (indicators)
        fill='toself',  # Fill the area under the curve
        name=f"{region} ({selected_year})",
        line=dict(color=colour, width=2),  # Customize line color and width
        hoverinfo="text",  # Enable custom hover text
        hovertemplate="<b>Indicator:</b> %{theta}<br><b>Relative to UK Median:</b> %{r:.2f}%<extra></extra>"  # Custom hover text
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100]*len(r_values),  # Values for the radar plot
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
                range=[20, 200],  # Adjust the range as needed
                showticklabels=False  # Remove radial axis ticks

            )
        ),
        title={
            'text': '<span style="font-weight:normal;">' + 
            '<br>'.join(textwrap.wrap(f"Spider Plot of <b>Productivity Indicators</b> {region} - {selected_year}",width=70)) +
            '</span>',
            'font': {'size': 14},
        },
        width=400,  # Set the desired width in pixels
        height=400,  # Set the desired height in pixels
        template="plotly_white",  # Use a clean white background
        showlegend=False
    )
    
    return fig

def bar(data, indicator, regions, driver):
    temp = data.loc[(data['name'] == regions[0]), ['year', indicator]].dropna()
    if indicator != 'GVA per hour worked':
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
    if indicator != 'GVA per hour worked':
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
        width=750,  # Set the desired width
        height=350,  # Set the desired height
        template="plotly_white",  # Use a clean white background
        showlegend=False
    )
    
    return fig