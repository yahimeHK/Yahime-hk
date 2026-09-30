/* LOL攻略網站 V5 data layer - Patch 26.19 / Data Dragon 16.19.1 */
const DDragonVersion = '16.19.1';
const DDragonBase = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/zh_TW`;
const DDragonEnglish = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/en_US`;
const LiveGuideBase = 'https://lanelore.com/champions/';
const CounterBase = 'https://www.leagueofgraphs.com/champions/counters/';
const $ = id => document.getElementById(id);
const escapeHTML = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));

/* ===== 清理 Riot 技能描述中的 HTML 標籤 ===== */
function cleanRiotText(raw) {
    return String(raw || '')
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/?(main|scaleAP|scaleAD|scaleHealth|scaleMana|scaleArmor|scaleMR|scaleLevel|physicalDamage|magicDamage|trueDamage|healing|shield|speed|attackSpeed|lifeSteal|spellBlock|armor|health|mana|gold|attention|status|font|b|i|u|s|span|div|p|li|ul|ol)[^>]*>/gi, '')
        .replace(/<[^>]+>/g, '')
        .replace(/[ \t]{2,}/g, ' ')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}

const championSeed = [
    { name: "Aatrox", img: "Aatrox" }, { name: "Ahri", img: "Ahri" }, { name: "Akali", img: "Akali" },
    { name: "Akshan", img: "Akshan" }, { name: "Alistar", img: "Alistar" }, { name: "Ambessa", img: "Ambessa" },
    { name: "Amumu", img: "Amumu" }, { name: "Anivia", img: "Anivia" }, { name: "Annie", img: "Annie" },
    { name: "Aphelios", img: "Aphelios" }, { name: "Ashe", img: "Ashe" }, { name: "Aurelion Sol", img: "AurelionSol" },
    { name: "Aurora", img: "Aurora" }, { name: "Azir", img: "Azir" }, { name: "Bard", img: "Bard" },
    { name: "Bel'Veth", img: "Belveth" }, { name: "Blitzcrank", img: "Blitzcrank" }, { name: "Brand", img: "Brand" },
    { name: "Braum", img: "Braum" }, { name: "Briar", img: "Briar" }, { name: "Caitlyn", img: "Caitlyn" },
    { name: "Camille", img: "Camille" }, { name: "Cassiopeia", img: "Cassiopeia" }, { name: "Cho'Gath", img: "Chogath" },
    { name: "Corki", img: "Corki" }, { name: "Darius", img: "Darius" }, { name: "Diana", img: "Diana" },
    { name: "Dr. Mundo", img: "DrMundo" }, { name: "Draven", img: "Draven" }, { name: "Ekko", img: "Ekko" },
    { name: "Elise", img: "Elise" }, { name: "Evelynn", img: "Evelynn" }, { name: "Ezreal", img: "Ezreal" },
    { name: "Fiddlesticks", img: "Fiddlesticks" }, { name: "Fiora", img: "Fiora" }, { name: "Fizz", img: "Fizz" },
    { name: "Galio", img: "Galio" }, { name: "Gangplank", img: "Gangplank" }, { name: "Garen", img: "Garen" },
    { name: "Gnar", img: "Gnar" }, { name: "Gragas", img: "Gragas" }, { name: "Graves", img: "Graves" },
    { name: "Gwen", img: "Gwen" }, { name: "Hecarim", img: "Hecarim" }, { name: "Heimerdinger", img: "Heimerdinger" },
    { name: "Hwei", img: "Hwei" }, { name: "Illaoi", img: "Illaoi" }, { name: "Irelia", img: "Irelia" },
    { name: "Ivern", img: "Ivern" }, { name: "Jarvan IV", img: "JarvanIV" }, { name: "Jax", img: "Jax" },
    { name: "Jayce", img: "Jayce" }, { name: "Jhin", img: "Jhin" }, { name: "Jinx", img: "Jinx" },
    { name: "K'Sante", img: "KSante" }, { name: "Kai'Sa", img: "Kaisa" }, { name: "Kalista", img: "Kalista" },
    { name: "Karma", img: "Karma" }, { name: "Karthus", img: "Karthus" }, { name: "Kassadin", img: "Kassadin" },
    { name: "Katarina", img: "Katarina" }, { name: "Kayle", img: "Kayle" }, { name: "Kayn", img: "Kayn" },
    { name: "Kennen", img: "Kennen" }, { name: "Kha'Zix", img: "Khazix" }, { name: "Kindred", img: "Kindred" },
    { name: "Kled", img: "Kled" }, { name: "Kog'Maw", img: "KogMaw" }, { name: "LeBlanc", img: "Leblanc" },
    { name: "Lee Sin", img: "LeeSin" }, { name: "Leona", img: "Leona" }, { name: "Lillia", img: "Lillia" },
    { name: "Lissandra", img: "Lissandra" }, { name: "Lucian", img: "Lucian" }, { name: "Lulu", img: "Lulu" },
    { name: "Lux", img: "Lux" }, { name: "Malphite", img: "Malphite" }, { name: "Malzahar", img: "Malzahar" },
    { name: "Maokai", img: "Maokai" }, { name: "Master Yi", img: "MasterYi" }, { name: "Mel", img: "Mel" },
    { name: "Milio", img: "Milio" }, { name: "Miss Fortune", img: "MissFortune" }, { name: "Mordekaiser", img: "Mordekaiser" },
    { name: "Morgana", img: "Morgana" }, { name: "Naafiri", img: "Naafiri" }, { name: "Nami", img: "Nami" },
    { name: "Nasus", img: "Nasus" }, { name: "Nautilus", img: "Nautilus" }, { name: "Neeko", img: "Neeko" },
    { name: "Nidalee", img: "Nidalee" }, { name: "Nilah", img: "Nilah" }, { name: "Nocturne", img: "Nocturne" },
    { name: "Nunu & Willump", img: "Nunu" }, { name: "Olaf", img: "Olaf" }, { name: "Orianna", img: "Orianna" },
    { name: "Ornn", img: "Ornn" }, { name: "Pantheon", img: "Pantheon" }, { name: "Poppy", img: "Poppy" },
    { name: "Pyke", img: "Pyke" }, { name: "Qiyana", img: "Qiyana" }, { name: "Quinn", img: "Quinn" },
    { name: "Rakan", img: "Rakan" }, { name: "Rammus", img: "Rammus" }, { name: "Rek'Sai", img: "RekSai" },
    { name: "Rell", img: "Rell" }, { name: "Renata Glasc", img: "Renata" }, { name: "Renekton", img: "Renekton" },
    { name: "Rengar", img: "Rengar" }, { name: "Riven", img: "Riven" }, { name: "Rumble", img: "Rumble" },
    { name: "Ryze", img: "Ryze" }, { name: "Samira", img: "Samira" }, { name: "Sejuani", img: "Sejuani" },
    { name: "Senna", img: "Senna" }, { name: "Seraphine", img: "Seraphine" }, { name: "Sett", img: "Sett" },
    { name: "Shaco", img: "Shaco" }, { name: "Shen", img: "Shen" }, { name: "Shyvana", img: "Shyvana" },
    { name: "Singed", img: "Singed" }, { name: "Sion", img: "Sion" }, { name: "Sivir", img: "Sivir" },
    { name: "Skarner", img: "Skarner" }, { name: "Smolder", img: "Smolder" }, { name: "Sona", img: "Sona" },
    { name: "Soraka", img: "Soraka" }, { name: "Swain", img: "Swain" }, { name: "Sylas", img: "Sylas" },
    { name: "Syndra", img: "Syndra" }, { name: "Tahm Kench", img: "TahmKench" }, { name: "Taliyah", img: "Taliyah" },
    { name: "Talon", img: "Talon" }, { name: "Taric", img: "Taric" }, { name: "Teemo", img: "Teemo" },
    { name: "Thresh", img: "Thresh" }, { name: "Tristana", img: "Tristana" }, { name: "Trundle", img: "Trundle" },
    { name: "Tryndamere", img: "Tryndamere" }, { name: "Twisted Fate", img: "TwistedFate" }, { name: "Twitch", img: "Twitch" },
    { name: "Udyr", img: "Udyr" }, { name: "Urgot", img: "Urgot" }, { name: "Varus", img: "Varus" },
    { name: "Vayne", img: "Vayne" }, { name: "Veigar", img: "Veigar" }, { name: "Vel'Koz", img: "Velkoz" },
    { name: "Vex", img: "Vex" }, { name: "Vi", img: "Vi" }, { name: "Viego", img: "Viego" },
    { name: "Viktor", img: "Viktor" }, { name: "Vladimir", img: "Vladimir" }, { name: "Volibear", img: "Volibear" },
    { name: "Warwick", img: "Warwick" }, { name: "Wukong", img: "Wukong" }, { name: "Xayah", img: "Xayah" },
    { name: "Xerath", img: "Xerath" }, { name: "Xin Zhao", img: "XinZhao" }, { name: "Yasuo", img: "Yasuo" },
    { name: "Yone", img: "Yone" }, { name: "Yorick", img: "Yorick" }, { name: "Yuumi", img: "Yuumi" },
    { name: "Zac", img: "Zac" }, { name: "Zed", img: "Zed" }, { name: "Zeri", img: "Zeri" },
    { name: "Ziggs", img: "Ziggs" }, { name: "Zilean", img: "Zilean" }, { name: "Zoe", img: "Zoe" },
    { name: "Zyra", img: "Zyra" }, { name: "Zaahen", img: "Zaahen" }
];

