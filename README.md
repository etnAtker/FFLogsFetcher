# FFLogs数据统计器
本程序用于统计FFLogs上一些不直接提供的指标，如某个Phase的RD总量，CPM统计，并有一定存储
和从断点继续统计的功能。

## 原理概述

程序统计分为获取report列表和爬取各report的战斗两个步骤，通常获取report列表不需改动。
如果需要统计其他指标则需继承`AbstractTableFetcher`，参照目前有的fetcher写法自行添加，
主流程已在抽象类中配置好，重写三个抽象方法即可。另外还可以自行配置数据统计器，
可照默认自行编写添加。

## 存档

存档/断点继续统计功能由各fetcher的`enable_sav`、`re_fetch`控制。
 - `enable_sav`：是否开启存档功能。
 - `re_fetch`：忽略已有存档，重新从FFLogs上获取数据。

另外，`ReportFetcher`和各`AbstractTableFetcher`的存档逻辑也不同。
 - `ReportFetcher`：除非存档不存在或为空，否则只要开启存档功能，则不会重新抓取数据。
 - `AbstractTableFetcher`：会遍历传入的report，如果存档中存在，则使用存档中的数据，
   否则从FFLogs上获取数据并存入存档。注意，存档中存储的数据为`extract`方法返回的数据，
   并不是返回的原始字典。如果修改了`extract`方法，则存档可能失效。