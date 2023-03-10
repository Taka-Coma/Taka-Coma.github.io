---
title: "Imbalanced Classification"
date: 2020-10-20T22:24:46+09:00
draft: false
background: /images/researches/bgs/imbalance_bg.jpg
---

In classification, class imbalance is a factor that degrades 
the classification performance of many classification methods.
Resampling is one widely accepted approach to the class imbalance;
however, it still suffers from an insufficient data space,
which also degrades performance.
To overcome this, in this paper, an undersampling-based imbalanced
classification framework, MMEnsemble, is proposed that incorporates 
metric learning into a multi-ratio undersampling-based ensemble.
This framework also overcomes a problem with determining the appropriate
sampling ratio in the multi-ratio ensemble method.
It was evaluated by using 12 real-world datasets.
It outperformed the state-of-the-art approaches of metric learning,
undersampling, and oversampling in recall and ROC-AUC,
and it performed comparably with them in terms of Gmean and F-measure metrics.

{{< twoimages
	img1 = /images/researches/imbalance_0.jpg
	img2 = /images/researches/imbalance_1.jpg
>}}

----
### Publications
#### International Journals
- [Takahiro Komamizu](/), "Combining Multi-ratio Undersampling and Metric Learning for Imbalanced Classification", JDI, Vol.2, No.4, pp.462-475, 2021 ([DOI](https://doi.org/10.26421/JDI2.4-5))
- [Takahiro Komamizu](/), Yasuhiro Ogawa, Katsuhiko Toyama, "An Ensemble Framework of Multi-ratio Undersampling-based Imbalanced Classification", JDI, Vol.2, No.1, pp.30-46, 2021 ([DOI](http://www.rintonpress.com/xjdi2/xjdi2-1/030-046.pdf))

#### Japanese Domestic Journals 
- Takahiro Yamakoshi, [Takahiro Komamizu](/), Yasuhiro Ogawa, Katsuhiko Toyama, "Japanese Mistakable Legal Term Correction using Infrequency-aware BERT Classifier", Transactions of the Japanese Society for Artificial Intelligence, Vol.35, No.4, pp.E-K25_1-17, 2020 ([DOI](https://doi.org/10.1527/tjsai.E-K25))

#### International Conferences
- [Takahiro Komamizu](/), "MMEnsemble: Imbalanced Classification Framework Using Metric Learning and Multi-sampling Ratio Ensemble", DEXA, pp.176-188, 2021 ([DOI](https://doi.org/10.1007/978-3-030-86475-0_18), [slide](/pdfs/DEXA2021.pdf))
- [Takahiro Komamizu](/), Risa Uehara, Yasuhiro Ogawa, Katsuhiko Toyama, "MUEnsemble: Multi-ratio Undersampling-Based Ensemble Framework for Imbalanced Data", DEXA, pp.213-228, 2020 ([DOI](https://doi.org/10.1007/978-3-030-59051-2_14), [slide](/pdfs/DEXA2020.pdf))
- Takahiro Yamakoshi, [Takahiro Komamizu](/), Yasuhiro Ogawa, Katsuhiko Toyama, "Japanese Mistakable Legal Term Correction using Infrequency-aware BERT Classifier", IEEE BigData, pp.4342-4351, 2019 ([DOI](https://doi.org/10.1109/BigData47090.2019.9006511))

#### Japanese Domestic Conferences
- 植原 リサ, [駒水 孝裕](/), 小川 泰弘, 外山 勝彦, "弱分類器の調整に基づく不均衡データ向けアンサンブル・フレームワーク", 第12回Webとデータベースに関するフォーラム, pp.81-84, 2019 ([link](https://ipsj.ixsq.nii.ac.jp/ej/index.php?active_action=repository_view_main_item_detail&page_id=13&block_id=8&item_id=199066&item_no=1)) -- {{< awards name="MicroAd Award" url="https://db-event.jpn.org/webdbf2019/award.html" >}}, {{< awards name="FRONTEO Award" url="https://db-event.jpn.org/webdbf2019/award.html" >}}, {{< awards name="FUJITSU Award" url="https://db-event.jpn.org/webdbf2019/award.html" >}}
- 植原 リサ, [駒水 孝裕](/), 小川 泰弘, 外山 勝彦, "不均衡データ分類フレームワークにおけるサンプリング比率の最適化", 第12回データ工学と情報マネジメントに関するフォーラム, pp.F8-2, 2020 -- {{< awards name="Online Presentation Award" url="https://db-event.jpn.org/deim2020/post/awards.html" >}}
