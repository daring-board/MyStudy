.. _theoretical:

.. toctree::
   :maxdepth: 4


Theoretical Document
=========================

Prediction for Stock Price
--------------------------------

We use following time series forcasting model.

.. math::
  y(t) = g(t) + s(t) +  h(t) + \epsilon_{t}

| Here :math:`g(t)` is the trend function.
| :math:`s(t)` represents periodic changes( e.g.. weekly and yearly seasonality).
| :math:`h(t)` represents the effects of holidays which occur on potentially irregular schedules orver one or more days.
| refference [ https://peerj.com/preprints/3190.pdf ]


Distance between stocks
^^^^^^^^^^^^^^^^^^^^^^^^^^

We define the following equation which two stock is similar.

.. math::
 d_{ij} = \sum_{t \in S} | v_{i}(t) - v_{j}(t) |

When we can define distance matrix.

.. math::
 D = (d_{ij})_{i,j \in N}

:math:`N` is set of indies for stocks.

Trand
^^^^^^^

| For stock :math:`i, j \in N`, trand line's value is defined :math:`u_{i}, u_{j} \in R`
| For interval :math:`I(t) = (t, t+k]`,
| we define 'Upward Trand'. That satisfied following conditions.

.. math::
 \sum_{t' \in I(t)}up(t') \ge \alpha k

For all :math:`t' \in I(t)`

* If :math:`u_{i}(t') - u_{j}(t') > 0` then :math:`up(t') = 1`
* otherwise :math:`up(t') = 0`

And we define 'Downward Trand'. That satisfied following conditions.

.. math::
 \sum_{t' \in I(t)}down(t') \le \alpha k

For all :math:`t' \in I(t)`

* If :math:`u_{i}(t') - u_{j}(t') < 0]` then :math:`down(t') = 1`
* otherwise :math:`down(t') = 0`

Information of Stock
^^^^^^^^^^^^^^^^^^^^^^^^^

StockInfo is tuple of :math:`S_{i}(t) = (v_{i}(t), f_{i}(t), \epsilon_{i}, \delta_{i}, \{p_{i}(t)\})`

.. math::
  & v_{i}(t) \in R &: Stock\ Value \\
  & f_i(t) \in \{-1, 0, 1\} &: Trand\ Flag \\
  & \epsilon_i \in (0, 1) &: Confidence Interval \\
  & \delta_i \in A &: Degree\ of\ Reliability \\
  & p_i(t)=(j, k) \in N\times N &: Pair\ Trade\ Flag \\

Pair Trade Flag is defined following conditions.

.. math::
  & p_i(t) = (j, k) & \Leftrightarrow & (f_i(t) \neq f_j(t) \land f_i(t) \neq 0 \land f_j(t) \land 0) \\
  & & & \land (v_i(t+k) \in (v_j(t+k)-\epsilon_j, v_j(t+k)+\epsilon_j)) \\
  & & & \land (v_j(t+k) \in (v_i(t+k)-\epsilon_i, v_i(t+k)+\epsilon_i)) \\
  & & \Leftrightarrow & (f_i(t) \neq f_j(t) \land f_i(t) \neq 0 \land f_j(t) \land 0) \\
  & & & \land (v_j(t+k) =v_i(t+k)) \\

PairTrading
^^^^^^^^^^^^^^^^

Cluster
