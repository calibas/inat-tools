#!/usr/bin/env python3
"""
Label lookup functions for iNaturalist API data
Contains dictionaries and lookup functions for term labels, value labels, and place labels
"""

from typing import Optional

# iNaturalist annotation term labels
term_labels = {
    1: "Life Stage",
    9: "Sex",
    12: "Plant Phenology",
    17: "Alive or Dead",
    22: "Evidence of Presence",
    36: "Leaves"
}

# iNaturalist annotation value labels
# TODO: Double-check these, copied from
# https://forum.inaturalist.org/t/how-to-use-inaturalists-search-urls-wiki-part-2-of-2/18792
# This list has the same values:
# https://github.com/pyinat/pyinaturalist/blob/36b23a688ccfade3a6f438f9ecb3ab770ec9351a/test/sample_data/get_controlled_terms.json#L45
# Missing Established annotation?
# See: https://www.inaturalist.org/pages/annotationvalues
value_labels = {
    2: "Adult",
    3: "Teneral",
    4: "Pupa",
    5: "Nymph",
    6: "Larva",
    7: "Egg",
    8: "Juvenile",
    16: "Subimago",

    10: "Female",
    11: "Male",
    # 20:"Cannot Be Determined",

    13: "Flowering",
    14: "Fruits or Seeds",
    15: "Flower Buds",
    21: "No Flowers or Fruits",

    18: "Alive",
    19: "Dead",
    20: "Cannot Be Determined",

    23: "Feather",
    24: "Organism",
    25: "Scat",
    26: "Track",
    27: "Bone",
    28: "Molt",
    29: "Gall",
    30: "Egg",
    31: "Hair",
    32: "Leafmine",
    35: "Construction",

    37: "Breaking Leaf Buds",
    38: "Green Leaves",
    39: "Colored Leaves",
    40: "No Live Leaves"
}

