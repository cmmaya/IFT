## Description
The purpose is to compare the algorithms for Swap aggregation via Coincidence of wants used by CoW protocol and our optimization model. 

> The basic idea behind the CoW model is to find pairs of trading orders that directly complement each other. For example, if one party wants to sell a certain amount of cryptocurrency A for cryptocurrency B, and another party wants to buy the same amount of A in exchange for B, they match perfectly and can complete their trades immediately. This first step helps in quickly clearing the market of straightforward, matchable orders, reducing the complexity of the remaining order book. However, not all orders will find a direct match in this initial step. The remaining orders, which couldn't be matched directly, are then handled in a batch auction. In a batch auction, all orders are considered together at the end of a set time period. This method calculates the exchange prices for all asset pairs simultaneously. What makes it unique is that it aims to set a uniform clearing price for trades between identical asset pairs during each batch period. This uniform price ensures that all trades between the same pair of currencies occur at the same rate, providing consistency and fairness in pricing. For instance, if multiple traders want to trade between cryptocurrency A and B during a batch period, the system calculates a single exchange rate for A to B that best satisfies the most orders, potentially adjusting the quantities to be traded so that as many traders as possible can participate in the trade. This approach can also facilitate *ring trades*, where multiple currencies are traded in a loop (e.g., A to B, B to C, and C back to A), which can significantly increase the liquidity of the market. 

**solver competition**
In the case of CoW protocol. They conduct a competition among solvers and select the "winning" solver for each batch of orders. The winning solver is the one that maximizes the surplus for traders. 

In our case, the variables being optimized are the exchange rates 𝑝 and the amounts x and 𝑦 of each asset being bought and sold, respectively. **The goal is to maximize the total traded volume.** For technical details, refer to the [explanation](https://hackmd.io/@pkzpf-CcSQCT_9b6FGtTPg/r1FU_HhD0).

## Methodology
In order to compare the volume traded, we obtained data from multiple batch auctions using [CoW protocol's Order Book API](https://docs.cow.fi/cow-protocol/reference/apis/orderbook).

Each auction includes a list of intents that are queued to be addressed by solvers competing to maximize the surplus which have an structure similar to this: 

```json
# Batch Auction structure
{
  "id": 0,
  "block": 0,
  "latestSettlementBlock": 0,
  "orders": [
    {
      "uid": "0xff2e2e54d178997f173266817c1e9ed6fee1a1aae4b43971c53b543cffcc2969845c6f5599fbb25dbdd1b9b013daf85c03f3c63763e4bc4a",
      "sellToken": "0x6810e776880c02933d47db1b9fc05908e5386b96",
      "buyToken": "0x6810e776880c02933d47db1b9fc05908e5386b96",
      "sellAmount": "1234567890",
      "buyAmount": "1234567890",
      "validTo": 0,
      "kind": "buy",
      "receiver": "0x6810e776880c02933d47db1b9fc05908e5386b96",
      "owner": "0x6810e776880c02933d47db1b9fc05908e5386b96",
      "partiallyFillable": true,
      "executed": "1234567890",


      "sellTokenBalance": "erc20",
      "buyTokenBalance": "erc20",
      "class": "market",
      
      "protocolFees": [
        {
          "surplus": {
            "factor": 0.5,
            "maxVolumeFactor": 0.01
          }
        }
      ]
    }
  ]
}
```

The solver competition structure involves ranked solutions proposed by solvers for each auction identified by a number.

```json
{
  "auctionId": 9119405,
  "transactionHash": "0xd27c2e2e7b93a095f9757026cb0c019054f79682c3bc683cbedf9af982d2610c",
  "auctionStartBlock": 20277743,
  "competitionSimulationBlock": 20277746,
  "auction": {
    "orders": [
      "solutions": [
        {
          "solver": "copiumcapital",
          "solverAddress": "0x16c473448e770ff647c69cbe19e28528877fba1b",
          "score": "2619094225286",
          "ranking": 1,
          "clearingPrices": {
            "0x2b591e99afe9f32eaa6214f7b7629768c40eeb39": "18446744073709551616",
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "4652009065799291"
          },
          "orders": [
            {
              "id": "0xdf7545e22642d198a247327486bfa9171b6d1b3b2f66ae76f134f55fef9072ba340a637a0704ea65aa51d5d59f2dc574be5d1976668ed2bc",
              "sellAmount": "59220000000000000",
              "buyAmount": "14006096268092"
            }
          ],
        }
      ]
    ]
  }
}
```
Reconstructing the JSON files as tables shows the input information for the algorithm.
| uid        | amount_usd | kind | class | token_bought_symbol | token_sold_symbol | token_bought_amount | token_sold_amount | token_bought_price_usd | token_sold_price_usd | fulfill | fee |
|------------|------------|------|-------|---------------------|-------------------|---------------------|-------------------|------------------------|----------------------|---------|-----|
| 0x9c05cf... | 5155.50    | sell | limit | WPOKT               | WETH              | 120000.00           | 1.50              | 0.04                   | 3437.00              | 0       | 0   |
| 0xc713aa... | 405.06     | sell | limit | OSAK                | WETH              | 1616312604.04       | 0.12              | 2.48e-7                   | 3437.00              | 0       | 0   |
| 0x7b4ef0... | 2003.38    | sell | limit | SAFE                | WETH              | 1417.67             | 0.58              | 1.40                   | 3437.00              | 0       | 0   |
| 0x3230f5... | 144.73     | sell | limit | WETH                | FET               | 0.04                | 104.01            | 3437.00                | 1.39                 | 0       | 0   |


## Files description
* **dataframes** folder contains csv files with auction information downloaded with download_multiple_auctions.py file and organized with get_orderBook_data.py
* **optimize_swap.py** holds the optimizing algorithm
* **get_DUNE_data.py** request info from DUNE API and **dune_metrics.py** creates a report based on the metrics.
* **test_fulfilled_proportion** runs the algorith for multiple auctions and outputs different metrics to compare both algorithms
* **metrics_report** folder contains code related to graphs and data useful for the final report.
