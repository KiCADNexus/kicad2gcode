# Data taken from UnionTool website https://www.uniontool.co.jp
# Copyright(C)2005 UNION TOOL CO. All rights reserved.
from units import mm, inch

# Standard drillbit sizes
DRILLBIT_STANDARD_SIZES = [
    0.05, 0.07, 0.09, 0.1 , 0.12, 0.15, 0.2 , 0.25, 0.27, 0.3, 0.35, 0.4, 0.45, 0.5,
    0.55, 0.6 , 0.65, 0.7 , 0.75, 0.8 , 0.85, 0.9 , 0.95, 1.0, 1.05, 1.1, 1.15, 1.2,
    1.25, 1.3 , 1.35, 1.4 , 1.45, 1.5 , 1.55, 1.6 , 1.65, 1.7 , 1.75, 1.8 , 1.85, 1.9,
    1.95, 2   , 2.05, 2.1 , 2.15, 2.2 , 2.25, 2.3 , 2.35, 2.4 , 2.45, 2.5 , 2.55, 2.6,
    2.65, 2.7 , 2.75, 2.8 , 2.85, 2.9 , 2.95, 3   , 3.05, 3.1 , 3.15, 3.175
] * mm

# Standard router bit sizes
ROUTERBIT_STANDARD_SIZES = [
    0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
    2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.175
] * mm

# Lookup table for drill bit in FR4 double sided for spindle up to 100KRpm
# @see https://www.uniontool.co.jp/assets/pdf/product/drill_router/06fr4_100k_ds-4l.pdf
# Key is router diameter in mm
# Value is: 0=Spindle Speed (Rpm), 1=Z Feed (m/min)
DRILLBIT_DATA_LOOKUP = {
    mm(0.05): (10000, 5000 ),
    mm(0.07): (10000, 5000 ),
    mm(0.09): (10000, 5000 ),
    mm(0.1 ): (10000, 5000 ),
    mm(0.12): (10000, 5000 ),
    mm(0.15): (10000, 7500 ),
    mm(0.2 ): (10000, 15000),
    mm(0.25): (10000, 20000),
    mm(0.27): (10000, 20000),
    mm(0.3 ): (10000, 20000),
    mm(0.35): (10000, 23000),
    mm(0.4 ): (95000, 23800),
    mm(0.45): (85000, 21300),
    mm(0.5 ): (75000, 21000),
    mm(0.55): (70000, 19600),
    mm(0.6 ): (65000, 19500),
    mm(0.65): (65000, 19500),
    mm(0.7 ): (60000, 18000),
    mm(0.75): (60000, 18000),
    mm(0.8 ): (57000, 17100),
    mm(0.85): (57000, 17100),
    mm(0.9 ): (55000, 16500),
    mm(0.95): (52000, 15600),
    mm(1   ): (48000, 14400),
    mm(1.05): (47000, 14100),
    mm(1.1 ): (45000, 13500),
    mm(1.15): (43000, 12900),
    mm(1.2 ): (41000, 16400),
    mm(1.25): (39000, 15600),
    mm(1.3 ): (38000, 15200),
    mm(1.35): (36000, 14400),
    mm(1.4 ): (34000, 13600),
    mm(1.45): (32000, 12800),
    mm(1.5 ): (30000, 12000),
    mm(1.55): (30000, 12000),
    mm(1.6 ): (30000, 12000),
    mm(1.65): (30000, 18000),
    mm(1.7 ): (27000, 16200),
    mm(1.75): (27000, 16200),
    mm(1.8 ): (25000, 15000),
    mm(1.85): (25000, 15000),
    mm(1.9 ): (22000, 13200),
    mm(1.95): (22000, 13200),
    mm(2   ): (20000, 12000),
    mm(2.05): (20000, 12000),
    mm(2.1 ): (18000, 10800),
    mm(2.15): (18000, 10800),
    mm(2.2 ): (16000, 9600),
    mm(2.25): (16000, 9600),
    mm(2.3 ): (15000, 9000),
    mm(2.35): (15000, 9000),
    mm(2.4 ): (15000, 9000),
    mm(2.45): (15000, 9000),
    mm(2.5 ): (15000, 9000),
    mm(2.55): (15000, 9000),
    mm(2.6 ): (15000, 9000),
    mm(2.65): (15000, 9000),
    mm(2.7 ): (15000, 9000),
    mm(2.75): (15000, 9000),
    mm(2.8 ): (15000, 9000),
    mm(2.85): (15000, 9000),
    mm(2.9 ): (15000, 9000),
    mm(2.95): (15000, 9000),
    mm(3   ): (15000, 9000),
    mm(3.05): (15000, 9000),
    mm(3.1 ): (15000, 9000),
    mm(3.15): (15000, 9000),
    inch(1/8): (15000, 9000)
}

# Lookup table from Union Tool for various router bits
# @see https://www.uniontool.co.jp/en/product/drill_router/technical_info/router_condi/fr4.html
# Key is router diameter in mm
# Value is: 0=Spindle Speed (Rpm), 1=Table Feed (m/min), 2=Z Feed (m/min), 3=back board depth (mm)
ROUTERBIT_DATA_LOOKUP = {
    mm(0.8): (60000, 0.4, 0.1, 0.75),
    mm(0.9): (53000, 0.6, 0.1, 0.75),
    mm(1.0): (48000, 0.8, 0.1, 0.75),
    mm(1.1): (38000, 0.9, 0.1, 0.75),
    mm(1.2): (35000, 1.0, 0.1, 0.75),
    mm(1.3): (32000, 1.0, 0.1, 0.75),
    mm(1.4): (30000, 1.1, 0.1, 0.75),
    mm(1.5): (29000, 1.1, 0.2, 0.75),
    mm(1.6): (27000, 1.2, 0.2, 0.75),
    mm(1.7): (27000, 1.2, 0.2, 0.75),
    mm(1.8): (25000, 1.2, 0.2, 0.75),
    mm(1.9): (24000, 1.2, 0.3, 1.0),
    mm(2.0): (23000, 1.2, 0.3, 1.0),
    mm(2.1): (22000, 1.2, 0.3, 1.0),
    mm(2.2): (21000, 1.25, 0.3, 1.0),
    mm(2.3): (20000, 1.25, 0.3, 1.0),
    mm(2.4): (20000, 1.3, 0.2, 1.0),
    mm(2.5): (19000, 1.3, 0.2, 1.0),
    mm(2.6): (19000, 1.3, 0.2, 1.0),
    mm(2.7): (18000, 1.3, 0.2, 1.0),
    mm(2.8): (18000, 1.3, 0.2, 1.0),
    mm(2.9): (17000, 1.3, 0.2, 1.0),
    mm(3.0): (17000, 1.3, 0.1, 1.0),
    mm(3.1): (16000, 1.3, 0.1, 1.0),
    inch(1/8): (16000, 1.3, 0.1, 1.0),
}