const roleGroups = {
    "上路": ["Aatrox","Ambessa","Camille","Cho'Gath","Darius","Dr. Mundo","Fiora","Gangplank","Garen","Gnar","Gragas","Gwen","Illaoi","Irelia","Jax","Jayce","K'Sante","Kayle","Kennen","Kled","Malphite","Mordekaiser","Nasus","Olaf","Ornn","Pantheon","Poppy","Quinn","Renekton","Riven","Rumble","Sett","Shen","Singed","Sion","Tahm Kench","Teemo","Trundle","Tryndamere","Urgot","Vayne","Volibear","Warwick","Yasuo","Yone","Yorick"],
    "打野": ["Amumu","Bel'Veth","Briar","Diana","Ekko","Elise","Evelynn","Fiddlesticks","Graves","Hecarim","Ivern","Jarvan IV","Karthus","Kayn","Kha'Zix","Kindred","Kled","Lee Sin","Lillia","Master Yi","Nidalee","Nocturne","Nunu & Willump","Rammus","Rek'Sai","Rengar","Sejuani","Shaco","Shyvana","Skarner","Taliyah","Talon","Udyr","Vi","Viego","Volibear","Warwick","Wukong","Xin Zhao","Zac","Brand","Morgana","Zyra"],
    "中路": ["Ahri","Akali","Akshan","Anivia","Annie","Aurelion Sol","Aurora","Azir","Brand","Cassiopeia","Corki","Diana","Fizz","Galio","Hwei","Irelia","Jayce","Kassadin","Katarina","Kayle","Kayn","Kog'Maw","LeBlanc","Lissandra","Lux","Malzahar","Mel","Naafiri","Neeko","Orianna","Pantheon","Qiyana","Ryze","Sylas","Syndra","Taliyah","Talon","Tristana","Twisted Fate","Viktor","Vladimir","Vex","Xerath","Yasuo","Yone","Zoe","Zed","Swain","Veigar","Vel'Koz","Ziggs","Zilean","Zac","Volibear","Kennen","Lulu","Seraphine","Heimerdinger"],
    "下路": ["Aphelios","Ashe","Caitlyn","Draven","Ezreal","Jhin","Jinx","Kai'Sa","Kalista","Kog'Maw","Lucian","Miss Fortune","Nilah","Samira","Senna","Sivir","Smolder","Tristana","Twitch","Varus","Vayne","Xayah","Zeri","Ziggs","Seraphine","Swain","Corki"],
    "輔助": ["Alistar","Bard","Blitzcrank","Braum","Brand","Karma","Leona","Lulu","Lux","Maokai","Milio","Morgana","Nami","Nautilus","Neeko","Pyke","Rakan","Rell","Renata Glasc","Sona","Soraka","Swain","Tahm Kench","Taric","Teemo","Thresh","Yuumi","Zilean","Zyra","Senna","Seraphine","Poppy","Galio","Malphite","Heimerdinger","Zaahen"]
};

const roleSlug = { "上路": "top", "打野": "jungle", "中路": "middle", "下路": "adc", "輔助": "support" };
const championRoleMap = {};
Object.entries(roleGroups).forEach(([role, names]) => names.forEach(name => {
    if (!championRoleMap[name]) championRoleMap[name] = [];
    if (!championRoleMap[name].includes(role)) championRoleMap[name].push(role);
}));

