import plotly.offline as pyo
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def earning(y_pred, y_visu, up=0, down=0, spread=0.00050, leverage=1):
    
    # Initialization
    l = len(y_pred)
    
    earning = np.zeros((l,1))
    rise = np.zeros((l,1))
    drop = np.zeros((l,1))
    
    # Earning
    for i in range(l):
        if y_pred[i][0]>up:
            earning[i][0] = (y_visu[i][0]-spread)*leverage
            rise[i][0] = (y_visu[i][0]-spread)*leverage
        elif y_pred[i][0]<-down:
            earning[i][0] = (-y_visu[i][0]-spread)*leverage
            drop[i][0] = (-y_visu[i][0]-spread)*leverage
            
            
    # Growth
    coef = 1
    coef_ = np.zeros((l,1))
    
    for i in range(l):
        coef = coef * (1+earning[i][0])
        coef_[i][0] = (coef-1)*100
        
    percentage = (coef-1)*100
    
    
    # Statisitcs
    mean = np.mean(earning[earning!=0])
    std = np.std(earning[earning!=0])
    std_down = np.std(earning[earning<0])
    
    Sharpe = mean/std
    
    Sortino = mean/std_down
    
    
    
    # Metrics
    sum_rise_earning = np.sum(rise)*100
    sum_down_earning = np.sum(drop)*100
    
    min_rise_earning = np.min(rise, axis=0)[0]*100
    max_rise_earning = np.max(rise, axis=0)[0]*100
    
    min_drop_earning = np.min(drop, axis=0)[0]*100
    max_drop_earning = np.max(drop, axis=0)[0]*100
    
    
    #Accuracy
    
    count_true = 0
    count_false = 0
    p = 0
    
    for i in range(l):
        if earning[i][0]>0:
            count_true += 1
        elif earning[i][0]<0:
            count_false += 1
    
    if count_true == 0 and count_false == 0:
        p = "Error"
    else:
        p = round(count_true/(count_false+count_true)*100,2)
        
    earnings = earning
    k = np.array([k for k in range(len(y_pred))])
    k = tuple(k.reshape(1,-1)[0])
    earning = tuple(earning.reshape(1,-1)[0])
    y_pred = tuple(y_pred.reshape(1,-1)[0])
    y_visu = tuple(y_visu.reshape(1,-1)[0])
    coef_ = tuple(coef_.reshape(1,-1)[0])


    Rise = len(earnings[0.035<earnings])
    rise = len(earnings[0.005<earnings]) - len(earnings[0.035<earnings])
    Drop = len(earnings[earnings<-0.035])
    drop = len(earnings[-0.035<earnings]) - len(earnings[-0.005<earnings])
    stagnation = len(earnings[-0.005<earnings]) - len(earnings[0.005<earnings])

    liste = [Rise, rise, stagnation, drop, Drop]
    signe = [len(earnings[earnings<0]), len(earnings[earnings>0])]
    initialization = pds.DataFrame(np.array([["Percentage of earning","{}%".format(round(percentage))],
                                                ["Sharpe ratio", round(Sharpe,6)],
                                                ["Sortino ratio",round(Sortino,6)],
                                            ["Sum upward earning","{}%".format(round(sum_down_earning))],
                                             ["Sum downward earning","{}%".format(round(sum_rise_earning))],
                                             ["Earning per trade", "{}%".format(round(np.mean(earnings)*100,3))]

                                            ]), 
                                   columns = ["Indicator", "Value"])


    import plotly.offline as pyo
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots

    # Initialization
    background = "#555555"
    specs = [[{"type":"table"}, {"type":"domain"}, {"type":"domain"}],
             [{"type":"Scatter"}, {"type":"Histogram"},{"type":"Scatter"}

]]


    figure = make_subplots(rows=2, cols=3, subplot_titles=("Table", "Pie", "Pie","Scatter", "Histogram", "Graphe"),specs=specs)

    # Create the graphics
    trace_1 = go.Table(
        header=dict(values=list(initialization.columns),
                    fill_color='#71C942',
                    align='center'),
        cells=dict(values=[initialization.Indicator, initialization.Value],
                   fill_color='#747474',
                   align='center',
                  height=50))

    trace_2 = go.Pie(labels=["earning < -3.50%", "earning < -0.5%", "-0.5%<earning<0.5%", "0.5% < earning", "3.50% < earning"], values=liste, name="Gain", hole=0.5, hoverinfo="label+percent+name")

    trace_3 = go.Pie(labels=["Loss", "Profit"], values=signe, name="Gain", hole= 0.5, hoverinfo = "label+percent+name")

    trace_4 = go.Scatter(x=y_pred, y=y_visu, mode="markers",  marker=dict(color="#B95AFF"), name="Predicted/True Variation")

    trace_5 = go.Histogram(x=earning, marker=dict(color="#51F1FF"), name="Distibution")

    trace_6 = go.Scatter(x=k, y=coef_,  marker=dict(color="#90FF55"), mode="lines", name="Developmnt of capital")


    # Add trace on the subplots
    figure.add_trace(trace_1, row = 1, col = 1)
    figure.add_trace(trace_2, row = 1, col = 2)
    figure.add_trace(trace_3, row = 1, col = 3)
    figure.add_trace(trace_4, row = 2, col = 1)
    figure.add_trace(trace_5, row = 2, col = 2)
    figure.add_trace(trace_6, row = 2, col = 3)


    # Change x axis
    figure.update_xaxes(title_text="Predicted asset variation", row=2, col=1)
    figure.update_xaxes(title_text="Earning in %", row=2, col=2)
    figure.update_xaxes(title_text="", row=2, col=3)


    # Change y axis
    figure.update_yaxes(title_text="True asset variation", row=2, col=1)
    figure.update_yaxes(title_text="Frequency", row=2, col=2)
    figure.update_yaxes(title_text="Cumulative growth %", row=2, col=3)


    # Layout
    figure.update_layout(

        plot_bgcolor=background, 

        paper_bgcolor=background, 

        font={"color":"#FFFFFF"},

        annotations=[dict(text="", x=0.50, y=0.79, font_size=20, showarrow=False),
                     dict(text="", x=0.85, y=0.79, font_size=20, showarrow=False)],

        height=850)





    pyo.plot(figure, filename="Backtesting")

        #return percentage, earning, coef_, sum_down_earning, sum_rise_earning, Sharpe, Sortino, mean*100 