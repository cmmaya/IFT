import pandas as pd
import numpy as np
from gekko import GEKKO  
import yfinance as yf
import tqdm as tqdm

def optimizeSwap(df: pd.DataFrame):
    def omega():
        #builds matrices
        tokens_unique=set(df.token_bought_symbol).union(df.token_sold_symbol)
        N_swaps=len(df)
        N_coins=len(tokens_unique)
        tokens={}
        ii=0
        for n in tokens_unique:
            tokens[n]=ii
            ii=ii+1
        T_buy=np.zeros((N_swaps,N_coins))
        T_sell=np.zeros((N_swaps,N_coins))
        omegas=[]
        
        
        list_of_coins=pd.DataFrame(tokens,index=[0]).T
        cps=[]
        for n in range(len(list_of_coins)):
            try:
                cp=yf.download(f'{list_of_coins.index[n]}-USD')['Close'].iloc[-1]
            except:
                cp=0
            cps.append(cp)
        list_of_coins['current_price']=cps
        list_of_coins

        # populates matrices
        for n in range(N_swaps):
            a=df.iloc[n]
            A=a['token_bought_symbol']
            B=a['token_sold_symbol']
            i=tokens[A]
            j=tokens[B]
            x_bar=a['token_bought_amount']
            T_buy[n,i]=1
            T_sell[n,j]=1
            pi=(0.98 + 0.04*np.random.random())*a['price_token_bought']/a['price_token_sold']
            
            order_kind = f"{a['class']}_{a['kind']}"

            # Handle order types
            if (order_kind == "limit_sell"):
                max_amount_buy = x_bar
                max_amount_sell = np.inf
            elif (order_kind == "limit_buy"):
                max_amount_buy = np.inf
                max_amount_sell = x_bar
            else:
                max_amount_buy = x_bar
                max_amount_sell = np.inf

            w={
                'buy':A,
                'sell':B,
                'max_amount_buy':max_amount_buy,
                'max_amount_sell':max_amount_sell,
                'max_rate':pi,
                'rate_A':a['price_token_bought'],
                'rate_B':a['price_token_sold'],
                'rate_AB':a['price_token_bought']/a['price_token_sold'],
                'id':n
                }
            omegas.append(w)
            omega_df=pd.DataFrame(omegas)   
        return tokens, omega_df, list_of_coins, T_buy, T_sell

    def optimize(tokens,omega_df,list_of_coins,T_buy,T_sell):
        # Handle nan values by filling them with zeros
        omega_df.fillna(0, inplace=True)
        list_of_coins.fillna(0, inplace=True)

        n=len(tokens)
        N=len(omega_df)
        p0=list_of_coins['current_price'].values
        pj=list_of_coins['current_price'].values
        pi=omega_df['max_rate'].values
        x_bar=omega_df['max_amount_buy'].values
        y_bar=omega_df['max_amount_sell'].values
        #creates variables, and transforms infinities to large numbers, for handling of the optimizer
        x_bar[x_bar==np.inf]=1e10
        y_bar[y_bar==np.inf]=1e10
        pi[pi==np.inf]=1e10
        M=2*N+n
        p_upper_factor=1.01
        p_lower_factor=0.99
        m = GEKKO(remote=False)

        x = [m.Var() for i in range(N)]
        y=  [m.Var() for i in range(N)]
        p=  [m.Var() for i in range(n)] 

        #12b
        for j in range(n):
            m.Equation(m.sum([T_buy[i,j]*x[i] for i in range(N)])-
                    m.sum([T_sell[i,j]*y[i] for i in range(N)])==0   )
        #12c and 12d and 12g
        for i in range(N):
            m.Equation(x[i]*m.sum([T_buy[i,j]*p[j] for j in range(n)])-
                    y[i]*m.sum([T_sell[i,j]*p[j] for j in range(n)])==0)
            
            m.Equation(pi[i]*x[i]>=y[i])
     
        #  bounds on the variables
        for i in range(N):
            x[i].lower=0
            x[i].upper=x_bar[i]
            #x[i].value=0#r*x_bar[i]

            y[i].lower=0
            y[i].upper=y_bar[i]
            #y[i].value=0#r*y_bar[i]

        for j in range(n):
            p[j].lower=p0[j]*p_lower_factor
            p[j].upper=p0[j]*p_upper_factor
            #p[j].value=p0[j]

        # defines objective. The minus is taken since the optimier fiunds the minimum 
        m.Obj(-0.5*m.sum([x[i]*m.sum([T_buy[i,j]*p[j] for j in range(n)]) for i in range(N)])
            -0.5*m.sum([y[i]*m.sum([T_sell[i,j]*p[j] for j in range(n)]) for i in range(N)])      )

        #Set global options
        m.options.SOLVER = 1 # APOPT=1, IPOPT=3
        m.options.IMODE = 3 #steady state optimization
        m.options.MAX_ITER=200
        #Solve simulation
        m.solve()

        solution=[]

        for i in range(N):
            
            den=np.min([omega_df['max_amount_buy'][i],omega_df['max_amount_sell'][i]])
            b_or_s=np.argmin([omega_df['max_amount_buy'][i],omega_df['max_amount_sell'][i]])

            if b_or_s==0:
                num=x[i][0]

            else:
                num=y[i][0]
            token=omega_df['buy'].iloc[i]
            jb=np.argmax(list_of_coins.index==token)
            token=omega_df['sell'].iloc[i]
            js=np.argmax(list_of_coins.index==token)

            fulfilled_percentage=num/den*100
 
            solution.append({
            'buy':omega_df['buy'][i],   
            'sell':omega_df['sell'][i],
            'fulfilled_percentage':fulfilled_percentage,
            'price buy':p[jb][0],
            'price sell':p[js][0]
            })

        sol=pd.DataFrame(solution)
        return sol

    return optimize(*omega())