/* ===== 英雄別名 ===== */
const championAliases = {
    "Aatrox": ["剑魔", "暗裔剑魔"], "Ahri": ["狐狸", "阿狸", "九尾"], "Akali": ["阿卡丽", "离群之刺"],
    "Alistar": ["牛头", "牛头酋长"], "Amumu": ["木木", "阿木木", "大头儿子"], "Anivia": ["冰鸟", "凤凰"],
    "Annie": ["火女", "安妮", "黑暗之女"], "Ashe": ["寒冰", "冰弓", "艾希"], "Blitzcrank": ["机器人"],
    "Brand": ["火男", "布兰德"], "Braum": ["布隆", "门板"], "Caitlyn": ["女警", "小蛋糕"],
    "Cassiopeia": ["蛇女", "魔蛇之拥"], "Cho'Gath": ["大虫子", "科加斯"], "Corki": ["飞机", "库奇"],
    "Darius": ["诺手", "诺克", "德莱厄斯"], "Diana": ["皎月", "月女"], "Dr. Mundo": ["蒙多"],
    "Draven": ["德莱文", "文森特"], "Ekko": ["艾克", "时间刺客"], "Elise": ["蜘蛛"],
    "Evelynn": ["寡妇", "伊芙琳"], "Ezreal": ["EZ", "伊泽瑞尔", "小黄毛"], "Fiddlesticks": ["稻草人"],
    "Fiora": ["剑姬", "菲奥娜", "无双剑姬"], "Fizz": ["小鱼人", "菲兹"], "Galio": ["加里奥", "石像鬼"],
    "Gangplank": ["船长", "普朗克"], "Garen": ["盖伦", "德玛", "gay伦"], "Gnar": ["纳尔"],
    "Gragas": ["酒桶", "古拉加斯"], "Graves": ["男枪", "格雷福斯"], "Hecarim": ["人马", "赫卡里姆"],
    "Heimerdinger": ["大头", "大发明家"], "Illaoi": ["触手妈", "章鱼妈", "俄洛伊"],
    "Irelia": ["刀妹", "女刀", "艾瑞莉娅"], "Jarvan IV": ["皇子", "嘉文四世"],
    "Jax": ["武器", "武器大师", "贾克斯"], "Jayce": ["杰斯"], "Jhin": ["烬", "瘸子"],
    "Jinx": ["金克丝", "暴走萝莉"], "Kai'Sa": ["卡莎", "虚空之女"], "Kalista": ["滑板鞋", "卡莉丝塔"],
    "Karma": ["扇子妈", "卡尔玛"], "Karthus": ["死歌", "卡尔萨斯"], "Kassadin": ["卡萨丁"],
    "Katarina": ["卡特", "卡特琳娜"], "Kayle": ["天使", "凯尔"], "Kennen": ["凯南", "电耗子"],
    "Kha'Zix": ["螳螂", "卡兹克"], "Kindred": ["千珏"], "LeBlanc": ["妖姬", "乐芙兰"],
    "Lee Sin": ["盲僧", "瞎子", "李青"], "Leona": ["日女", "蕾欧娜"], "Lissandra": ["冰女", "丽桑卓"],
    "Lucian": ["奥巴马", "卢锡安"], "Lulu": ["璐璐", "紫皮大蒜"], "Lux": ["光辉", "拉克丝"],
    "Malphite": ["石头人", "墨菲特"], "Malzahar": ["蚂蚱", "玛尔扎哈"], "Maokai": ["大树", "茂凯"],
    "Master Yi": ["剑圣", "易"], "Miss Fortune": ["女枪", "厄运小姐"], "Mordekaiser": ["铁男", "莫德凯撒"],
    "Morgana": ["莫甘娜", "堕落天使"], "Nami": ["娜美", "人鱼"], "Nasus": ["狗头", "内瑟斯"],
    "Nautilus": ["泰坦", "诺提勒斯"], "Nidalee": ["豹女", "奈德丽"], "Nocturne": ["梦魇", "魔腾"],
    "Olaf": ["奥拉夫", "狂战士"], "Orianna": ["发条", "奥莉安娜"], "Ornn": ["奥恩", "山羊"],
    "Pantheon": ["潘森", "斯巴达"], "Poppy": ["波比"], "Pyke": ["派克", "水鬼"],
    "Rammus": ["龙龟", "龟龟"], "Renekton": ["鳄鱼", "雷克顿"], "Rengar": ["狮子狗", "雷恩加尔"],
    "Riven": ["锐雯", "瑞文"], "Rumble": ["兰博", "喷火娃"], "Ryze": ["瑞兹", "光头", "流浪"],
    "Sejuani": ["猪妹", "瑟庄妮"], "Senna": ["赛娜"], "Seraphine": ["酸辣粉", "轮椅妹"],
    "Sett": ["瑟提", "劲夫", "腕豪"], "Shaco": ["小丑", "萨科"], "Shen": ["慎"],
    "Shyvana": ["龙女", "希瓦娜"], "Singed": ["炼金", "辛吉德"], "Sion": ["塞恩", "老司机"],
    "Sivir": ["轮子妈", "希维尔"], "Skarner": ["蝎子", "斯卡纳"], "Sona": ["琴女", "娑娜"],
    "Soraka": ["星妈", "索拉卡"], "Swain": ["乌鸦", "斯维因"], "Sylas": ["塞拉斯", "偷男"],
    "Syndra": ["球女", "辛德拉"], "Tahm Kench": ["蛤蟆", "塔姆", "鲶鱼"], "Talon": ["男刀", "泰隆"],
    "Taric": ["宝石", "塔里克"], "Teemo": ["提莫"], "Thresh": ["锤石", "魂锁典狱长"],
    "Tristana": ["小炮", "崔丝塔娜"], "Trundle": ["巨魔", "特朗德尔"], "Tryndamere": ["蛮王", "泰达米尔"],
    "Twisted Fate": ["卡牌", "崔斯特"], "Twitch": ["老鼠", "图奇"], "Udyr": ["乌迪尔"],
    "Urgot": ["螃蟹", "厄加特"], "Varus": ["韦鲁斯"], "Vayne": ["薇恩", "VN"],
    "Veigar": ["小法", "维迦"], "Vel'Koz": ["大眼", "维克兹"], "Vi": ["蔚", "楚雨荨"],
    "Viego": ["佛耶戈", "破败王"], "Viktor": ["三只手", "维克托"], "Vladimir": ["吸血鬼", "弗拉基米尔"],
    "Volibear": ["狗熊", "沃利贝尔"], "Warwick": ["狼人", "沃里克"], "Wukong": ["猴子", "孙悟空"],
    "Xayah": ["霞"], "Xerath": ["泽拉斯", "三炮"], "Xin Zhao": ["赵信", "德邦", "菊花信"],
    "Yasuo": ["亚索", "风男"], "Yone": ["永恩"], "Yorick": ["掘墓", "约里克"],
    "Yuumi": ["猫咪", "悠米"], "Zac": ["扎克", "粑粑人"], "Zed": ["劫", "影流之主"],
    "Ziggs": ["炸弹人", "吉格斯"], "Zilean": ["时光", "基兰"], "Zoe": ["佐伊"],
    "Zyra": ["婕拉", "荆棘之兴"]
};

/* ===== 英雄經典台詞 ===== */
const championQuotes = {
    "Yasuo": "生命的意义，是体验痛苦。",
    "Diana": "别再否定我了。",
    "Darius": "只有我才能带领我们走向胜利。",
    "Vayne": "在霓虹闪烁的世界，我就是黑暗。",
    "Ryze": "我们再来一次，这一次，好好来。",
    "Lee Sin": "跪下！",
    "Talon": "只有傻瓜才会为荣誉而献身。",
    "Jhin": "我于杀戮之中盛放，亦如黎明中的花朵。",
    "Poppy": "你笑我为何拿上锤和盾，有你在，我不会受到伤害。",
    "Jax": "下了手中的武器，我知道你已厌倦。",
    "Ashe": "当水晶箭射向你的时候，请不要害怕，只是为了让你片刻的驻足。",
    "Xin Zhao": "我只想顶在最前面，用我的长枪保护我的朋友。",
    "Fiddlesticks": "我没有过多的抱怨，漫天的乌鸦都是我的朋友。",
    "Taric": "我曾踏足山巅，也曾进入低谷，二者都让我受益良多。",
    "Master Yi": "真正的大师，永远都怀着一颗学徒的心。",
    "Aatrox": "我是亚托克斯，我是世界的终结者。",
    "Kayn": "通往王座的路上，挑战我的人都得死。我是天选，也是唯一。",
    "Sett": "我妈喊我回家吃饭。",
    "Syndra": "能量属于那些能够运用它的人。"
};

