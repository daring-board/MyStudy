# This Document for pred_fx

## Theoretical document
https://scrapbox.io/mahotox101500-60434823/Prediction_for_Stock_Price

## Classis

1. Class PredVolatGraphs  
  Predict stock price volatility graphs.
  This class uses fbprophet.

2. Class CalcDist  
  Clustering Stocks.

## システム考察

### 100銘柄を対象に解析を行った場合のハイパーパラメタについて
- 株価の予測値を算出するためのハイパーパラメータの設定は、以下のように取るのがよさそう。
>- 変化点の個数50  
>- スケール0.1  
>- 5日に1度、予測グラフを更新

- ペアトレードの組を作成するためのハイパーパラメータの設定は、以下のような傾向がみられる。
>- クラスタの個数は銘柄数の半分程度が目安。
>- クラスタ数が少ない方がリターンが大きくなりやすいが、マイナスが出やすく大きい場合が多い。
>- クラスタ数が多い場合はリターンが小さいが、マイナスは出にくくなる。
>- クラスタ数が少ないと処理に時間がかかる。
