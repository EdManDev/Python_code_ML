import numpy as np
import matplotlib.pyplot as plt
def earning(tx_pred, tx_visu, sb=0.00, sh=0.00, spread=0.00050, leverage=1):
    # Initialisation
    l = len(tx_pred)
    earning = np.zeros(l).reshape(l,1)
    rise = np.zeros(l).reshape(l,1)
    drop = np.zeros(l).reshape(l,1)
    count_true = 0
    count_false = 0
    p = 0
    
    #Earning
    for i in range(l):
        if tx_pred[i][0]>sh:
            earning[i][0] = (tx_visu[i][0]-spread)*leverage
            rise[i][0] = (tx_visu[i][0]-spread)*leverage
        if tx_pred[i][0]<-sb:
            earning[i][0] = (-tx_visu[i][0]-spread)*leverage
            drop[i][0] = (-tx_visu[i][0]-spread)*leverage
    
    #Statistics
    moyenne = np.mean(earning[earning!=0])
    ecart_type = np.std(earning[earning!=0])
    
    # Growth
    coef = 1
    coef_ = np.zeros(l).reshape(l,1)

    for i in range(l):
        coef *= (1+earning[i][0])
        coef_[i][0] = coef
    pourcentage = (coef-1)*100
    
    
    sharpe = moyenne/ecart_type
    
    sortino = np.mean(earning[earning!=0])/np.std(earning[earning<0])
    
    #Metrics
    sum_rise_earning = round(sum(rise)[0]*100,2)
    sum_drop_earning = round(sum(drop)[0]*100,2)
    
    
    max_rise_earning = round(np.max(rise, axis=0)[0]*100,2)
    min_rise_earning = round(np.min(rise, axis=0)[0]*100,2)
    
    
    max_drop_earning = round(np.max(drop, axis=0)[0]*100,2)
    min_drop_earning = round(np.min(drop, axis=0)[0]*100,2)
    
    for i in range(l):
        if earning[i][0]>0:
            count_true += 1
        elif earning[i][0]<0:
            count_false += 1
    
    if count_false == 0 and count_true == 0:
        p="Error"
    else:
        p = count_true/(count_false+count_true)
    
    # Affichage
    
    print("------------------ Initialization -----------------------")
    print("Rising threshold:", sh)
    print("Lower threshold:", sb)
    print("Spread:", spread)
    print("Leverage:",leverage)
    print("                                                           ")
    print("---------------------- Metrics ----------------------------")
    print("Accuracy", round(p*100,2), "%")
    print("Pourcentage of earnings:", round(np.sum(earning)*100,2), "%")
    print("Poucentage composed:", round(pourcentage,2), "%")
    print("Ratio earning/trade:", round(moyenne*100,2), "%")
    print("Standard deviation of earning:", round(ecart_type*100,2), "%")
    print("Sharpe ratio:", round(sharpe,6))
    print("Sortino ratio:", round(sortino,6))
    print("                                                           ")
    print("-------------------- Other Data -----------------------")
    print("Sum rise earning:", sum_rise_earning, "%")
    print("Sum drop earning:", sum_drop_earning, "%")
    print("Max rise earning:",max_rise_earning, "%")
    print("Min rise earning:",min_rise_earning, "%")
    print("Max drop earning:",max_drop_earning, "%")
    print("Min drop earning:",min_drop_earning, "%")
    print("                                                           ")
    print("-------------------- Distribution -----------------------")
    plt.title("Distribution")
    plt.hist(earning[earning!=0]*100,bins=55)
    plt.axvline(0, color="black")
    plt.xlabel("Percentage")
    plt.show()
    print("                                                           ")
    print("-------------------- Growth of investment -----------------------")
    plt.plot((coef_-1)*100,color="green")
    plt.title("Investment")
    plt.ylabel("Earning")
    plt.show()