/* ===== 英雄克制關係 ===== */
const championCounters = {
    "Aatrox": { weakAgainst: ["Fiora", "Pantheon", "Malphite", "Maokai", "Malzahar", "Nasus"], strongAgainst: [] },
    "Fiora": { weakAgainst: ["Pantheon", "Tryndamere", "Poppy", "Jax"], strongAgainst: ["Aatrox", "Malphite", "Maokai"] },
    "Riven": { weakAgainst: ["Renekton", "Garen", "Malphite", "Volibear", "Kled"], strongAgainst: [] },
    "Garen": { weakAgainst: ["Gangplank", "Kled", "Akali", "Kennen"], strongAgainst: ["Kled", "Riven"] },
    "Malphite": { weakAgainst: ["Shen", "Hecarim", "Garen", "Darius", "Nasus"], strongAgainst: ["Tryndamere"] },
    "Tryndamere": { weakAgainst: ["Pantheon", "Tahm Kench", "Aatrox", "Renekton", "Fiora"], strongAgainst: [] },
    "Kassadin": { weakAgainst: ["Renekton", "Talon", "Lucian", "Zed"], strongAgainst: [] },
    "Caitlyn": { weakAgainst: [], strongAgainst: ["Vayne"] },
    "Morgana": { weakAgainst: [], strongAgainst: ["Thresh", "Blitzcrank"] },
    "Gangplank": { weakAgainst: ["Neeko", "Olaf", "Yorick", "Fiora"], strongAgainst: ["Malzahar"] },
    "Renekton": { weakAgainst: ["Gangplank", "Hecarim", "Teemo"], strongAgainst: ["Kassadin", "Riven"] },
    "Jax": { weakAgainst: ["Garen", "Cho'Gath", "Sion"], strongAgainst: ["Fiora"] },
    "Camille": { weakAgainst: ["Jax", "Shen", "Fiora", "Garen", "Teemo"], strongAgainst: [] },
    "Darius": { weakAgainst: ["Volibear", "Warwick", "Trundle"], strongAgainst: ["Malphite"] },
    "Jayce": { weakAgainst: ["Dr. Mundo", "Rumble", "Nasus", "Olaf"], strongAgainst: [] },
    "Gnar": { weakAgainst: ["Gangplank", "Vayne", "Renekton", "Irelia"], strongAgainst: [] }
};

