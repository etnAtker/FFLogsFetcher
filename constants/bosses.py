from objects.boss import Boss

# Boss的zone_id和encounter_id可以在网页的url中找到。
# 例如绝O：https://cn.fflogs.com/zone/reports?zone=53&boss=1068&difficulty=0
# 53即为zone_id，1068即为encounter_id。对于绝本这种不分普通/零式难度的boss，可以不填difficulty，或填0。

DSR = Boss(45, 1065)
TOP = Boss(53, 1068)
M4S = Boss(62, 96, 101)
