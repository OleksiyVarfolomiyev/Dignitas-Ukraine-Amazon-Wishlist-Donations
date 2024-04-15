import data_aggregation_tools as da
import ETL as etl
import plotly.graph_objects as go
import data_aggregation_tools as da
import plotly.express as px
from plotly.subplots import make_subplots

def hide_axis_title(fig):
    fig.update_layout(margin=dict(l=0, r=0, b=0), yaxis_title='')
    fig.update_layout(xaxis_title='')
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
def fig_add_mean(fig, val, col):
    """ Add a horizontal line for the mean"""
    mean_value = val[col].mean()
    fig.add_shape(
        type='line',
<<<<<<< HEAD
        #x0 = min(val.index.strftime("%Y-%m-%d")),  
        #x1 = max(val.index.strftime("%Y-%m-%d")),  
        x0 = val.index[0],  
        x1 = val.index[-1],  
        y0=mean_value,
        y1=mean_value,
        name='mean',
        line=dict(color='blue', dash = 'dot')  
=======
        #x0 = min(val.index.strftime("%Y-%m-%d")),
        #x1 = max(val.index.strftime("%Y-%m-%d")),
        x0 = val.index[0],
        x1 = val.index[-1],
        y0=mean_value,
        y1=mean_value,
        name='mean',
        line=dict(color='blue', dash = 'dot')
>>>>>>> origin/main
    )

def pie_plot(data, col, names, title, show):
    """Ring plot"""
<<<<<<< HEAD
    fig = px.pie(data, 
             values = col, 
             names = names, 
=======
    fig = px.pie(data,
             values = col,
             names = names,
>>>>>>> origin/main
             hole=0.5,
             title = title
             )
    fig.update_layout(legend=dict(orientation='h', x=0.2, y=-0.1))
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def subplot_horizontal(fig1, fig2, rows, cols, type1, type2, title1, title2, show):
<<<<<<< HEAD
    fig = make_subplots(rows=rows, cols=cols, 
                    specs=[[{'type': type1}, {'type': type2}]], 
=======
    fig = make_subplots(rows=rows, cols=cols,
                    specs=[[{'type': type1}, {'type': type2}]],
>>>>>>> origin/main
                    subplot_titles=[title1, title2])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_layout(grid={'columns': cols, 'rows': rows, 'pattern': "independent"})
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def stack_bar_plot(df, title, show):
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    df['Date'] = df['Date'].astype(str)
    mean_value = df[df.columns[1:]].sum(axis=1).mean()

    fig = go.Figure()

    for column in df.columns[1:]:
        fig.add_trace(
        go.Bar(name=column, x = df['Date'], y = df[column],
               text = df[column].apply(etl.format_money)
        ))
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
    fig.update_layout(
    barmode='stack',
    title = title,
    #legend=dict(orientation='h', x=0.2, y=-0.1),
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
<<<<<<< HEAD
    
    if show:
        fig.show(renderer="notebook")
    else: 
        return fig

def chart_by_period(ds, categories, period, title):
    """Stack bar plot of Donations Total Cost by Product by Period (d, w, m)"""
    by_category = da.sum_by_period_by_category(categories, period, ds, 'Product').fillna(0)
    if period == 'w':
=======

    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def chart_by_period(df, categories, period, title):
    """Stack bar plot of Donations Total Cost by Product by Period (d, w, m)"""
    by_category = da.sum_by_period_by_category(categories, period, df, 'Product').fillna(0)
    if period == 'W':
>>>>>>> origin/main
        by_category['Date'] = by_category['Date'].astype(str).str.split('/').str[0]
    return stack_bar_plot(by_category, title, False)