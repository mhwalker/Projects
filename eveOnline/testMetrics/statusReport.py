import MySQLdb

listOfRaw = [16633,16634,16635,16636,16637,16638,16639,16640,16641,16642,16643,16644,16646,16647,16648,16649,16650,16651,16652,16653]
listOfSimple = [16654,16655,16656,16657,16658,16659,16660,16661,16662,16663,16664,16665,16666,16667,16668,16669,17769,17959,17960]
listOfComplex = [16670,16671,16672,16673,16678,16679,16680,16681,16682,16683,17317]

listOfT2 = [11530,11531,11532,11533,11534,11535,11536,11537,11538,11539,11540,11541,11542,11543,11544,11545,11547,11548,11549,11550,11551,11552,11554,11554,11555,11556,11557,11558,11688,11689,11690,11691,11692,11693,11694,11695]
listOfProducts = [2048, 10250, 22544, 22546, 22548, 32790, 22553, 22555, 22557, 20514, 28710, 32809, 28848, 4147, 32821, 32822, 32823, 2104, 32825, 12346, 32827, 32828, 2109, 12356, 2117, 30832, 30834, 22440, 30836, 1436, 2175, 16065, 2185, 2195, 4248, 4250, 4252, 2205, 18590, 4256, 4258, 4260, 18598, 4264, 4266, 4268, 4270, 18608, 4274, 12017, 18612, 4278, 18616, 4282, 4284, 4286, 4288, 4290, 4292, 4294, 4296, 4299, 18624, 2258, 2259, 2260, 2261, 2262, 2281, 22444, 11987, 2297, 22778, 2299, 2301, 22229, 26888, 26890, 26892, 12557, 12559, 12563, 12565, 2333, 26912, 26913, 26914, 2341, 29063, 2355, 4405, 2364, 12608, 12612, 12614, 12618, 12620, 12625, 12631, 12633, 32826, 2404, 2410, 29039, 29041, 29043, 2420, 29045, 29047, 29049, 29051, 380, 29053, 29055, 29057, 29059, 2436, 29061, 10631, 29065, 29067, 29069, 2446, 29071, 400, 29073, 29075, 29077, 29079, 2456, 29081, 29083, 29085, 29087, 29089, 2466, 29091, 29093, 29095, 29097, 29099, 29101, 2478, 29103, 29105, 29107, 29109, 438, 10680, 12729, 12731, 12733, 12735, 448, 3488, 12743, 12745, 12747, 12753, 12761, 12765, 12767, 482, 2531, 12773, 12775, 12777, 12779, 15784, 12787, 12789, 12791, 2553, 2559, 12801, 12803, 12805, 519, 2571, 12814, 2575, 12816, 12818, 12820, 12822, 2584, 12826, 12828, 2592, 20409, 2613, 2621, 2629, 2637, 440, 22456, 2647, 10842, 2655, 10850, 15804, 10858, 2679, 11370, 1999, 17544, 32824, 17522, 25715, 15818, 13001, 13003, 2801, 2811, 2817, 11014, 1969, 11017, 21638, 2865, 11052, 32829, 21640, 2873, 13119, 2881, 2889, 2897, 12771, 2905, 2913, 2921, 2929, 2937, 3170, 2945, 2539, 2953, 2961, 2969, 2977, 11172, 11174, 12785, 11176, 2985, 11178, 11182, 11184, 2993, 11186, 2547, 11188, 4254, 11190, 11192, 3001, 11194, 11196, 11198, 11200, 18592, 11202, 3017, 18594, 3025, 11219, 18596, 29659, 29660, 29661, 29662, 29663, 29664, 3041, 2488, 4262, 11239, 3049, 18600, 3065, 11259, 18602, 3074, 11269, 28844, 3082, 3090, 2563, 18606, 3098, 1541, 4272, 3106, 3114, 2567, 28850, 3122, 4276, 3130, 3138, 18614, 3146, 17485, 19534, 15885, 4280, 3154, 3162, 527, 17500, 18618, 17502, 17504, 17506, 17508, 11365, 17510, 15889, 17512, 3178, 11371, 17516, 17518, 17520, 11377, 3186, 11379, 17524, 11381, 17526, 17528, 2580, 11387, 17536, 11393, 17538, 17540, 17542, 11400, 17549, 12824, 17557, 17559, 1183, 1190, 2588, 3244, 1198, 25812, 3285, 20345, 28197, 1248, 20347, 1256, 28199, 1266, 28201, 1236, 1276, 15915, 1286, 1296, 1306, 19739, 11553, 1319, 11577, 11578, 28213, 15685, 11229, 1355, 15693, 15705, 15707, 15709, 19806, 15711, 15721, 15723, 15725, 15727, 15729, 15731, 15733, 15735, 11640, 15737, 11642, 15739, 11644, 1405, 11646, 11648, 15800, 1422, 15759, 15761, 15764, 15766, 15768, 15770, 15772, 15776, 15778, 3995, 15780, 15782, 1447, 3496, 15786, 15788, 15790, 3504, 15794, 15796, 22430, 15798, 3512, 15802, 3516, 3518, 3520, 1952, 3530, 15821, 32207, 3540, 15838, 15841, 15953, 28215, 3568, 1960, 17912, 3578, 2303, 22442, 15875, 3588, 15877, 15879, 15881, 15883, 1549, 3598, 15887, 1553, 22446, 1559, 3608, 1565, 13856, 15909, 15911, 15913, 28203, 28205, 28207, 28209, 28211, 15925, 15927, 15929, 15931, 24501, 15941, 3655, 15945, 15947, 15949, 3665, 15955, 15957, 15959, 15961, 15963, 20069, 20070, 12807, 1964, 28268, 12221, 28272, 28264, 18604, 28276, 28280, 28284, 28288, 28292, 3009, 28296, 28300, 28304, 1987, 18068, 17514, 20124, 20125, 11957, 11959, 11961, 11963, 11965, 16062, 11969, 11971, 11978, 11985, 22227, 22228, 11989, 11993, 11995, 11999, 12003, 12005, 4014, 12011, 12013, 12015, 24305, 12019, 12021, 12023, 12032, 3841, 12034, 12038, 12042, 12044, 22291, 3033, 12058, 25563, 12068, 18610, 12076, 3831, 3888, 12084, 1855, 12102, 1877, 24417, 3939, 3943, 24427, 3949, 3955, 24438, 20343, 28308, 24443, 20349, 20351, 20353, 12271, 3979, 3983, 3986, 3989, 24471, 24473, 24475, 22428, 24477, 24478, 24479, 28576, 28578, 11249, 22436, 24486, 3057, 24488, 24490, 24492, 24493, 24494, 24495, 22448, 24497, 24499, 22452, 20405, 20406, 24503, 20408, 24505, 1978, 24507, 22460, 24509, 24511, 22464, 24513, 22466, 24515, 22468, 24517, 22470, 24519, 24521, 22474, 24523, 24525, 10190, 24527, 24529, 24531, 24533, 24535, 24537, 24539, 24541, 12259, 12263, 2024, 12267, 28846, 2032, 28659, 28661, 2038, 28665]

allProducts = []
allProducts.extend(listOfRaw)
allProducts.extend(listOfSimple)
allProducts.extend(listOfComplex)
allProducts.extend(listOfT2)
allProducts.extend(listOfProducts)

db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()


theCount = dict()
nItems = 0
totalRecords = 0
missing = []

for item in allProducts:
    nItems += 1
    query = "SELECT COUNT(*) as count FROM history WHERE regionID = 10000002 AND day > \"2012-08-31 23:00:00\" and day < \"2013-03-01 00:00:00\" and typeID="+str(item)+";"
    #print query
    cursor.execute(query)
    rows = cursor.fetchall()
    count = int(rows[0][0])
    theCount[item] = count
    totalRecords += count
    if count == 0: missing.append(item)

print float(totalRecords)/float(nItems*181)
print missing


query = "SELECT COUNT(*) FROM history;"
cursor.execute(query)
row = cursor.fetchone()
totalCount = int(row[0])

print totalCount

outfile = open("index.html","w")



outfile.close()
