import data_aggregation_tools as da
import ETL as etl
import plotly
import plotly.graph_objects as go
import data_aggregation_tools as da
import plotly.express as px
from plotly.subplots import make_subplots

def hide_axis_title(fig):
    fig.update_layout(margin=dict(l=0, r=0, b=0), yaxis_title='')
    fig.update_layout(xaxis_title='')
    
def fig_add_mean(fig, val, col):
    """ Add a horizontal line for the mean"""
    mean_value = val[col].mean()
    fig.add_shape(
        type='line',
        #x0 = min(val.index.strftime("%Y-%m-%d")),  
        #x1 = max(val.index.strftime("%Y-%m-%d")),  
        x0 = val.index[0],  
        x1 = val.index[-1],  
        y0=mean_value,
        y1=mean_value,
        name='mean',
        line=dict(color='blue', dash = 'dot')  
    )
    
def subplot_horizontal(fig1, fig2, rows, cols, type1, type2, title1, title2, show):
    fig = make_subplots(rows=rows, cols=cols, 
                    specs=[[{'type': type1}, {'type': type2}]], 
                    subplot_titles=[title1, title2])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_layout(grid={'columns': cols, 'rows': rows, 'pattern': "independent"})
    if show:
        fig.show(renderer="notebook")
    else:
        return fig
    
def subplot_vertical(val, fig1, fig2, rows, cols, type1, type2, barmode, title1, title2, show):
    fig = make_subplots(rows=rows, cols=cols, 
                    specs=[[{'type': type1}], [{'type': type2}]], 
                    subplot_titles=[title1, title2])
    
    if not val.empty:
        fig_add_mean(fig, val, 'UAH')
    
    fig.update_layout(
    barmode = barmode,
    legend=dict(orientation='h', x=0.2, y=-0.1))
    
    for trace in fig1.data:
        fig.add_trace(trace, row=1, col=1)

    for trace in fig2.data:
        fig.add_trace(trace, row=2, col=1)
    
    fig.update_layout(grid={'columns': cols, 'rows': rows, 'pattern': "independent"})
    fig.update_layout(height=800)
        
    if show:
        fig.show(renderer="notebook")
    else:
        return fig
    
def pie_plot(data, col, title, show):

    fig = px.pie(data, 
             values = col, 
             names = data.index, 
             hole=0.5,
             title = title)
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def bar_plot(val, col, fig_title, show):
    fig = px.bar(val, x = val.index, y = col, 
            color = col, 
            text_auto = '.2s',
            title = fig_title
            )
    fig_add_mean(fig, val, col)
    hide_axis_title(fig)
    if show:
        fig.show(renderer="notebook")
    else: 
        return fig

def stack_bar_plot(df, title, show):
    
    df['Date'] = df['Date'].astype(str)
    mean_value = df[df.columns[1:]].sum(axis=1).mean()

    fig = go.Figure()

    for column in df.columns[1:]:
        fig.add_trace(
        go.Bar(name=column, x = df['Date'], y = df[column],
               text = df[column].apply(etl.format_money)
        ))
        
    fig.update_layout(
    barmode='stack',
    title = title,
    legend=dict(orientation='h', x=0.2, y=-0.1),
    # Add a horizontal line at the mean value
        shapes=[
            dict(
                type='line',
                x0=df['Date'].iloc[0],
                x1=df['Date'].iloc[-1],
                y0=mean_value,
                y1=mean_value,
                line=dict(color='blue', dash='dot')
            )
        ]
    )
    
    if show:
        fig.show(renderer="notebook")
    else: 
        return fig