/* ===== 完整符文方向（Patch 26.19） ===== */
const runeDirections = {
    "长手消耗": {
        label: "长手消耗型",
        desc: "适配所有射程 550 以上的传统法师，核心逻辑是对线有压制、换血不亏蓝、团战有 CD。",
        champions: ["Viktor","Lux","Xerath","Ziggs","Brand","Zyra","Vel'Koz","Hwei","Syndra","Orianna","Anivia","Corki","Twisted Fate","Zoe","Malzahar","Lissandra"],
        primary: { tree: "Sorcery（巫术系）", keystone: "Summon Aery（召唤艾莉）", runes: ["Manaflow Band（法力流系带）","Transcendence（超然）","Scorch（焦灼）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Magical Footwear（神奇之靴）","Biscuit Delivery（饼干配送）"] },
        shards: ["Adaptive Force","Adaptive Force","Health"],
        note: "艾莉比奥术彗星更稳定，技能命中即触发伤害。法力流系带解决前期缺蓝，超然提供 15 技能急速，焦灼每 10 秒附加额外魔法伤害。",
        source: "OP.GG 2026 年 7-10 月全分段排位数据统计"
    },
    "爆发刺客": {
        label: "爆发刺客型",
        desc: "适配刺客类法师，核心逻辑是短时间集中火力秒杀脆皮或关键目标。",
        champions: ["Akali","Fizz","LeBlanc","Katarina","Zed","Talon","Kassadin","Diana","Ekko","Sylas","Qiyana","Naafiri","Vex","Aurora","Ambessa"],
        primary: { tree: "Domination（主宰系）", keystone: "Electrocute（电刑）", runes: ["Sudden Impact（猛然冲击）","Eyeball Collection（眼球收集器）","Relentless Hunter（无情猎手）"] },
        secondary: { tree: "Sorcery（巫术系）", runes: ["Transcendence（超然）","Scorch（焦灼）"] },
        shards: ["Adaptive Force","Adaptive Force","Magic Resist"],
        note: "电刑在 3 秒内用 3 个独立攻击或技能命中英雄时造成额外伤害。猛然冲击提供穿透，无情猎手提升游走效率。",
        source: "Metabot 26.18 版本数据"
    },
    "法坦功能": {
        label: "法坦 / 功能型",
        desc: "适配需要前排承伤或团队功能的中路法师，核心逻辑是余震触发双抗 + 骸骨镀层挡爆发。",
        champions: ["Galio","Swain","Ryze","Vladimir","Sylas","Gragas","Singed","Kennen","Lulu","Seraphine","Karma"],
        primary: { tree: "Resolve（坚决系）", keystone: "Aftershock（余震）", runes: ["Bone Plating（骸骨镀层）","Second Wind（复苏之风）","Overgrowth（过度生长）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Biscuit Delivery（饼干配送）","Cosmic Insight（星界洞悉）"] },
        shards: ["Adaptive Force","Armor","Health"],
        note: "余震在控住敌人后提供双抗，骸骨镀层挡爆发，过度生长叠生命值。",
        source: "Metabot 26.18 版本数据"
    },
    "持续输出": {
        label: "持续输出型",
        desc: "适配需要长时间站场输出的法师，核心逻辑是风暴狂涌进场 + 骸骨镀层保命。",
        champions: ["Ryze","Vladimir","Cassiopeia","Swain","Aurelion Sol","Anivia","Karthus","Ziggs"],
        primary: { tree: "Sorcery（巫术系）", keystone: "Stormraider's Surge（风暴掠袭者的狂涌）", runes: ["Manaflow Band（法力流系带）","Transcendence（超然）","Gathering Storm（风暴聚集）"] },
        secondary: { tree: "Resolve（坚决系）", runes: ["Bone Plating（骸骨镀层）","Overgrowth（过度生长）"] },
        shards: ["Adaptive Force","Adaptive Force","Health"],
        note: "风暴狂涌在 3 秒内造成目标 25% 最大生命值伤害时提供移速与爆发。",
        source: "Metabot 26.18 版本数据"
    },
    "打野征服者": {
        label: "打野征服者（战士型）",
        desc: "适配需要持续作战与单挑能力的打野战士，核心逻辑是征服者叠层 + 黑切削甲。",
        champions: ["Lee Sin","Jarvan IV","Vi","Xin Zhao","Hecarim","Warwick","Volibear","Wukong","Sett","Ambessa","Kled","Rek'Sai","Trundle","Olaf"],
        primary: { tree: "Precision（精密系）", keystone: "Conqueror（征服者）", runes: ["Triumph（凯旋）","Legend: Alacrity（传说：欢欣）","Last Stand（坚毅不倒）"] },
        secondary: { tree: "Domination（主宰系）", runes: ["Sudden Impact（猛然冲击）","Treasure Hunter（宝藏猎人）"] },
        shards: ["Adaptive Force","Adaptive Force","Health Scaling"],
        note: "征服者叠满后提供持续作战能力，猛然冲击配合位移技能触发穿透。",
        source: "OP.GG 26.1 版本数据"
    },
    "打野收割": {
        label: "打野黑暗收割（刺客型）",
        desc: "适配需要游走抓单与后期收割的打野刺客，核心逻辑是黑暗收割叠层 + 猛然冲击穿透。",
        champions: ["Nidalee","Kha'Zix","Rengar","Evelynn","Elise","Shaco","Kayn","Nocturne","Briar","Bel'Veth","Viego","Talon"],
        primary: { tree: "Domination（主宰系）", keystone: "Dark Harvest（黑暗收割）", runes: ["Sudden Impact（猛然冲击）","Eyeball Collection（眼球收集器）","Treasure Hunter（宝藏猎人）"] },
        secondary: { tree: "Sorcery（巫术系）", runes: ["Transcendence（超然）","Water Walking（水上行走）"] },
        shards: ["Adaptive Force","Adaptive Force","Health Scaling"],
        note: "黑暗收割每次击杀英雄或大型野怪后永久提升伤害。水上行走提供河道移速。",
        source: "OP.GG 26.2 版本数据"
    },
    "上路征服者": {
        label: "上路征服者（持续作战）",
        desc: "适配需要持续换血与单带的上路战士，核心逻辑是征服者叠层 + 骸骨镀层换血。",
        champions: ["Aatrox","Darius","Riven","Camille","Fiora","Jax","Garen","Renekton","Sett","Ambessa","Kled","Gwen","Irelia","Yasuo","Yone"],
        primary: { tree: "Precision（精密系）", keystone: "Conqueror（征服者）", runes: ["Triumph（凯旋）","Legend: Alacrity（传说：欢欣）","Last Stand（坚毅不倒）"] },
        secondary: { tree: "Resolve（坚决系）", runes: ["Bone Plating（骸骨镀层）","Second Wind（复苏之风）"] },
        shards: ["Adaptive Force","Adaptive Force","Health"],
        note: "征服者叠满后提供 AD 与吸血，骸骨镀层挡对手一套连招。",
        source: "OP.GG 26.5 版本数据"
    },
    "上单不灭": {
        label: "上单不灭之握（坦克型）",
        desc: "适配需要前排承伤与对线压制的坦克上路，核心逻辑是不灭之握换血 + 过度生长叠血。",
        champions: ["Malphite","Ornn","Shen","Maokai","Poppy","Sion","Cho'Gath","Dr. Mundo","Tahm Kench","Volibear","Singed","Ambessa"],
        primary: { tree: "Resolve（坚决系）", keystone: "Grasp of the Undying（不灭之握）", runes: ["Demolish（爆破）","Second Wind（复苏之风）","Overgrowth（过度生长）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Biscuit Delivery（饼干配送）","Magical Footwear（神奇之靴）"] },
        shards: ["Adaptive Force","Armor","Health"],
        note: "不灭之握每 4 秒强化下一次普攻，造成额外伤害并永久提升生命值。",
        source: "Metabot 26.18 版本数据"
    },
    "ADC精密": {
        label: "ADC 精密系（持续输出）",
        desc: "适配需要持续普攻输出的射手，核心逻辑是致命节奏 / 强攻叠层 + 攻速鞋 + 飓风。",
        champions: ["Jinx","Kalista","Ashe","Kog'Maw","Twitch","Vayne","Kai'Sa","Sivir","Xayah","Aphelios","Zeri","Smolder","Tristana"],
        primary: { tree: "Precision（精密系）", keystone: "Lethal Tempo（致命节奏）或 Press the Attack（强攻）", runes: ["Triumph（凯旋）","Legend: Bloodline（传说：血统）","Cut Down（砍倒）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Magical Footwear（神奇之靴）","Biscuit Delivery（饼干配送）"] },
        shards: ["Attack Speed","Adaptive Force","Health"],
        note: "致命节奏提供攻速上限突破，强攻强化三次普攻的额外伤害。砍倒对高血量前排效果显著。",
        source: "Mobalytics 26.19 版本数据"
    },
    "ADC迅捷": {
        label: "ADC 迅捷步法（对线压制）",
        desc: "适配需要前期对线压制的射手，核心逻辑是迅捷步法续航 + 过量治疗 + 坚毅不倒。",
        champions: ["Draven","Miss Fortune","Lucian","Caitlyn","Ezreal","Jhin","Varus","Senna"],
        primary: { tree: "Precision（精密系）", keystone: "Fleet Footwork（迅捷步法）", runes: ["Overheal（过量治疗）","Legend: Alacrity（传说：欢欣）","Last Stand（坚毅不倒）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Biscuit Delivery（饼干配送）","Cosmic Insight（星界洞悉）"] },
        shards: ["Attack Speed","Adaptive Force","Health"],
        note: "迅捷步法提供移速与治疗，过量治疗将溢出治疗转为护盾。",
        source: "17173 2026 年 6 月数据"
    },
    "辅助艾莉": {
        label: "辅助艾莉（护盾 / 消耗型）",
        desc: "适配需要消耗与护盾的辅助法师，核心逻辑是艾莉双触发 + 法力流系带 + 焦灼。",
        champions: ["Karma","Lulu","Soraka","Sona","Seraphine","Nami","Milio","Janna","Lux","Morgana","Zyra","Brand","Zilean"],
        primary: { tree: "Sorcery（巫术系）", keystone: "Summon Aery（召唤艾莉）", runes: ["Manaflow Band（法力流系带）","Transcendence（超然）","Scorch（焦灼）"] },
        secondary: { tree: "Resolve（坚决系）", runes: ["Bone Plating（骸骨镀层）","Second Wind（复苏之风）"] },
        shards: ["Adaptive Force","Adaptive Force","Health"],
        note: "艾莉在伤害敌人时飞向目标造成伤害，在保护队友时提供护盾。",
        source: "Mobalytics 26.19 版本数据"
    },
    "辅助余震": {
        label: "辅助余震（坦克 / 开团型）",
        desc: "适配需要先手开团与承伤的辅助坦克，核心逻辑是余震双抗 + 骸骨镀层 + 过度生长。",
        champions: ["Leona","Nautilus","Thresh","Blitzcrank","Alistar","Braum","Taric","Rell","Pyke","Rakan","Galio","Maokai","Poppy"],
        primary: { tree: "Resolve（坚决系）", keystone: "Aftershock（余震）", runes: ["Font of Life（生命源泉）","Bone Plating（骸骨镀层）","Overgrowth（过度生长）"] },
        secondary: { tree: "Inspiration（启迪系）", runes: ["Hextech Flashtraption（海克斯闪现）","Cosmic Insight（星界洞悉）"] },
        shards: ["Adaptive Force","Armor","Health"],
        note: "余震在控住敌人后提供双抗，生命源泉标记敌人让队友回复。",
        source: "OP.GG 26.19 版本数据"
    }
};

