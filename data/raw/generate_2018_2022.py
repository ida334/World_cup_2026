"""
Generates WorldCupMatches_2018_2022.csv and WorldCups_2018_2022.csv
in the same schema as the original Kaggle World Cup dataset.
Run once: python data/raw/generate_2018_2022.py
"""
import csv
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Tournament summaries ───────────────────────────────────────────────────────
TOURNAMENTS = [
    # Year, Country, Winner, Runners-Up, Third, Fourth, Goals, Teams, Matches, Attendance
    (2018, "Russia",  "France",    "Croatia", "Belgium",  "England", 169, 32, 64, 3031768),
    (2022, "Qatar",   "Argentina", "France",  "Croatia",  "Morocco", 172, 32, 64, 3404252),
]

# ── Match data ─────────────────────────────────────────────────────────────────
# Columns: Year, Datetime, Stage, Stadium, City, Home, HG, AG, Away,
#          WinCond, Att, HT_HG, HT_AG, Referee, Asst1, Asst2, RoundID, MatchID, HI, AI
# WinCond: "" normal | "AET" extra time | "Penalties" penalties
MATCHES = [
    # ── 2018 GROUP STAGE ──────────────────────────────────────────────────────
    # Group A
    (2018,"14 Jun 2018 - 18:00","Group A","Luzhniki Stadium","Moscow","Russia",5,0,"Saudi Arabia","",78011,2,0,"N. PITANA","H. MOEL","J. BELATTI",500,10001,"RUS","KSA"),
    (2018,"15 Jun 2018 - 15:00","Group A","Ekaterinburg Arena","Ekaterinburg","Egypt",0,1,"Uruguay","",32060,0,0,"R. IRMATOV","T. GADAEV","J. ABDUKHAMIDUV",500,10002,"EGY","URU"),
    (2018,"19 Jun 2018 - 21:00","Group A","Saint Petersburg Stadium","Saint Petersburg","Russia",3,0,"Egypt","",64468,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",500,10003,"RUS","EGY"),
    (2018,"20 Jun 2018 - 18:00","Group A","Rostov Arena","Rostov-on-Don","Uruguay",1,0,"Saudi Arabia","",41866,0,0,"R. MARAN","O. ALP","B. DUARTE",500,10004,"URU","KSA"),
    (2018,"25 Jun 2018 - 15:00","Group A","Samara Arena","Samara","Uruguay",3,0,"Russia","",41970,1,0,"W. MAZUR","J. SOARES","E. ACANDA",500,10005,"URU","RUS"),
    (2018,"25 Jun 2018 - 15:00","Group A","Volgograd Arena","Volgograd","Saudi Arabia",2,1,"Egypt","",32066,1,0,"N. HAVANTSEV","A. ESKANDARI","M. TORRES",500,10006,"KSA","EGY"),
    # Group B
    (2018,"15 Jun 2018 - 18:00","Group B","Saint Petersburg Stadium","Saint Petersburg","Morocco",0,1,"Iran","",63291,0,0,"E. RAMOS","J. GONCALVES","B. CAMARGO",501,10007,"MAR","IRN"),
    (2018,"15 Jun 2018 - 21:00","Group B","Fisht Stadium","Sochi","Portugal",3,3,"Spain","",40479,2,1,"G. ROCCHI","E. BINDONI","M. TONOLINI",501,10008,"POR","ESP"),
    (2018,"20 Jun 2018 - 15:00","Group B","Luzhniki Stadium","Moscow","Portugal",1,0,"Morocco","",78011,1,0,"R. IRMATOV","T. GADAEV","J. ABDUKHAMIDUV",501,10009,"POR","MAR"),
    (2018,"20 Jun 2018 - 21:00","Group B","Kazan Arena","Kazan","Iran",0,1,"Spain","",41986,0,0,"A. CUNHA","B. CAMARGO","B. DUARTE",501,10010,"IRN","ESP"),
    (2018,"25 Jun 2018 - 18:00","Group B","Mordovia Arena","Saransk","Iran",1,1,"Portugal","",41686,0,0,"M. GEIGER","F. HANSBERG","J. HURD",501,10011,"IRN","POR"),
    (2018,"25 Jun 2018 - 18:00","Group B","Kaliningrad Stadium","Kaliningrad","Spain",2,2,"Morocco","",35212,1,0,"C. SOTO","H. HADZIC","M. FARIDA",501,10012,"ESP","MAR"),
    # Group C
    (2018,"16 Jun 2018 - 12:00","Group C","Kazan Arena","Kazan","France",2,1,"Australia","",41284,1,1,"A. CUNHA","B. CAMARGO","B. DUARTE",502,10013,"FRA","AUS"),
    (2018,"16 Jun 2018 - 18:00","Group C","Mordovia Arena","Saransk","Peru",0,1,"Denmark","",40442,0,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",502,10014,"PER","DEN"),
    (2018,"21 Jun 2018 - 12:00","Group C","Samara Arena","Samara","Denmark",1,1,"Australia","",41732,1,1,"R. IRMATOV","T. GADAEV","J. ABDUKHAMIDUV",502,10015,"DEN","AUS"),
    (2018,"21 Jun 2018 - 18:00","Group C","Ekaterinburg Arena","Ekaterinburg","France",1,0,"Peru","",32325,0,0,"M. GEIGER","F. HANSBERG","J. HURD",502,10016,"FRA","PER"),
    (2018,"26 Jun 2018 - 15:00","Group C","Luzhniki Stadium","Moscow","Denmark",0,0,"France","",78011,0,0,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",502,10017,"DEN","FRA"),
    (2018,"26 Jun 2018 - 15:00","Group C","Fisht Stadium","Sochi","Australia",0,2,"Peru","",40515,0,2,"R. MARAN","O. ALP","B. CAMARGO",502,10018,"AUS","PER"),
    # Group D
    (2018,"16 Jun 2018 - 15:00","Group D","Spartak Stadium","Moscow","Argentina",1,1,"Iceland","",44190,1,0,"J. AGUILAR","J. ZUMBA","L. MORENO",503,10019,"ARG","ISL"),
    (2018,"16 Jun 2018 - 21:00","Group D","Kaliningrad Stadium","Kaliningrad","Croatia",2,0,"Nigeria","",34561,1,0,"N. HAVANTSEV","A. ESKANDARI","M. TORRES",503,10020,"CRO","NGA"),
    (2018,"21 Jun 2018 - 21:00","Group D","Nizhny Novgorod Stadium","Nizhny Novgorod","Argentina",0,3,"Croatia","",40597,0,1,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",503,10021,"ARG","CRO"),
    (2018,"22 Jun 2018 - 15:00","Group D","Volgograd Arena","Volgograd","Nigeria",2,0,"Iceland","",31608,2,0,"W. MAZUR","J. SOARES","E. ACANDA",503,10022,"NGA","ISL"),
    (2018,"26 Jun 2018 - 18:00","Group D","Rostov Arena","Rostov-on-Don","Iceland",1,2,"Croatia","",40791,0,1,"G. ROCCHI","E. BINDONI","M. TONOLINI",503,10023,"ISL","CRO"),
    (2018,"26 Jun 2018 - 18:00","Group D","Saint Petersburg Stadium","Saint Petersburg","Nigeria",1,2,"Argentina","",63369,0,1,"M. GEIGER","F. HANSBERG","J. HURD",503,10024,"NGA","ARG"),
    # Group E
    (2018,"17 Jun 2018 - 15:00","Group E","Rostov Arena","Rostov-on-Don","Brazil",1,1,"Switzerland","",41716,0,0,"C. SOTO","H. HADZIC","M. FARIDA",504,10025,"BRA","SUI"),
    (2018,"17 Jun 2018 - 18:00","Group E","Samara Arena","Samara","Costa Rica",0,1,"Serbia","",41219,0,0,"R. IRMATOV","T. GADAEV","J. ABDUKHAMIDUV",504,10026,"CRC","SRB"),
    (2018,"22 Jun 2018 - 21:00","Group E","Saint Petersburg Stadium","Saint Petersburg","Brazil",2,0,"Costa Rica","",64468,0,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",504,10027,"BRA","CRC"),
    (2018,"22 Jun 2018 - 18:00","Group E","Kaliningrad Stadium","Kaliningrad","Serbia",1,2,"Switzerland","",34691,0,0,"A. CUNHA","B. CAMARGO","B. DUARTE",504,10028,"SRB","SUI"),
    (2018,"27 Jun 2018 - 18:00","Group E","Nizhny Novgorod Stadium","Nizhny Novgorod","Switzerland",2,2,"Costa Rica","",40747,1,0,"H. AYDINUS","B. DURAN","T. ONGUN",504,10029,"SUI","CRC"),
    (2018,"27 Jun 2018 - 18:00","Group E","Spartak Stadium","Moscow","Serbia",0,2,"Brazil","",44287,0,1,"M. GEIGER","F. HANSBERG","J. HURD",504,10030,"SRB","BRA"),
    # Group F
    (2018,"17 Jun 2018 - 21:00","Group F","Luzhniki Stadium","Moscow","Germany",0,1,"Mexico","",78011,0,1,"A. FAGHANI","R. GHOST","M. MANSOURI",505,10031,"GER","MEX"),
    (2018,"18 Jun 2018 - 12:00","Group F","Nizhny Novgorod Stadium","Nizhny Novgorod","Sweden",1,0,"South Korea","",40502,0,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",505,10032,"SWE","KOR"),
    (2018,"23 Jun 2018 - 15:00","Group F","Rostov Arena","Rostov-on-Don","South Korea",1,2,"Mexico","",41000,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",505,10033,"KOR","MEX"),
    (2018,"23 Jun 2018 - 21:00","Group F","Fisht Stadium","Sochi","Germany",2,1,"Sweden","",40459,0,0,"C. SOTO","H. HADZIC","M. FARIDA",505,10034,"GER","SWE"),
    (2018,"27 Jun 2018 - 15:00","Group F","Kazan Arena","Kazan","South Korea",2,0,"Germany","",41416,0,0,"M. RODRIGUEZ","B. CAMARGO","B. DUARTE",505,10035,"KOR","GER"),
    (2018,"27 Jun 2018 - 15:00","Group F","Ekaterinburg Arena","Ekaterinburg","Mexico",0,3,"Sweden","",32206,0,2,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",505,10036,"MEX","SWE"),
    # Group G
    (2018,"18 Jun 2018 - 15:00","Group G","Fisht Stadium","Sochi","Belgium",3,0,"Panama","",41313,1,0,"G. ROCCHI","E. BINDONI","M. TONOLINI",506,10037,"BEL","PAN"),
    (2018,"18 Jun 2018 - 18:00","Group G","Volgograd Arena","Volgograd","Tunisia",1,2,"England","",32022,1,1,"A. CUNHA","B. CAMARGO","B. DUARTE",506,10038,"TUN","ENG"),
    (2018,"23 Jun 2018 - 18:00","Group G","Spartak Stadium","Moscow","Belgium",5,2,"Tunisia","",44015,3,1,"W. MAZUR","J. SOARES","E. ACANDA",506,10039,"BEL","TUN"),
    (2018,"24 Jun 2018 - 21:00","Group G","Nizhny Novgorod Stadium","Nizhny Novgorod","England",6,1,"Panama","",40601,5,0,"M. GEIGER","F. HANSBERG","J. HURD",506,10040,"ENG","PAN"),
    (2018,"28 Jun 2018 - 18:00","Group G","Kaliningrad Stadium","Kaliningrad","England",0,1,"Belgium","",34581,0,0,"D. ORSATO","M. CECCONI","F. PRETI",506,10041,"ENG","BEL"),
    (2018,"28 Jun 2018 - 18:00","Group G","Mordovia Arena","Saransk","Panama",1,2,"Tunisia","",40870,0,1,"N. HAVANTSEV","A. ESKANDARI","M. TORRES",506,10042,"PAN","TUN"),
    # Group H
    (2018,"19 Jun 2018 - 15:00","Group H","Mordovia Arena","Saransk","Colombia",1,2,"Japan","",40502,0,1,"D. ORSATO","M. CECCONI","F. PRETI",507,10043,"COL","JPN"),
    (2018,"19 Jun 2018 - 18:00","Group H","Spartak Stadium","Moscow","Poland",1,2,"Senegal","",44190,0,1,"J. AGUILAR","J. ZUMBA","L. MORENO",507,10044,"POL","SEN"),
    (2018,"24 Jun 2018 - 12:00","Group H","Ekaterinburg Arena","Ekaterinburg","Japan",2,2,"Senegal","",32572,1,1,"M. RODRIGUEZ","B. CAMARGO","B. DUARTE",507,10045,"JPN","SEN"),
    (2018,"24 Jun 2018 - 15:00","Group H","Kazan Arena","Kazan","Poland",0,3,"Colombia","",41845,0,2,"C. RAMOS","J. GONCALVES","B. DUARTE",507,10046,"POL","COL"),
    (2018,"28 Jun 2018 - 15:00","Group H","Volgograd Arena","Volgograd","Japan",0,1,"Poland","",32003,0,0,"M. GEIGER","F. HANSBERG","J. HURD",507,10047,"JPN","POL"),
    (2018,"28 Jun 2018 - 15:00","Group H","Samara Arena","Samara","Senegal",0,1,"Colombia","",41474,0,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",507,10048,"SEN","COL"),
    # ── 2018 KNOCKOUT ─────────────────────────────────────────────────────────
    # Round of 16
    (2018,"30 Jun 2018 - 15:00","Round of 16","Kazan Arena","Kazan","France",4,3,"Argentina","",42873,1,2,"C. RAMOS","J. GONCALVES","B. DUARTE",508,10049,"FRA","ARG"),
    (2018,"30 Jun 2018 - 19:00","Round of 16","Fisht Stadium","Sochi","Uruguay",2,1,"Portugal","",40978,1,1,"M. GEIGER","F. HANSBERG","J. HURD",508,10050,"URU","POR"),
    (2018,"01 Jul 2018 - 15:00","Round of 16","Luzhniki Stadium","Moscow","Spain",1,1,"Russia","Penalties",78011,1,1,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",508,10051,"ESP","RUS"),
    (2018,"01 Jul 2018 - 19:00","Round of 16","Nizhny Novgorod Stadium","Nizhny Novgorod","Croatia",1,1,"Denmark","Penalties",40800,0,0,"M. RODRIGUEZ","B. CAMARGO","B. DUARTE",508,10052,"CRO","DEN"),
    (2018,"02 Jul 2018 - 15:00","Round of 16","Samara Arena","Samara","Brazil",2,0,"Mexico","",41872,0,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",508,10053,"BRA","MEX"),
    (2018,"02 Jul 2018 - 19:00","Round of 16","Rostov Arena","Rostov-on-Don","Belgium",3,2,"Japan","",41604,0,2,"M. GEIGER","F. HANSBERG","J. HURD",508,10054,"BEL","JPN"),
    (2018,"03 Jul 2018 - 15:00","Round of 16","Saint Petersburg Stadium","Saint Petersburg","Sweden",1,0,"Switzerland","",64287,0,0,"C. SOTO","H. HADZIC","M. FARIDA",508,10055,"SWE","SUI"),
    (2018,"03 Jul 2018 - 19:00","Round of 16","Spartak Stadium","Moscow","Colombia",1,1,"England","Penalties",44190,0,0,"M. MAZUR","J. SOARES","E. ACANDA",508,10056,"COL","ENG"),
    # Quarter-finals
    (2018,"06 Jul 2018 - 15:00","Quarter-finals","Nizhny Novgorod Stadium","Nizhny Novgorod","Uruguay",0,2,"France","",40617,0,0,"A. FAGHANI","R. GHOST","M. MANSOURI",509,10057,"URU","FRA"),
    (2018,"06 Jul 2018 - 19:00","Quarter-finals","Kazan Arena","Kazan","Brazil",1,2,"Belgium","",42873,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",509,10058,"BRA","BEL"),
    (2018,"07 Jul 2018 - 15:00","Quarter-finals","Samara Arena","Samara","Sweden",0,2,"England","",41050,0,0,"C. SOTO","H. HADZIC","M. FARIDA",509,10059,"SWE","ENG"),
    (2018,"07 Jul 2018 - 19:00","Quarter-finals","Fisht Stadium","Sochi","Russia",2,2,"Croatia","Penalties",40734,1,1,"N. PITANA","H. MOEL","J. BELATTI",509,10060,"RUS","CRO"),
    # Semi-finals
    (2018,"10 Jul 2018 - 19:00","Semi-finals","Saint Petersburg Stadium","Saint Petersburg","France",1,0,"Belgium","",64286,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",510,10061,"FRA","BEL"),
    (2018,"11 Jul 2018 - 19:00","Semi-finals","Luzhniki Stadium","Moscow","Croatia",2,1,"England","AET",78011,1,1,"D. ORSATO","M. CECCONI","F. PRETI",510,10062,"CRO","ENG"),
    # 3rd place
    (2018,"14 Jul 2018 - 15:00","Match for third place","Saint Petersburg Stadium","Saint Petersburg","Belgium",2,0,"England","",64406,0,0,"M. RODRIGUEZ","B. CAMARGO","B. DUARTE",511,10063,"BEL","ENG"),
    # Final
    (2018,"15 Jul 2018 - 15:00","Final","Luzhniki Stadium","Moscow","France",4,2,"Croatia","",78011,2,1,"N. PITANA","H. MOEL","J. BELATTI",512,10064,"FRA","CRO"),

    # ── 2022 GROUP STAGE ──────────────────────────────────────────────────────
    # Group A
    (2022,"20 Nov 2022 - 17:00","Group A","Al Bayt Stadium","Al Khor","Qatar",0,2,"Ecuador","",67372,0,1,"D. ORSATO","M. CECCONI","F. PRETI",600,20001,"QAT","ECU"),
    (2022,"21 Nov 2022 - 14:00","Group A","Al Thumama Stadium","Doha","Senegal",0,2,"Netherlands","",41721,0,1,"C. RAMOS","J. GONCALVES","B. DUARTE",600,20002,"SEN","NED"),
    (2022,"25 Nov 2022 - 11:00","Group A","Al Thumama Stadium","Doha","Qatar",1,3,"Senegal","",44667,0,1,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",600,20003,"QAT","SEN"),
    (2022,"25 Nov 2022 - 17:00","Group A","Khalifa International Stadium","Doha","Ecuador",1,1,"Netherlands","",44846,1,1,"F. RAPALLINI","D. BONFA","G. CAMARGO",600,20004,"ECU","NED"),
    (2022,"29 Nov 2022 - 18:00","Group A","Al Bayt Stadium","Al Khor","Netherlands",2,0,"Qatar","",68895,1,0,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",600,20005,"NED","QAT"),
    (2022,"29 Nov 2022 - 18:00","Group A","Khalifa International Stadium","Doha","Ecuador",1,2,"Senegal","",44137,0,0,"M. OLIVER","S. BURT","A. NUNN",600,20006,"ECU","SEN"),
    # Group B
    (2022,"21 Nov 2022 - 17:00","Group B","Khalifa International Stadium","Doha","England",6,2,"Iran","",45334,3,2,"R. MARCINIAK","P. GIL","T. LISTKIEWICZ",601,20007,"ENG","IRN"),
    (2022,"21 Nov 2022 - 20:00","Group B","Ahmad Bin Ali Stadium","Al Rayyan","USA",1,1,"Wales","",43418,1,0,"M. CLATTENBURG","M. MCDONALD","D. WEBB",601,20008,"USA","WAL"),
    (2022,"25 Nov 2022 - 14:00","Group B","Ahmad Bin Ali Stadium","Al Rayyan","Wales",0,2,"Iran","",42127,0,0,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",601,20009,"WAL","IRN"),
    (2022,"25 Nov 2022 - 20:00","Group B","Al Bayt Stadium","Al Khor","England",0,0,"USA","",68895,0,0,"I. VALERI","M. MARGIANI","E. MORENTE",601,20010,"ENG","USA"),
    (2022,"29 Nov 2022 - 22:00","Group B","Ahmad Bin Ali Stadium","Al Rayyan","Wales",0,3,"England","",44297,0,2,"P. GOMES","B. CAMARGO","B. DUARTE",601,20011,"WAL","ENG"),
    (2022,"29 Nov 2022 - 22:00","Group B","Al Thumama Stadium","Doha","Iran",0,1,"USA","",42127,0,0,"A. GHEID","M. AKHONDALI","E. SADEGHI",601,20012,"IRN","USA"),
    # Group C
    (2022,"22 Nov 2022 - 13:00","Group C","Lusail Stadium","Lusail","Argentina",1,2,"Saudi Arabia","",88012,1,1,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",602,20013,"ARG","KSA"),
    (2022,"22 Nov 2022 - 16:00","Group C","Stadium 974","Doha","Mexico",0,0,"Poland","",40269,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",602,20014,"MEX","POL"),
    (2022,"26 Nov 2022 - 13:00","Group C","Education City Stadium","Al Rayyan","Poland",2,0,"Saudi Arabia","",43982,1,0,"M. OLIVER","S. BURT","A. NUNN",602,20015,"POL","KSA"),
    (2022,"26 Nov 2022 - 22:00","Group C","Lusail Stadium","Lusail","Argentina",2,0,"Mexico","",88966,0,0,"F. RAPALLINI","D. BONFA","G. CAMARGO",602,20016,"ARG","MEX"),
    (2022,"30 Nov 2022 - 22:00","Group C","Stadium 974","Doha","Poland",0,2,"Argentina","",44089,0,1,"D. ORSATO","M. CECCONI","F. PRETI",602,20017,"POL","ARG"),
    (2022,"30 Nov 2022 - 22:00","Group C","Lusail Stadium","Lusail","Saudi Arabia",1,2,"Mexico","",88012,0,1,"I. VALERI","M. MARGIANI","E. MORENTE",602,20018,"KSA","MEX"),
    # Group D
    (2022,"22 Nov 2022 - 19:00","Group D","Al Janoub Stadium","Al Wakrah","France",4,1,"Australia","",40423,2,1,"S. MOKRANI","M. AKHONDALI","E. SADEGHI",603,20019,"FRA","AUS"),
    (2022,"22 Nov 2022 - 22:00","Group D","Education City Stadium","Al Rayyan","Denmark",0,0,"Tunisia","",42925,0,0,"C. SOTO","H. HADZIC","M. FARIDA",603,20020,"DEN","TUN"),
    (2022,"26 Nov 2022 - 16:00","Group D","Stadium 974","Doha","France",2,1,"Denmark","",44144,1,1,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",603,20021,"FRA","DEN"),
    (2022,"26 Nov 2022 - 19:00","Group D","Al Janoub Stadium","Al Wakrah","Australia",1,0,"Tunisia","",40281,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",603,20022,"AUS","TUN"),
    (2022,"30 Nov 2022 - 18:00","Group D","Al Janoub Stadium","Al Wakrah","Australia",1,0,"Denmark","",40423,1,0,"M. OLIVER","S. BURT","A. NUNN",603,20023,"AUS","DEN"),
    (2022,"30 Nov 2022 - 18:00","Group D","Education City Stadium","Al Rayyan","France",0,1,"Tunisia","",40734,0,1,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",603,20024,"FRA","TUN"),
    # Group E
    (2022,"23 Nov 2022 - 14:00","Group E","Khalifa International Stadium","Doha","Germany",1,2,"Japan","",42608,1,0,"D. ORSATO","M. CECCONI","F. PRETI",604,20025,"GER","JPN"),
    (2022,"23 Nov 2022 - 17:00","Group E","Al Thumama Stadium","Doha","Spain",7,0,"Costa Rica","",42649,3,0,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",604,20026,"ESP","CRC"),
    (2022,"27 Nov 2022 - 11:00","Group E","Ahmad Bin Ali Stadium","Al Rayyan","Japan",0,1,"Costa Rica","",42980,0,0,"I. VALERI","M. MARGIANI","E. MORENTE",604,20027,"JPN","CRC"),
    (2022,"27 Nov 2022 - 17:00","Group E","Al Bayt Stadium","Al Khor","Germany",1,1,"Spain","",68895,0,1,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",604,20028,"GER","ESP"),
    (2022,"01 Dec 2022 - 22:00","Group E","Al Bayt Stadium","Al Khor","Germany",4,2,"Costa Rica","",68895,3,2,"D. ORSATO","M. CECCONI","F. PRETI",604,20029,"GER","CRC"),
    (2022,"01 Dec 2022 - 22:00","Group E","Khalifa International Stadium","Doha","Japan",2,1,"Spain","",44401,0,1,"V. TURPIN","C. MUGNIER","H. TAHIRI",604,20030,"JPN","ESP"),
    # Group F
    (2022,"23 Nov 2022 - 11:00","Group F","Al Bayt Stadium","Al Khor","Morocco",0,0,"Croatia","",68895,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",605,20031,"MAR","CRO"),
    (2022,"23 Nov 2022 - 20:00","Group F","Ahmad Bin Ali Stadium","Al Rayyan","Belgium",1,0,"Canada","",42843,0,0,"F. RAPALLINI","D. BONFA","G. CAMARGO",605,20032,"BEL","CAN"),
    (2022,"27 Nov 2022 - 14:00","Group F","Al Thumama Stadium","Doha","Morocco",2,0,"Belgium","",44261,0,0,"C. SOTO","H. HADZIC","M. FARIDA",605,20033,"MAR","BEL"),
    (2022,"27 Nov 2022 - 20:00","Group F","Khalifa International Stadium","Doha","Croatia",4,1,"Canada","",44401,2,0,"M. OLIVE","S. BURT","A. NUNN",605,20034,"CRO","CAN"),
    (2022,"01 Dec 2022 - 18:00","Group F","Ahmad Bin Ali Stadium","Al Rayyan","Croatia",0,0,"Belgium","",42127,0,0,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",605,20035,"CRO","BEL"),
    (2022,"01 Dec 2022 - 18:00","Group F","Al Thumama Stadium","Doha","Canada",1,2,"Morocco","",44297,1,0,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",605,20036,"CAN","MAR"),
    # Group G
    (2022,"24 Nov 2022 - 11:00","Group G","Al Janoub Stadium","Al Wakrah","Switzerland",1,0,"Cameroon","",40423,1,0,"M. GEIGER","F. HANSBERG","J. HURD",606,20037,"SUI","CMR"),
    (2022,"24 Nov 2022 - 20:00","Group G","Lusail Stadium","Lusail","Brazil",2,0,"Serbia","",88012,0,0,"F. RAPALLINI","D. BONFA","G. CAMARGO",606,20038,"BRA","SRB"),
    (2022,"28 Nov 2022 - 11:00","Group G","Al Janoub Stadium","Al Wakrah","Cameroon",3,3,"Serbia","",41689,1,1,"D. ORSATO","M. CECCONI","F. PRETI",606,20039,"CMR","SRB"),
    (2022,"28 Nov 2022 - 17:00","Group G","Stadium 974","Doha","Brazil",1,0,"Switzerland","",44137,0,0,"I. VALERI","M. MARGIANI","E. MORENTE",606,20040,"BRA","SUI"),
    (2022,"02 Dec 2022 - 22:00","Group G","Lusail Stadium","Lusail","Cameroon",1,0,"Brazil","",88966,0,0,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",606,20041,"CMR","BRA"),
    (2022,"02 Dec 2022 - 22:00","Group G","Stadium 974","Doha","Serbia",2,3,"Switzerland","",44264,1,2,"M. OLIVER","S. BURT","A. NUNN",606,20042,"SRB","SUI"),
    # Group H
    (2022,"24 Nov 2022 - 14:00","Group H","Education City Stadium","Al Rayyan","Uruguay",0,0,"South Korea","",42372,0,0,"C. SOTO","H. HADZIC","M. FARIDA",607,20043,"URU","KOR"),
    (2022,"24 Nov 2022 - 17:00","Group H","Stadium 974","Doha","Portugal",3,2,"Ghana","",44137,2,0,"M. GEIGER","F. HANSBERG","J. HURD",607,20044,"POR","GHA"),
    (2022,"28 Nov 2022 - 14:00","Group H","Education City Stadium","Al Rayyan","South Korea",2,3,"Ghana","",40425,0,2,"J. AGUILAR","J. ZUMBA","L. MORENO",607,20045,"KOR","GHA"),
    (2022,"28 Nov 2022 - 20:00","Group H","Lusail Stadium","Lusail","Portugal",2,0,"Uruguay","",88012,0,0,"C. RAMOS","J. GONCALVES","B. DUARTE",607,20046,"POR","URU"),
    (2022,"02 Dec 2022 - 18:00","Group H","Education City Stadium","Al Rayyan","South Korea",2,1,"Portugal","",43667,0,1,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",607,20047,"KOR","POR"),
    (2022,"02 Dec 2022 - 18:00","Group H","Al Janoub Stadium","Al Wakrah","Ghana",0,2,"Uruguay","",40565,0,1,"B. MARINI","S. ARCIDIACONO","T. DEL PALACIO",607,20048,"GHA","URU"),
    # ── 2022 KNOCKOUT ─────────────────────────────────────────────────────────
    # Round of 16
    (2022,"03 Dec 2022 - 18:00","Round of 16","Khalifa International Stadium","Doha","Netherlands",3,1,"USA","",44846,2,1,"I. VALERI","M. MARGIANI","E. MORENTE",608,20049,"NED","USA"),
    (2022,"03 Dec 2022 - 22:00","Round of 16","Ahmad Bin Ali Stadium","Al Rayyan","Argentina",2,1,"Australia","",45032,1,0,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",608,20050,"ARG","AUS"),
    (2022,"04 Dec 2022 - 18:00","Round of 16","Al Thumama Stadium","Doha","France",3,1,"Poland","",44624,1,1,"C. SOTO","H. HADZIC","M. FARIDA",608,20051,"FRA","POL"),
    (2022,"04 Dec 2022 - 22:00","Round of 16","Al Bayt Stadium","Al Khor","England",3,0,"Senegal","",67781,2,0,"F. RAPALLINI","D. BONFA","G. CAMARGO",608,20052,"ENG","SEN"),
    (2022,"05 Dec 2022 - 18:00","Round of 16","Al Janoub Stadium","Al Wakrah","Japan",1,1,"Croatia","Penalties",40267,0,0,"D. ORSATO","M. CECCONI","F. PRETI",608,20053,"JPN","CRO"),
    (2022,"05 Dec 2022 - 22:00","Round of 16","Stadium 974","Doha","Brazil",4,1,"South Korea","",44567,2,0,"M. OLIVER","S. BURT","A. NUNN",608,20054,"BRA","KOR"),
    (2022,"06 Dec 2022 - 18:00","Round of 16","Education City Stadium","Al Rayyan","Morocco",0,0,"Spain","Penalties",44137,0,0,"A. LAHOZ","P. CEBRIAN","R. DEL PALOMAR",608,20055,"MAR","ESP"),
    (2022,"06 Dec 2022 - 22:00","Round of 16","Lusail Stadium","Lusail","Portugal",6,1,"Switzerland","",88966,3,0,"V. TURPIN","C. MUGNIER","H. TAHIRI",608,20056,"POR","SUI"),
    # Quarter-finals
    (2022,"09 Dec 2022 - 18:00","Quarter-finals","Education City Stadium","Al Rayyan","Croatia",1,1,"Brazil","Penalties",44846,0,0,"M. CLATTENBURG","M. MCDONALD","D. WEBB",609,20057,"CRO","BRA"),
    (2022,"09 Dec 2022 - 22:00","Quarter-finals","Lusail Stadium","Lusail","Netherlands",2,2,"Argentina","Penalties",88012,0,0,"D. ORSATO","M. CECCONI","F. PRETI",609,20058,"NED","ARG"),
    (2022,"10 Dec 2022 - 18:00","Quarter-finals","Al Thumama Stadium","Doha","Morocco",1,0,"Portugal","",44615,1,0,"F. RAPALLINI","D. BONFA","G. CAMARGO",609,20059,"MAR","POR"),
    (2022,"10 Dec 2022 - 22:00","Quarter-finals","Al Bayt Stadium","Al Khor","France",2,1,"England","",68895,1,1,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",609,20060,"FRA","ENG"),
    # Semi-finals
    (2022,"13 Dec 2022 - 22:00","Semi-finals","Lusail Stadium","Lusail","Argentina",3,0,"Croatia","",88966,2,0,"C. SOTO","H. HADZIC","M. FARIDA",610,20061,"ARG","CRO"),
    (2022,"14 Dec 2022 - 22:00","Semi-finals","Al Bayt Stadium","Al Khor","France",2,0,"Morocco","",68895,1,0,"I. VALERI","M. MARGIANI","E. MORENTE",610,20062,"FRA","MAR"),
    # 3rd place
    (2022,"17 Dec 2022 - 18:00","Match for third place","Khalifa International Stadium","Doha","Croatia",2,1,"Morocco","",44137,1,1,"V. TURPIN","C. MUGNIER","H. TAHIRI",611,20063,"CRO","MAR"),
    # Final
    (2022,"18 Dec 2022 - 18:00","Final","Lusail Stadium","Lusail","Argentina",3,3,"France","Penalties",88966,2,2,"S. MARCINIAK","P. GIL","T. LISTKIEWICZ",612,20064,"ARG","FRA"),
]

HEADERS_MATCHES = [
    "Year","Datetime","Stage","Stadium","City",
    "Home Team Name","Home Team Goals","Away Team Goals","Away Team Name",
    "Win conditions","Attendance",
    "Half-time Home Goals","Half-time Away Goals",
    "Referee","Assistant 1","Assistant 2",
    "RoundID","MatchID","Home Team Initials","Away Team Initials"
]

HEADERS_CUPS = [
    "Year","Country","Winner","Runners-Up","Third","Fourth",
    "GoalsScored","QualifiedTeams","MatchesPlayed","Attendance"
]

def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"Written {len(rows)} rows to file")

if __name__ == "__main__":
    write_csv(os.path.join(OUT_DIR, "WorldCupMatches_2018_2022.csv"), HEADERS_MATCHES, MATCHES)
    write_csv(os.path.join(OUT_DIR, "WorldCups_2018_2022.csv"), HEADERS_CUPS, TOURNAMENTS)
    print("Done.")
