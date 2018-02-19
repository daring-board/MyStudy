# This Document for pred_fx

## Theoretical document
https://scrapbox.io/mahotox101500-60434823/Prediction_for_Stock_Price

## プログラム1
ペアトレードによる売買最適化システム

### Usage
> ex: python calc_return3.py 5d
> usage: python calc_return3.py [モデル更新期間]

### Classis

1. Class PredVolatGraphs  
  Predict stock price volatility graphs.
  This class uses fbprophet.

2. Class CalcDist  
  Clustering Stocks.

### システム考察

#### 100銘柄を対象に解析を行った場合のハイパーパラメタについて
- 株価の予測値を算出するためのハイパーパラメータの設定は、以下のように取るのがよさそう。
>- 変化点の個数50  
>- スケール0.1  
>- 5日に1度、予測グラフを更新

- ペアトレードの組を作成するためのハイパーパラメータの設定は、以下のような傾向がみられる。
>- クラスタの個数は銘柄数の半分程度が目安。
>- クラスタ数が少ない方がリターンが大きくなりやすいが、マイナスが出やすく大きい場合が多い。
>- クラスタ数が多い場合はリターンが小さいが、マイナスは出にくくなる。
>- クラスタ数が少ないと処理に時間がかかる。

- トレンド決定パラメータkと損益確定Ndまでの日数の関係
>- kとNdは同じ日数である場合が最も利益が出やすい。
>> Ndを指定すると自動的にトレンド決定パラメータkが決まるように修正。

- 株価の予測値によるグラフに対して
>- グラフに対する信頼区間を決定するepsilonに対する係数は小さい方がマイナスになりにくいが、利益も出にくい。(より確実性を求めるため、単純に取引回数が減る)

## プログラム2
強化学習による売買システム

### Usage
> ex: python calc_return7.py 30000 7203 train  
> usage: python calc_return7.py [Loop] [stock] [train or pred]

### 基本概念
強化学習(Q-learning)を適用する。  
状態・行動・報酬について
> * 状態
>> 状態はリスクと保有株式数の組で(risk, stock)としてあらわす。
>> リスクは、前日の株価(終値)から前日までの20日間の平均株価(終値)を
>> 同期間の標準偏差で割った値とする。
> * 行動
>> 行動は『買い』・『売り』・『様子見』と分類する。
>> 更に、『買い』には、『大・中・小』を取れるようにする。
>> 買い：大・中・小 = 5・3・1
>> 売り：-1、様子見：0
> * 報酬
>> 複利型強化学習と呼ばれる手法を用いる。  
>> https://www.jstage.jst.go.jp/article/tjsai/26/2/26_2_330/_pdf

## プログラム3
強化学習による売買システム(DQN: Deep Q-learning)

### Usage
> ex: python calc_return5.py 1000 7203 train  
> usage: python calc_return5.py [Loop] [stock] [train or pred]

### DQN(Deep Q-learning)について

https://qiita.com/icoxfog417/items/242439ecd1a477ece312