/* ===== 查找英雄对应的符文方向 ===== */
function getRuneDirection(championName) {
    for (const dir of Object.values(runeDirections)) {
        if (dir.champions && dir.champions.includes(championName)) {
            return dir;
        }
    }
    return null;
}

/* ===== 生成符文方向 HTML ===== */
function runeDirectionHTML(c) {
    const dir = getRuneDirection(c.name) || getRuneDirection(c.keyName);
    if (!dir) {
        const fallback = itemRuneNote(c);
        return `<h3>📜 符文方向</h3><p>${escapeHTML(fallback.rune)}</p>`;
    }
    const primaryRunes = dir.primary.runes.map(r => `<span class="tag">${escapeHTML(r)}</span>`).join('');
    const secondaryRunes = dir.secondary.runes.map(r => `<span class="tag">${escapeHTML(r)}</span>`).join('');
    const shards = dir.shards.map(s => `<span class="tag">${escapeHTML(s)}</span>`).join('');
    return `
        <h3>📜 符文方向 · ${escapeHTML(dir.label)}</h3>
        <div class="rune-direction">
            <p class="rune-desc">${escapeHTML(dir.desc)}</p>
            <div class="rune-tree">
                <div class="rune-row">
                    <span class="rune-label">主系</span>
                    <strong>${escapeHTML(dir.primary.tree)}</strong>
                    <span class="rune-keystone">${escapeHTML(dir.primary.keystone)}</span>
                </div>
                <div class="rune-row">${primaryRunes}</div>
            </div>
            <div class="rune-tree">
                <div class="rune-row">
                    <span class="rune-label">副系</span>
                    <strong>${escapeHTML(dir.secondary.tree)}</strong>
                </div>
                <div class="rune-row">${secondaryRunes}</div>
            </div>
            <div class="rune-tree">
                <div class="rune-row">
                    <span class="rune-label">碎片</span>
                    ${shards}
                </div>
            </div>
            <p class="rune-note">💡 ${escapeHTML(dir.note)}</p>
            <p class="rune-source">📊 數據來源：${escapeHTML(dir.source)}</p>
        </div>
    `;
}

const classMap = { Fighter: '戰士', Mage: '法師', Assassin: '刺客', Marksman: '射手', Support: '輔助', Tank: '坦克' };
let champions = [];
let ddragonData = {};

const splash = n => `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${n}_0.jpg`;
const icon = n => `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/champion/${n}.png`;
const spellIcon = n => `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/spell/${n}.png`;