# See fetch_place_info() function
place_labels: dict[int, dict] = {
    1: {"name": "United States", "bbox_area": 6349.38211750929, "place_type": 12},
    2: {"name": "Massachusetts", "bbox_area": 6.202817939097, "place_type": 8},
    3: {"name": "Nebraska", "bbox_area": 26.2511947726, "place_type": 8},
    4: {"name": "Delaware", "bbox_area": 1.117451969472, "place_type": 8},
    5: {"name": "District of Columbia", "bbox_area": 0.0429567372, "place_type": 8},
    6: {"name": "Alaska", "bbox_area": 1168.791879840781, "place_type": 8},
    7: {"name": "Virginia", "bbox_area": 24.89086076688, "place_type": 8},
    8: {"name": "Rhode Island", "bbox_area": 0.755620265642, "place_type": 8},
    9: {"name": "New Mexico", "bbox_area": 34.281980445289, "place_type": 8},
    10: {"name": "Oregon", "bbox_area": 35.493394938095, "place_type": 8},
    11: {"name": "Hawaii", "bbox_area": 228.630130882009, "place_type": 8},
    12: {"name": "Oklahoma", "bbox_area": 29.027412778625, "place_type": 8},
    13: {"name": "North Dakota", "bbox_area": 22.97637431948, "place_type": 8},
    14: {"name": "California", "bbox_area": 98.13259845252, "place_type": 8},
    15: {"name": "Wyoming", "bbox_area": 28.086578542459, "place_type": 8},
    16: {"name": "Montana", "bbox_area": 55.762139886915, "place_type": 8},
    17: {"name": "Maine", "bbox_area": 19.07255265344, "place_type": 8},
    18: {"name": "Texas", "bbox_area": 140.09339774878, "place_type": 8},
    19: {"name": "Alabama", "bbox_area": 17.435924346543, "place_type": 8},
    20: {"name": "Indiana", "bbox_area": 13.218874212, "place_type": 8},
    21: {"name": "Florida", "bbox_area": 50.5955923494, "place_type": 8},
    22: {"name": "Idaho", "bbox_area": 43.477094732848, "place_type": 8},
    23: {"name": "Georgia", "bbox_area": 22.545128053872, "place_type": 8},
    24: {"name": "Iowa", "bbox_area": 20.315613564544, "place_type": 8},
    25: {"name": "Kansas", "bbox_area": 22.4658993273, "place_type": 8},
    26: {"name": "Kentucky", "bbox_area": 20.16212647371, "place_type": 8},
    27: {"name": "Louisiana", "bbox_area": 22.008788641024, "place_type": 8},
    28: {"name": "Missouri", "bbox_area": 30.828261791352, "place_type": 8},
    29: {"name": "Michigan", "bbox_area": 54.8322765618457, "place_type": 8},
    30: {"name": "North Carolina", "bbox_area": 25.29565041825, "place_type": 8},
    31: {"name": "Ohio", "bbox_area": 16.8782266344, "place_type": 8},
    32: {"name": "Wisconsin", "bbox_area": 31.99164319827, "place_type": 8},
    33: {"name": "West Virginia", "bbox_area": 16.928757907792, "place_type": 8},
    34: {"name": "Colorado", "bbox_area": 28.15207387564, "place_type": 8},
    35: {"name": "Illinois", "bbox_area": 24.883853717352, "place_type": 8},
    36: {"name": "Arkansas", "bbox_area": 17.385664355932, "place_type": 8},
    37: {"name": "Mississippi", "bbox_area": 17.274283084734, "place_type": 8},
    38: {"name": "Minnesota", "bbox_area": 45.642924467567, "place_type": 8},
    39: {"name": "Maryland", "bbox_area": 8.266458075408, "place_type": 8},
    40: {"name": "Arizona", "bbox_area": 32.732879886612, "place_type": 8},
    41: {"name": "New Hampshire", "bbox_area": 5.170266534681, "place_type": 8},
    42: {"name": "Pennsylvania", "bbox_area": 16.303247489277, "place_type": 8},
    43: {"name": "South Carolina", "bbox_area": 15.447840611922, "place_type": 8},
    44: {"name": "South Dakota", "bbox_area": 26.413441647237, "place_type": 8},
    45: {"name": "Tennessee", "bbox_area": 14.687327194738, "place_type": 8},
    46: {"name": "Washington", "bbox_area": 27.441236976482, "place_type": 8},
    47: {"name": "Vermont", "bbox_area": 4.517486322594, "place_type": 8},
    48: {"name": "New York", "bbox_area": 36.240100318134, "place_type": 8},
    49: {"name": "Connecticut", "bbox_area": 2.13389876918411, "place_type": 8},
    50: {"name": "Nevada", "bbox_area": 41.7711724542, "place_type": 8},
    51: {"name": "New Jersey", "bbox_area": 4.311740518916, "place_type": 8},
    52: {"name": "Utah", "bbox_area": 25.076835761085, "place_type": 8},
    53: {"name": "Union", "bbox_area": 0.119087307587, "place_type": 9},
    54: {"name": "Van Buren", "bbox_area": 0.140317207199954, "place_type": 9},
    55: {"name": "Kiowa", "bbox_area": 0.193994406771, "place_type": 9},
    56: {"name": "Logan", "bbox_area": 0.293722141979933, "place_type": 9},
    57: {"name": "Anderson", "bbox_area": 0.160184945899965, "place_type": 9},
    58: {"name": "Pawnee", "bbox_area": 0.235964283358035, "place_type": 9},
    59: {"name": "Wallace", "bbox_area": 0.248770142112, "place_type": 9},
    60: {"name": "Saline", "bbox_area": 0.194779267616, "place_type": 9},
    61: {"name": "Ballard", "bbox_area": 0.115361956872, "place_type": 9},
    62: {"name": "Breckinridge", "bbox_area": 0.256578423236, "place_type": 9},
    63: {"name": "Fulton", "bbox_area": 0.11269030916, "place_type": 9},
    64: {"name": "Linn", "bbox_area": 0.164368674416, "place_type": 9},
    65: {"name": "Daviess", "bbox_area": 0.218504771127, "place_type": 9},
    66: {"name": "Grant", "bbox_area": 0.10228066962, "place_type": 9},
    67: {"name": "Green", "bbox_area": 0.124866025046, "place_type": 9},
    68: {"name": "Hancock", "bbox_area": 0.125694629255, "place_type": 9},
    69: {"name": "Graves", "bbox_area": 0.149535158748, "place_type": 9},
    70: {"name": "Hickman", "bbox_area": 0.114383901254, "place_type": 9},
    71: {"name": "Harrison", "bbox_area": 0.138488736425, "place_type": 9},
    72: {"name": "Jackson County, US, KY", "bbox_area": 0.14008274799, "place_type": 9},
    73: {"name": "Johnson", "bbox_area": 0.116622808128, "place_type": 9},
    74: {"name": "Larue", "bbox_area": 0.133072273188, "place_type": 9},
    75: {"name": "Laurel", "bbox_area": 0.200930937384, "place_type": 9},
    76: {"name": "Lee", "bbox_area": 0.08945526711, "place_type": 9},
    77: {"name": "Lawrence", "bbox_area": 0.218640100826, "place_type": 9},
    78: {"name": "Kenton", "bbox_area": 0.063932787808, "place_type": 9},
    79: {"name": "Lincoln", "bbox_area": 0.166208171851, "place_type": 9},
    80: {"name": "Owsley", "bbox_area": 0.104888373035, "place_type": 9},
    81: {"name": "Magoffin", "bbox_area": 0.16007275665, "place_type": 9},
    82: {"name": "Robertson", "bbox_area": 0.047246170925, "place_type": 9},
    83: {"name": "Marion", "bbox_area": 0.15648001716, "place_type": 9},
    84: {"name": "Pendleton", "bbox_area": 0.116408755452, "place_type": 9},
    85: {"name": "Perry", "bbox_area": 0.2501475834, "place_type": 9},
    86: {"name": "Rockcastle", "bbox_area": 0.145095716472, "place_type": 9},
    87: {"name": "Taylor", "bbox_area": 0.149109167269, "place_type": 9},
    88: {"name": "Todd", "bbox_area": 0.12408532316, "place_type": 9},
    89: {"name": "Scott", "bbox_area": 0.129449794821, "place_type": 9},
    90: {"name": "Saint James", "bbox_area": 0.08918929536, "place_type": 1001},
    91: {"name": "Tensas", "bbox_area": 0.28392848172, "place_type": 1001},
    92: {"name": "Saint Landry", "bbox_area": 0.44889317286, "place_type": 1001},
    93: {"name": "Saint Martin", "bbox_area": 0.7179435648, "place_type": 1001},
    94: {"name": "Clarke", "bbox_area": 0.193650307266, "place_type": 9},
    95: {"name": "Ionia", "bbox_area": 0.166761817040965, "place_type": 9},
    96: {"name": "Montcalm", "bbox_area": 0.254267582064108, "place_type": 9},
    97: {"name": "Miller", "bbox_area": 0.213327794679959, "place_type": 9},
    98: {"name": "Taney", "bbox_area": 0.175719349322945, "place_type": 9},
    99: {"name": "Hamilton", "bbox_area": 0.744259337064, "place_type": 9},
    100: {"name": "Montgomery", "bbox_area": 0.18646274248, "place_type": 9},
    101: {"name": "Greene", "bbox_area": 0.28074613688, "place_type": 9},
    102: {"name": "Warren", "bbox_area": 0.452484125508058, "place_type": 9},
    103: {"name": "Yates", "bbox_area": 0.145693266444, "place_type": 9},
    104: {"name": "Anson", "bbox_area": 0.1909732028, "place_type": 9},
    105: {"name": "Scotland", "bbox_area": 0.149405826528, "place_type": 9},
    106: {"name": "Clinton", "bbox_area": 0.149091096704, "place_type": 9},
    107: {"name": "Fulton", "bbox_area": 0.122484288846, "place_type": 9},
    108: {"name": "Logan", "bbox_area": 0.153037860726031, "place_type": 9},
    109: {"name": "Pike", "bbox_area": 0.149643823952, "place_type": 9},
    110: {"name": "Lawrence", "bbox_area": 0.23561916585, "place_type": 9},
    111: {"name": "Clarion", "bbox_area": 0.230963199018, "place_type": 9},
    112: {"name": "Blair", "bbox_area": 0.25238951442, "place_type": 9},
    113: {"name": "Elk", "bbox_area": 0.368362230659, "place_type": 9},
    114: {"name": "Cumberland", "bbox_area": 0.295577846033, "place_type": 9},
    115: {"name": "Greene", "bbox_area": 0.184845478242, "place_type": 9},
    116: {"name": "Edgefield", "bbox_area": 0.236299776504, "place_type": 9},
    117: {"name": "Lyon", "bbox_area": 0.233932074816, "place_type": 9},
    118: {"name": "Stanton", "bbox_area": 0.180822475428, "place_type": 9},
    119: {"name": "Woodson", "bbox_area": 0.136099787796, "place_type": 9},
    120: {"name": "Hardin", "bbox_area": 0.339705458622, "place_type": 9},
    121: {"name": "Pike", "bbox_area": 0.421568666232, "place_type": 9},
    122: {"name": "East Carroll", "bbox_area": 0.21270576912, "place_type": 1001},
    123: {"name": "East Feliciana", "bbox_area": 0.173255942823035, "place_type": 1001},
    124: {"name": "Iberville", "bbox_area": 0.321964960933068, "place_type": 1001},
    125: {"name": "Lafayette", "bbox_area": 0.130664086971, "place_type": 1001},
    126: {"name": "Lincoln", "bbox_area": 0.143218882097, "place_type": 1001},
    127: {"name": "Washington", "bbox_area": 1.673606612597, "place_type": 9},
    128: {"name": "Franklin", "bbox_area": 0.34983236283, "place_type": 9},
    129: {"name": "Arenac", "bbox_area": 0.328256523584, "place_type": 9},
    130: {"name": "Baraga", "bbox_area": 0.429532623876, "place_type": 9},
    131: {"name": "Grand Traverse", "bbox_area": 0.294961655826, "place_type": 9},
    132: {"name": "Missaukee", "bbox_area": 0.171141260575, "place_type": 9},
    133: {"name": "Pettis", "bbox_area": 0.201805327026, "place_type": 9},
    134: {"name": "Schuyler", "bbox_area": 0.094209586047, "place_type": 9},
    135: {"name": "Wright", "bbox_area": 0.187804380015955, "place_type": 9},
    136: {"name": "Dakota", "bbox_area": 0.091937418066, "place_type": 9},
    137: {"name": "Lander", "bbox_area": 2.327029916673, "place_type": 9},
    138: {"name": "Essex", "bbox_area": 0.837017373792, "place_type": 9},
    139: {"name": "Grafton", "bbox_area": 0.86768289544, "place_type": 9},
    140: {"name": "Ocean", "bbox_area": 0.409712894487, "place_type": 9},
    141: {"name": "Rensselaer", "bbox_area": 0.257695138152, "place_type": 9},
    142: {"name": "Nassau", "bbox_area": 0.167227817760036, "place_type": 9},
    143: {"name": "Clark", "bbox_area": 0.15932360025, "place_type": 9},
    144: {"name": "DeWitt", "bbox_area": 0.13448854365, "place_type": 9},
    145: {"name": "Putnam", "bbox_area": 0.066600352632, "place_type": 9},
    146: {"name": "Tazewell", "bbox_area": 0.2835730023, "place_type": 9},
    147: {"name": "Union", "bbox_area": 0.130055730717, "place_type": 9},
    148: {"name": "Henry", "bbox_area": 0.11527165024, "place_type": 9},
    149: {"name": "Johnson", "bbox_area": 0.089270982411, "place_type": 9},
    150: {"name": "LaGrange", "bbox_area": 0.110244953, "place_type": 9},
    151: {"name": "LaPorte", "bbox_area": 0.234388983885, "place_type": 9},
    152: {"name": "Allamakee", "bbox_area": 0.232732250784, "place_type": 9},
    153: {"name": "Clinton", "bbox_area": 0.2321451864, "place_type": 9},
    154: {"name": "Jefferson", "bbox_area": 0.122562512613, "place_type": 9},
    155: {"name": "Mahaska", "bbox_area": 0.160800329708954, "place_type": 9},
    156: {"name": "Osceola", "bbox_area": 0.116453409870047, "place_type": 9},
    157: {"name": "Wright", "bbox_area": 0.166295217587965, "place_type": 9},
    158: {"name": "Palo Alto", "bbox_area": 0.163798095424, "place_type": 9},
    159: {"name": "Jefferson", "bbox_area": 0.162958266207, "place_type": 9},
    160: {"name": "Wilson", "bbox_area": 0.153458433534044, "place_type": 9},
    161: {"name": "Logan", "bbox_area": 0.528104631552, "place_type": 9},
    162: {"name": "Moffat", "bbox_area": 1.36090254616, "place_type": 9},
    163: {"name": "Rio Grande", "bbox_area": 0.29354191695, "place_type": 9},
    164: {"name": "San Juan", "bbox_area": 0.168285050002, "place_type": 9},
    165: {"name": "Sedgwick", "bbox_area": 0.152752357296, "place_type": 9},
    166: {"name": "Sussex", "bbox_area": 0.40740355908, "place_type": 9},
    167: {"name": "Calhoun", "bbox_area": 0.18663916284, "place_type": 9},
    168: {"name": "Clay", "bbox_area": 0.22231610506, "place_type": 9},
    169: {"name": "Dixie", "bbox_area": 0.331639776372, "place_type": 9},
    170: {"name": "Gadsden", "bbox_area": 0.2104213002, "place_type": 9},
    171: {"name": "Flagler", "bbox_area": 0.197490010098, "place_type": 9},
    172: {"name": "Duval", "bbox_area": 0.35355945036, "place_type": 9},
    173: {"name": "Hamilton", "bbox_area": 0.210542686515, "place_type": 9},
    174: {"name": "Lafayette", "bbox_area": 0.21732849418, "place_type": 9},
    175: {"name": "Leon", "bbox_area": 0.304059155824, "place_type": 9},
    176: {"name": "Clay", "bbox_area": 0.1581624324, "place_type": 9},
    177: {"name": "McKinley", "bbox_area": 1.816621578252, "place_type": 9},
    178: {"name": "Franklin", "bbox_area": 0.158165021362, "place_type": 9},
    179: {"name": "Garfield", "bbox_area": 0.161488726893, "place_type": 9},
    180: {"name": "Churchill", "bbox_area": 1.639973001931, "place_type": 9},
    181: {"name": "Atlantic", "bbox_area": 0.332402335223, "place_type": 9},
    182: {"name": "Hunterdon", "bbox_area": 0.220528717835, "place_type": 9},
    183: {"name": "Monmouth", "bbox_area": 0.32551592226, "place_type": 9},
    184: {"name": "Adams", "bbox_area": 0.742401960168, "place_type": 9},
    185: {"name": "Benton", "bbox_area": 0.834220874446, "place_type": 9},
    186: {"name": "Ferry", "bbox_area": 0.895704485676, "place_type": 9},
    187: {"name": "Berkeley", "bbox_area": 0.144519045237, "place_type": 9},
    188: {"name": "Brooke", "bbox_area": 0.039339520214, "place_type": 9},
    189: {"name": "Marshall", "bbox_area": 0.109856276307066, "place_type": 9},
    190: {"name": "Grant", "bbox_area": 0.261074673543, "place_type": 9},
    191: {"name": "Jackson", "bbox_area": 0.220719769802041, "place_type": 9},
    192: {"name": "Mineral", "bbox_area": 0.25250515626, "place_type": 9},
    193: {"name": "Roane", "bbox_area": 0.19479248074, "place_type": 9},
    194: {"name": "Tyler", "bbox_area": 0.157221871712, "place_type": 9},
    195: {"name": "Wetzel", "bbox_area": 0.162249682644, "place_type": 9},
    196: {"name": "Crawford", "bbox_area": 0.239681067972044, "place_type": 9},
    197: {"name": "Elbert", "bbox_area": 0.664578289928, "place_type": 9},
    198: {"name": "Stone", "bbox_area": 0.249157924182, "place_type": 9},
    199: {"name": "Aleutians West", "bbox_area": 133.205583038668, "place_type": 9},
    200: {"name": "Cherokee", "bbox_area": 0.260279584224, "place_type": 9},
    201: {"name": "Summit", "bbox_area": 0.377183858064, "place_type": 9},
    202: {"name": "Rio Blanco", "bbox_area": 1.16074181155, "place_type": 9},
    203: {"name": "White", "bbox_area": 0.397798027952, "place_type": 9},
    204: {"name": "Madison", "bbox_area": 0.283309387554, "place_type": 9},
    205: {"name": "Denver", "bbox_area": 0.152797806, "place_type": 9},
    206: {"name": "Frontier", "bbox_area": 0.28163782394992, "place_type": 9},
    207: {"name": "Greeley", "bbox_area": 0.160355931707, "place_type": 9},
    208: {"name": "Hall", "bbox_area": 0.153188923632035, "place_type": 9},
    209: {"name": "Jefferson", "bbox_area": 0.15827380799, "place_type": 9},
    210: {"name": "Kearney", "bbox_area": 0.154673957815, "place_type": 9},
    211: {"name": "Otoe", "bbox_area": 0.197160912756, "place_type": 9},
    212: {"name": "Thomas", "bbox_area": 0.2024860116, "place_type": 9},
    213: {"name": "Lyon", "bbox_area": 1.271844157605, "place_type": 9},
    214: {"name": "Cumberland", "bbox_area": 0.30383734328, "place_type": 9},
    215: {"name": "Sampson", "bbox_area": 0.425660353343, "place_type": 9},
    216: {"name": "Watauga", "bbox_area": 0.129369834732, "place_type": 9},
    217: {"name": "McHenry", "bbox_area": 0.67766909628, "place_type": 9},
    218: {"name": "Walsh", "bbox_area": 0.422463102608, "place_type": 9},
    219: {"name": "Gallia", "bbox_area": 0.220366752528045, "place_type": 9},
    220: {"name": "Geauga", "bbox_area": 0.143150351784, "place_type": 9},
    221: {"name": "Hocking", "bbox_area": 0.17691034134, "place_type": 9},
    222: {"name": "Lorain", "bbox_area": 0.383720658684, "place_type": 9},
    223: {"name": "Dawson", "bbox_area": 0.304397621623919, "place_type": 9},
    224: {"name": "Douglas", "bbox_area": 0.121902804806, "place_type": 9},
    225: {"name": "Hickory", "bbox_area": 0.137600516944, "place_type": 9},
    226: {"name": "Henry", "bbox_area": 0.206678653088037, "place_type": 9},
    227: {"name": "Nodaway", "bbox_area": 0.273186688593045, "place_type": 9},
    228: {"name": "Sainte Genevieve", "bbox_area": 0.244915842624046, "place_type": 9},
    229: {"name": "Newton", "bbox_area": 0.172860464403, "place_type": 9},
    230: {"name": "Ripley", "bbox_area": 0.15096057216904, "place_type": 9},
    231: {"name": "Scott", "bbox_area": 0.086146031517, "place_type": 9},
    232: {"name": "Buffalo", "bbox_area": 0.278633168136, "place_type": 9},
    233: {"name": "Cass", "bbox_area": 0.184911453942, "place_type": 9},
    234: {"name": "Dodge", "bbox_area": 0.201909682943965, "place_type": 9},
    235: {"name": "Furnas", "bbox_area": 0.199318489668, "place_type": 9},
    236: {"name": "Logan", "bbox_area": 0.160916265509954, "place_type": 9},
    237: {"name": "Loup", "bbox_area": 0.161829529224, "place_type": 9},
    238: {"name": "Merrick", "bbox_area": 0.362733013908, "place_type": 9},
    239: {"name": "Valley", "bbox_area": 0.160002693942, "place_type": 9},
    240: {"name": "Webster", "bbox_area": 0.157992716326, "place_type": 9},
    241: {"name": "Cape May", "bbox_area": 0.376894755976, "place_type": 9},
    242: {"name": "Cleveland", "bbox_area": 0.18800905929, "place_type": 9},
    243: {"name": "Mineral", "bbox_area": 1.731350923366, "place_type": 9},
    244: {"name": "Wayne", "bbox_area": 0.227781150619, "place_type": 9},
    245: {"name": "Renville", "bbox_area": 0.520729949971, "place_type": 9},
    246: {"name": "Cleburne", "bbox_area": 0.28874195145395, "place_type": 9},
    247: {"name": "Saline", "bbox_area": 0.372498422904, "place_type": 9},
    248: {"name": "Van Buren", "bbox_area": 0.260578468920043, "place_type": 9},
    249: {"name": "Lincoln County, US, CO", "bbox_area": 0.946366237243, "place_type": 9},
    250: {"name": "Jefferson", "bbox_area": 0.27501683563, "place_type": 9},
    2757: {"name": "Siskiyou", "bbox_area": 2.31256057032, "place_type": 9},
    6481: {"name": "Dunsmuir City Park", "bbox_area": 7.68452732075066e-06, "place_type": 100},
    177501: {"name": "Klamath Mountains Youth Stewardship", "bbox_area": 6.823216183615742, "place_type": None},
}

place_type_labels = {
    8: "State",
    9: "County",
    12: "Country",
    100: "Park", # TODO: Confirm
    1001: "Parish", # Counties in Louisiana
}


def get_term_label(term_id: int) -> Optional[str]:
    """
    Get the label for a given annotation term ID
    
    Args:
        term_id: The annotation term ID
        
    Returns:
        The term label or None if not found
    """
    return term_labels.get(term_id)


def get_value_label(value_id: int) -> Optional[str]:
    """
    Get the label for a given annotation value ID
    
    Args:
        value_id: The annotation value ID
        
    Returns:
        The value label or None if not found
    """
    return value_labels.get(value_id)


def get_place_label(place_id: int) -> Optional[dict[int,dict]]:
    """
    Get the label for a given place ID
    
    Args:
        place_id: The place ID
        
    Returns:
        The place label or None if not found
    """
    return place_labels.get(place_id)
