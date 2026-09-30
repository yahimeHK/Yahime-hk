/* LOL攻略網站 V5 data layer - Patch 26.19 / Data Dragon 16.19.1 */
const DDragonVersion = '16.19.1';
const DDragonBase = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/zh_TW`;
const DDragonEnglish = `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/data/en_US`;
const LiveGuideBase = 'https://lanelore.com/champions/';
const CounterBase = 'https://www.leagueofgraphs.com/champions/counters/';
const $ = id => document.getElementById(id);
const escapeHTML = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));

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

const classMap = { Fighter: '戰士', Mage: '法師', Assassin: '刺客', Marksman: '射手', Support: '輔助', Tank: '坦克' };
let champions = [];
let ddragonData = {};
let runeData = [];
let itemData = {};

const splash = n => `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${n}_0.jpg`;
const icon = n => `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/champion/${n}.png`;
const spellIcon = n => `https://ddragon.leagueoflegends.com/cdn/${DDragonVersion}/img/spell/${n}.png`;

function slugify(n) {
    return String(n || '').toLowerCase().replace(/&/g, '').replace(/[.'’]/g, '').replace(/[^a-z0-9]+/g, '');
}

const slugOverrides = { 'Nunu & Willump': 'nunu', 'Dr. Mundo': 'drmundo' };
function guideUrl(c) { return LiveGuideBase + (slugOverrides[c.keyName] || slugify(c.keyName || c.name)); }
function counterUrl(c) {
    const role = (c.roles && c.roles[0]) || '中路';
    return CounterBase + (slugOverrides[c.keyName] || slugify(c.keyName || c.name)) + '/' + (roleSlug[role] || 'middle');
}
function classify(info) { return (info.tags || []).map(t => classMap[t] || t).join('／') || '未分類'; }
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

/* 裝備頁：玩法方向盤 */
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
    const pass = c.passive
        ? `<div class="ability-card"><img src="${spellIcon(c.passive.image.full)}" onerror="this.style.display='none'"><div><b>被動｜${escapeHTML(c.passive.name)}</b><p>${escapeHTML(c.passive.description)}</p></div></div>`
        : '';
    const letters = ['Q', 'W', 'E', 'R'];
    const spells = (c.spells || []).slice(0, 4).map((s, i) =>
        `<div class="ability-card"><img src="${spellIcon(s.image.full)}" onerror="this.style.display='none'"><div><b>${letters[i]}｜${escapeHTML(s.name)}</b><p>${escapeHTML(s.description).replace(/\n/g, ' ')}</p></div></div>`
    ).join('');
    return pass + spells;
}

function openChampion(name) {
    const c = champions.find(x => x.name === name);
    if (!c) return;
    const tips = (c.enemytips || []).slice(0, 3).map(x => `<li>${escapeHTML(x)}</li>`).join('');
    const guide = guideUrl(c);
    const counter = counterUrl(c);
    const build = itemRuneNote(c);
    const body = $('modalBody');
    if (!body) return;
    body.innerHTML =
        `<div class="champ-modal-head"><img src="${icon(c.img)}" alt="${escapeHTML(c.name)}"><div><span class="tag">${c.roles.join('／')}</span><span class="tag">${escapeHTML(c.classes.join('／'))}</span><span class="tag">${c.difficulty}</span><h2>⚔ ${escapeHTML(c.name)}</h2><p>${escapeHTML(c.title || '')}</p></div></div>` +
        `<h3>⚡ 被動 / Q / W / E / R</h3><div class="ability-grid">${abilityHTML(c)}</div>` +
        `<h3>🎯 玩法</h3><p>${escapeHTML(c.style)}。${escapeHTML(c.blurb || '')}</p>` +
        `<h3>📜 符文方向</h3><p>${escapeHTML(build.rune)}</p>` +
        `<h3>🛒 裝備方向</h3><p>${escapeHTML(build.items)}</p>` +
        `<div class="modal-links"><a class="small-btn" href="${guide}" target="_blank" rel="noopener">查看 26.19 Build／符文／技能順序</a><a class="small-btn" href="${counter}" target="_blank" rel="noopener">查看 26.19 Counter／對線</a></div>` +
        `<h3>🧠 官方對手提示</h3><ul>${tips || '<li>此英雄目前資料未提供額外對手提示。</li>'}</ul>`;
    const modal = $('modal');
    if (modal) {
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
    }
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
    el.innerHTML = data.length
        ? data.map(c => `<article class="comment"><header><strong>${escapeHTML(c.name)}</strong><span>${escapeHTML(c.time)}</span></header><p>${escapeHTML(c.text)}</p></article>`).join('')
        : '<div class="empty">暫時未有留言，第一個留言由你開始！</div>';
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
                name: s.name,
                keyName: s.name,
                img: s.img,
                roles: championRoleMap[s.name] || ['中路'],
                classes: ['未分類'],
                difficulty: '中等',
                style: '離線模式：英雄簡介暫未載入',
                spells: [],
                passive: null
            };
        }
        return {
            ...c,
            name: c.name || s.name,
            keyName: s.name,
            img: s.img,
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
            o.value = c.name;
            o.textContent = c.name;
            select.appendChild(o);
        });
        renderCounter();
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
    if (randomHero) randomHero.onclick = () => {
        const c = champions[Math.floor(Math.random() * champions.length)];
        if (c) openChampion(c.name);
    };

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
        if (modal) {
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
        }
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