function slugify(n) { return String(n || '').toLowerCase().replace(/&/g, '').replace(/[.'’]/g, '').replace(/[^a-z0-9]+/g, ''); }
const slugOverrides = { 'Nunu & Willump': 'nunu', 'Dr. Mundo': 'drmundo' };
function guideUrl(c) { return LiveGuideBase + (slugOverrides[c.keyName] || slugify(c.keyName || c.name)); }
function counterUrl(c) {
    const role = (c.roles && c.roles[0]) || '中路';
    return CounterBase + (slugOverrides[c.keyName] || slugify(c.keyName || c.name)) + '/' + (roleSlug[role] || 'middle');
}
function difficulty(info) { const d = Number(info.info?.difficulty || 5); return d <= 3 ? '簡單' : d <= 6 ? '中等' : '困難'; }
function playstyle(c) {
    const tags = c.tags || [];
    if (tags.includes('Assassin')) return '刺客爆發／側翼切入';
    if (tags.includes('Marksman')) return '遠程持續輸出／安全站位';
    if (tags.includes('Tank')) return '前排承傷／開戰或保護';
    if (tags.includes('Support')) return '控制／保護／團隊功能';
    if (tags.includes('Mage')) return '技能消耗／控場／爆發';
    return '戰士近戰／持續作戰';
}
function itemRuneNote(c) {
    const tags = c.tags || [];
    if (tags.includes('Marksman')) return { rune: '以 Precision 系為核心，按對線選擇攻速、持續輸出或爆發型符文。', items: '鞋子＋核心攻擊裝，再按敵方前排、護甲與爆發調整。' };
    if (tags.includes('Mage')) return { rune: '以 Sorcery／Domination 為主，按射程、爆發或控場需求調整。', items: '法穿／法強／技能急速核心，再按敵方魔抗與威脅調整。' };
    if (tags.includes('Assassin')) return { rune: '以 Domination 或 Precision 的爆發／追擊方向為主。', items: '穿透／爆發／技能急速，視敵方脆皮與護甲調整。' };
    if (tags.includes('Tank')) return { rune: '以 Resolve 為主，按換血、開戰或反開需求選擇。', items: '生命值＋抗性＋團隊功能裝，按敵方傷害類型調整。' };
    if (tags.includes('Support')) return { rune: '按開戰、保護、消耗或功能性選擇 Resolve／Sorcery／Inspiration。', items: '輔助裝＋鞋子＋視野與團隊功能裝。' };
    return { rune: '以 Precision／Resolve 等耐久或持續作戰方向為主，按對線調整。', items: '戰士核心裝＋鞋子，再按敵方護甲、魔抗與控制調整。' };
}

function renderBuilds() {
    const presets = [
        ['符文', '📜', '符文不是固定答案：以目前角色定位與對線任務選擇主系，再用副系補足弱點。'],
        ['裝備', '🛒', '裝備需要按 26.19 對局調整；網站提供即時 Build 頁，避免把舊版本出裝當成固定答案。'],
        ['技能', '⚡', 'Q/W/E/R 技能名稱與描述直接來自 Data Dragon 16.19.1。'],
        ['Counter', '⚔', 'Counter 會連到當前 Ranked matchup 資料頁；勝率會隨版本、段位、地區及樣本量變化。']
    ];
    const grid = $('buildGrid');
    if (!grid) return;
    grid.innerHTML = presets.map(x => `<article class="build-card"><div class="icon">${x[1]}</div><span class="tag">${x[0]}</span><h3>${x[0]}資料</h3><p>${x[2]}</p></article>`).join('');
}

const styles = [
    ['💥', '爆發秒殺', '短時間集中火力，找脆皮或關鍵目標。'],
    ['🏹', '遠程消耗', '利用射程與技能壓低血量，再找進場窗口。'],
    ['🛡️', '坦克開戰', '吸收傷害、控制敵人並製造空間。'],
    ['🪓', '單帶推塔', '用邊線壓力迫使敵方分人處理。'],
    ['🌲', '野區入侵', '掌握位置後爭奪野怪與地圖資源。'],
    ['🪽', '全球支援', '利用高機動或遠距技能改變其他區域戰況。'],
    ['🧲', '保護核心', '圍繞主要輸出建立安全輸出環境。'],
    ['🎯', '反開戰', '等待敵方先手，再用控制或反擊接管戰鬥。']
];

const articles = [
    ['新手', '英雄池點樣建立？', '先固定一至兩個位置，再逐步擴大英雄池。'],
    ['對線', '兵線控制基本功', '推線、慢推、控線與回城時機會直接影響換血與支援。'],
    ['打野', 'Gank 前先睇三樣嘢', '兵線、召喚師技能與視野通常比見人就 Gank 更重要。'],
    ['團戰', '入場前五秒檢查表', '位置、視野、關鍵技能、隊友距離與目標都要先確認。'],
    ['裝備', '唔好死跟一套出裝', '敵方傷害類型、前排厚度與你的任務不同，裝備就應不同。'],
    ['符文', '符文係玩法方向盤', '先決定換血、發育、追擊、保護還是團戰，再選符文。']
];

function renderStyles() {
    const el = $('styleGrid');
    if (!el) return;
    el.innerHTML = styles.map(s => `<article class="style-card"><b>${s[0]} ${s[1]}</b><p>${s[2]}</p></article>`).join('');
}

function renderArticles(cat = 'all') {
    const el = $('articleGrid');
    if (!el) return;
    el.innerHTML = articles.filter(a => cat === 'all' || a[0] === cat).map(a =>
        `<article class="article-card"><small>${a[0]}</small><h3>${a[1]}</h3><p>${a[2]}</p><button class="small-btn readArticle" data-title="${escapeHTML(a[1])}" data-text="${escapeHTML(a[2])}">閱讀摘要</button></article>`
    ).join('');
    document.querySelectorAll('.readArticle').forEach(b => b.onclick = () => toast(b.dataset.title + '：' + b.dataset.text));
}

function renderChampions() {
    const grid = $('champGrid');
    if (!grid) return;
    const q = ($('champSearch')?.value || '').toLowerCase().trim();
    const role = $('champRole')?.value || 'all';
    const cls = $('champClass')?.value || 'all';
    const diff = $('champDifficulty')?.value || 'all';
    const list = champions.filter(c =>
        (role === 'all' || c.roles.includes(role)) &&
        (cls === 'all' || c.classes.includes(cls)) &&
        (diff === 'all' || c.difficulty === diff) &&
        `${c.name} ${c.style} ${c.roles.join(' ')} ${c.classes.join(' ')}`.toLowerCase().includes(q)
    );
    const count = $('resultCount');
    if (count) count.textContent = list.length;
    grid.innerHTML = list.map(c =>
        `<article class="champ" data-name="${escapeHTML(c.name)}"><img src="${splash(c.img)}" alt="${escapeHTML(c.name)}" loading="lazy" onerror="this.style.display='none'"><div class="champ-info">${c.roles.map(r => `<span class="tag">${r}</span>`).join('')}<span class="tag">${escapeHTML(c.classes.join('／'))}</span><span class="tag">${c.difficulty}</span><h3>${escapeHTML(c.name)}</h3><p>${escapeHTML(c.style)}</p></div></article>`
    ).join('');
    const empty = $('emptyChamp');
    if (empty) empty.style.display = list.length ? 'none' : 'block';
    document.querySelectorAll('.champ').forEach(x => x.onclick = () => openChampion(x.dataset.name));
}

function abilityHTML(c) {
    const pass = c.passive ? `<div class="ability-card"><img src="${spellIcon(c.passive.image.full)}" onerror="this.style.display='none'"><div><b>被動｜${escapeHTML(c.passive.name)}</b><p>${escapeHTML(cleanRiotText(c.passive.description))}</p></div></div>` : '';
    const letters = ['Q', 'W', 'E', 'R'];
    const spells = (c.spells || []).slice(0, 4).map((s, i) => `<div class="ability-card"><img src="${spellIcon(s.image.full)}" onerror="this.style.display='none'"><div><b>${letters[i]}｜${escapeHTML(s.name)}</b><p>${escapeHTML(cleanRiotText(s.description))}</p></div></div>`).join('');
    return pass + spells;
}

function openChampion(name) {
    const c = champions.find(x => x.name === name);
    if (!c) return;
    const tips = (c.enemytips || []).slice(0, 3).map(x => `<li>${escapeHTML(cleanRiotText(x))}</li>`).join('');
    const guide = guideUrl(c);
    const counter = counterUrl(c);
    const build = itemRuneNote(c);
    const body = $('modalBody');
    if (!body) return;

    const aliases = championAliases[c.name] || championAliases[c.keyName] || [];
    const aliasHTML = aliases.length
        ? `<p class="champ-aliases">🏷️ 玩家常用稱呼：${aliases.map(a => `<span class="tag">${escapeHTML(a)}</span>`).join('')}</p>`
        : '';

    const quote = championQuotes[c.name] || championQuotes[c.keyName] || '';
    const quoteHTML = quote ? `<blockquote class="champ-quote">「${escapeHTML(quote)}」</blockquote>` : '';

    const counterData = championCounters[c.name] || null;
    let counterHTML = '';
    if (counterData) {
        const weak = (counterData.weakAgainst || []).map(n => {
            const t = champions.find(x => x.name === n);
            return t ? `<span class="tag counter-weak">${escapeHTML(t.name)}</span>` : '';
        }).join('');
        const strong = (counterData.strongAgainst || []).map(n => {
            const t = champions.find(x => x.name === n);
            return t ? `<span class="tag counter-strong">${escapeHTML(t.name)}</span>` : '';
        }).join('');
        if (weak || strong) {
            counterHTML = `<h3>⚔ 對線克制參考</h3><div class="counter-section">`;
            if (weak) counterHTML += `<p><span class="counter-label weak">較難打</span> ${weak}</p>`;
            if (strong) counterHTML += `<p><span class="counter-label strong">較好打</span> ${strong}</p>`;
            counterHTML += `</div>`;
        }
    }

    body.innerHTML = `
        <div class="champ-modal-head">
            <img src="${icon(c.img)}" alt="${escapeHTML(c.name)}">
            <div>
                <span class="tag">${c.roles.join('／')}</span>
                <span class="tag">${escapeHTML(c.classes.join('／'))}</span>
                <span class="tag">${c.difficulty}</span>
                <h2>⚔ ${escapeHTML(c.name)}</h2>
                <p>${escapeHTML(c.title || '')}</p>
            </div>
        </div>
        ${aliasHTML}
        ${quoteHTML}
        <h3>⚡ 被動 / Q / W / E / R</h3>
        <div class="ability-grid">${abilityHTML(c)}</div>
        <h3>🎯 玩法</h3>
        <p>${escapeHTML(c.style)}。${escapeHTML(cleanRiotText(c.blurb || ''))}</p>
        ${runeDirectionHTML(c)}
        <h3>🛒 裝備方向</h3>
        <p>${escapeHTML(build.items)}</p>
        ${counterHTML}
        <div class="modal-links">
            <a class="small-btn" href="${guide}" target="_blank" rel="noopener">查看 26.19 Build／符文／技能順序</a>
            <a class="small-btn" href="${counter}" target="_blank" rel="noopener">查看 26.19 Counter／對線</a>
        </div>
        <h3>🧠 官方對手提示</h3>
        <ul>${tips || '<li>此英雄目前資料未提供額外對手提示。</li>'}</ul>
    `;

    const modal = $('modal');
    if (modal) { modal.classList.add('show'); modal.setAttribute('aria-hidden', 'false'); }
}

function renderCounter() {
    const sel = $('counterChamp');
    const out = $('counterResult');
    if (!sel || !out) return;
    const name = sel.value;
    const c = champions.find(x => x.name === name);
    if (!c) return;
    const role = (c.roles && c.roles[0]) || '中路';
    const url = counterUrl(c);
    out.innerHTML = `<article class="counter-card"><span class="badge">Patch 26.19 · ${role}</span><h3>${escapeHTML(c.name)} 對線資料</h3><p>Counter 屬於統計資料，不是永久固定答案；不同段位、地區、樣本量與版本都可能改變結果。</p><p>你可以直接查看當前 Ranked matchup 頁面的實際對手與數據。</p><a class="small-btn" href="${url}" target="_blank" rel="noopener">開啟即時 Counter</a></article>`;
}

function toast(t) {
    const el = $('toast');
    if (!el) return;
    el.textContent = t;
    el.classList.add('show');
    clearTimeout(window.__toast);
    window.__toast = setTimeout(() => el.classList.remove('show'), 2800);
}

function renderComments() {
    const el = $('commentList');
    if (!el) return;
    const data = JSON.parse(localStorage.getItem('lolV4Comments') || '[]');
    el.innerHTML = data.length ? data.map(c => `<article class="comment"><header><strong>${escapeHTML(c.name)}</strong><span>${escapeHTML(c.time)}</span></header><p>${escapeHTML(c.text)}</p></article>`).join('') : '<div class="empty">暫時未有留言，第一個留言由你開始！</div>';
}

/* ===== 隨機英雄（跨頁支援） ===== */
function pickRandomChampion() {
    if (!champions.length) return null;
    return champions[Math.floor(Math.random() * champions.length)];
}

function handleRandomHero() {
    const modal = $('modal');
    if (modal && champions.length) {
        const c = pickRandomChampion();
        if (c) openChampion(c.name);
    } else {
        window.location.href = 'champions.html?random=1';
    }
}

async function loadGameData() {
    try {
        const res = await fetch(`${DDragonBase}/championFull.json`);
        if (!res.ok) throw new Error('Data Dragon load failed');
        const json = await res.json();
        ddragonData = json.data || {};
    } catch (e) {
        try {
            const res = await fetch(`${DDragonEnglish}/championFull.json`);
            const json = await res.json();
            ddragonData = json.data || {};
        } catch (e2) {
            console.warn('無法載入 Riot Data Dragon，將以內建離線資料運行。', e2);
        }
    }

    champions = championSeed.map(s => {
        const c = ddragonData[s.img] || ddragonData[s.name];
        if (!c) {
            return {
                name: s.name, keyName: s.name, img: s.img,
                roles: championRoleMap[s.name] || ['中路'],
                classes: ['未分類'], difficulty: '中等',
                style: '離線模式：英雄簡介暫未載入', spells: [], passive: null
            };
        }
        return {
            ...c, name: c.name || s.name, keyName: s.name, img: s.img,
            roles: championRoleMap[s.name] || ['中路'],
            classes: (c.tags || []).map(t => classMap[t] || t),
            difficulty: difficulty(c),
            style: playstyle(c)
        };
    });

    renderChampions();

    const select = $('counterChamp');
    if (select) {
        select.innerHTML = '';
        champions.forEach(c => {
            const o = document.createElement('option');
            o.value = c.name; o.textContent = c.name;
            select.appendChild(o);
        });
        renderCounter();
    }

    const params = new URLSearchParams(window.location.search);
    if (params.get('random') === '1') {
        const c = pickRandomChampion();
        if (c) setTimeout(() => openChampion(c.name), 200);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    renderStyles();
    renderArticles();
    renderBuilds();
    renderComments();

    ['champSearch', 'champRole', 'champClass', 'champDifficulty'].forEach(id => {
        const el = $(id);
        if (!el) return;
        el.addEventListener(id === 'champSearch' ? 'input' : 'change', renderChampions);
    });

    const clearBtn = $('clearFilters');
    if (clearBtn) clearBtn.onclick = () => {
        if ($('champSearch')) $('champSearch').value = '';
        if ($('champRole')) $('champRole').value = 'all';
        if ($('champClass')) $('champClass').value = 'all';
        if ($('champDifficulty')) $('champDifficulty').value = 'all';
        renderChampions();
    };

    const counterBtn = $('counterBtn');
    if (counterBtn) counterBtn.onclick = renderCounter;

    document.querySelectorAll('.article-filter').forEach(b => b.onclick = () => {
        document.querySelectorAll('.article-filter').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        renderArticles(b.dataset.cat);
    });

    const randomHero = $('randomHero');
    if (randomHero) randomHero.onclick = handleRandomHero;

    const themeBtn = $('themeBtn');
    if (themeBtn) themeBtn.onclick = () => {
        document.body.classList.toggle('light');
        themeBtn.textContent = document.body.classList.contains('light') ? '🌙' : '☀️';
        localStorage.setItem('lolTheme', document.body.classList.contains('light') ? 'light' : 'dark');
    };
    if (localStorage.getItem('lolTheme') === 'light' && themeBtn) themeBtn.click();

    const closeModal = $('closeModal');
    if (closeModal) closeModal.onclick = () => {
        const modal = $('modal');
        if (modal) { modal.classList.remove('show'); modal.setAttribute('aria-hidden', 'true'); }
    };

    const modal = $('modal');
    if (modal) modal.onclick = e => { if (e.target === modal && closeModal) closeModal.click(); };

    document.onkeydown = e => {
        const m = $('modal');
        if (e.key === 'Escape' && m && m.classList.contains('show') && $('closeModal')) $('closeModal').click();
    };

    const commentForm = $('commentForm');
    if (commentForm) commentForm.onsubmit = e => {
        e.preventDefault();
        const data = JSON.parse(localStorage.getItem('lolV4Comments') || '[]');
        data.unshift({
            name: $('commentName').value.trim(),
            text: $('commentText').value.trim(),
            time: new Date().toLocaleString('zh-HK')
        });
        localStorage.setItem('lolV4Comments', JSON.stringify(data.slice(0, 20)));
        commentForm.reset();
        renderComments();
        toast('留言已保存在這部裝置的瀏覽器。');
    };

    loadGameData();
});