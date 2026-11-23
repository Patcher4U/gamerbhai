import sys, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shorts2.py"), encoding="utf-8").read()
exec(src.split("# A) money")[0])   # helpers: bg, glow, brand, title_slide, rows_slide, text_slide, cta, render, colours

render("short-5-tips.mp4",[
 (title_slide([("6 GTA 6",140,PINK),("MISTAKES",150,ORANGE),("NEW PLAYERS MAKE",76,CYAN)],"Don't lose your cash",51),2.8),
 (text_slide("1. NOT BANKING",["Pocket cash is lost","when you're busted or wasted","Use ATMs + BuckMe often"],52,PINK),3.6),
 (text_slide("2. DYING WITH LOOT",["Jewels & drugs only pay","at a fence - lose the","cops before you sell"],53,ORANGE),3.6),
 (text_slide("3. NO DISGUISE",["Ski mask, hat or glasses","lower your heat","Have a getaway car ready"],54,CYAN),3.6),
 (text_slide("4. WRECKING CARS",["Damage = lower payout","Check for trackers","before selling"],55,PINK),3.6),
 (text_slide("5. SOLO GRIND",["Your partner helps","grab duffel bags","Use Jason AND Lucia"],56,GREEN),3.6),
 (text_slide("6. SAME STORE",["Robbed stores need","time to restock","Rotate your targets"],57,ORANGE),3.6),
 (cta(58),3.5)])

render("short-6-price.mp4",[
 (title_slide([("GTA 6",150,PINK),("PRICE",170,ORANGE)],"What it costs + how to pay less",61),2.8),
 (rows_slide("EDITIONS",[("Standard Edition","$79.99"),("Ultimate Edition","$99.99"),("Some stores (Standard)","around $60")],62,ORANGE),5),
 (text_slide("YOUR COUNTRY?",["Live price in 55+","local currencies","PKR, INR, AED, EUR..."],63,CYAN),3.8),
 (text_slide("BEWARE",["'Free GTA 6' or cheap keys","from random sellers","= scam or stolen"],64,PINK),3.6),
 (text_slide("ONLY ON",["PS5 + Xbox Series X|S","No PC version yet"],65,GREEN),3.2),
 (cta(66),3.5)])

render("short-7-game.mp4",[
 (title_slide([("FREE",170,GREEN),("NEON RACING",110,PINK),("GAME",150,ORANGE)],"Play in your browser - no download",71),2.8),
 (text_slide("HOW IT WORKS",["Dodge traffic, hit nitro","near-misses = combo points","Beat the leaderboard"],72,CYAN),3.8),
 (text_slide("MYSTERY PRIZE",["Top score when GTA 6","comes to PC wins","a mystery prize"],73,ORANGE),3.8),
 (text_slide("$100 LUCKY DRAW",["When we hit 50,000 players","one player wins $100","Free to enter"],74,PINK),3.8),
 (text_slide("PLAY NOW",["Phone or PC","No account needed","Sign in with Google to save"],75,GREEN),3.2),
 (cta(76),3.5)])
