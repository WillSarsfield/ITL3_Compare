import plotly.graph_objects as go

'''Data should only be filtered by indicator and ITL1 regions'''

def gauge(data, region, indicator, selected_year, bounds):
    data = data.loc[data['year'] == int(selected_year), :]
    median = data[indicator].median()
    temp = data.loc[(data['name'] == region), :]
    value = temp[indicator].values[0]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"{region} {indicator}, {selected_year}",
            'font': {'size': 12}},
        number={'font': {'size': 30}},  # Adjust the number text size
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
        height=250  # Set the desired height in pixels
    )
    return fig

def time_series(data, regions, indicator):
    data = data.dropna()
    temp = data.loc[(data['name'] == regions[0]), :]
    
    # Create a time series plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Value
        mode='lines+markers',  # Line and markers
        name=f"{regions[0]}",
        line=dict(color="#eb5e5e", width=2),  # Customize line color and width
        marker=dict(size=6)  # Customize marker size
    ))
    temp = data.loc[(data['name'] == regions[1]), :]
    
    fig.add_trace(go.Scatter(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Value
        mode='lines+markers',  # Line and markers
        name=f"{regions[1]}",
        line=dict(color="#9c4f8b", width=2),  # Customize line color and width
        marker=dict(size=6)  # Customize marker size
    ))
    
    # Update layout for better visualization
    fig.update_layout(
        title={
            'text': f"Time Series for {regions[0]} against {regions[1]} - {indicator}",
            'font': {'size': 14},
        },
        xaxis_title="Year",
        yaxis_title="Value",
        width=800,  # Set the desired width
        height=320,  # Set the desired height
        template="plotly_white"  # Use a clean white background
    )
    
    return fig

def spider(data, indicators, region, selected_year, colour):
    # Filter the data for the selected region and year
    data = data.loc[data['year'] == selected_year, :]
    
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
        line=dict(color=colour, width=2)  # Customize line color and width
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
            'text': f"Spider Plot for {region} - {selected_year}",
            'font': {'size': 14},
        },
        width=400,  # Set the desired width in pixels
        height=300,  # Set the desired height in pixels
        template="plotly_white"  # Use a clean white background
    )
    
    return fig

def bar(data, indicator, regions):
    temp = data.loc[(data['name'] == regions[0]), ['year', indicator]].dropna()
    # Create a bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Indicator values
        name=f"{regions[0]}",
        marker=dict(color="#eb5e5e")  # Customize bar color
    ))
    temp = data.loc[(data['name'] == regions[1]), ['year', indicator]].dropna()
    fig.add_trace(go.Bar(
        x=temp['year'],  # X-axis: Year
        y=temp[indicator],  # Y-axis: Indicator values
        name=f"{regions[1]}",
        marker=dict(color="#9c4f8b")  # Customize bar color
    ))

    # Update layout for better visualization
    fig.update_layout(
        title={
            'text': f"Bar Chart for {regions[0]} against {regions[1]} - {indicator}",
            'font': {'size': 14},
        },
        xaxis_title="Year",
        yaxis_title=indicator,
        width=800,  # Set the desired width
        height=350,  # Set the desired height
        template="plotly_white"  # Use a clean white background
    )
    
    return fig