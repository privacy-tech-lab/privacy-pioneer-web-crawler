countries = ['australia', 'brazil', 'canada', 'germany', 'india', 'singapore', 'southafrica', 'southkorea', 'spain', 'unitedstates']
typs = ['analytics', 'advertising', 'social', 'fingerprinting', 'trackingPixel', 'possiblePixel', 'ipAddress', 'region', 'city', 'coarseLocation', 'fineLocation', 'zipCode']

# The three privacy permission categories tracked by Privacy Pioneer.
permissions = ['monetization', 'location', 'tracking']

# Maps internal country codes to display names used in chart titles and axes.
country_mapping = {
    'unitedstates': 'United States',
    'australia':    'Australia',
    'southafrica':  'South Africa',
    'canada':       'Canada',
    'india':        'India',
    'brazil':       'Brazil',
    'southkorea':   'South Korea',
    'singapore':    'Singapore',
    'germany':      'Germany',
    'spain':        'Spain',
}

# fix_map: manual corrections applied during preprocessing.
# Each entry is [domain_keyword, rank_in_top_525] where rank == -1 means
# the site should be removed entirely (it does not belong in the crawl list).
fix_map = {
    "australia": [
        ['adfixus', -1], ['ardc', 245], ['leapfrogmarket', 486], ['econnection', 482],
        ["foundryco", 309], ["australiaonline", 274], ['clickvieweducation', 510],
        ['library', 29], ['mammoth', 403],
    ],
    "brazil": [
        ['king', 23], ['noticiabrasil', 475], ['portaldatorcida10', 80], ['portaln10', 266],
        ['unifique', 382], ["3cx", 473], ['alaresinternet', 249], ['ifood', 265],
        ['umbler', 194],
    ],
    "canada": [
        ['montrealbits', 261], ['dns', 395], ['easydns', 451], ['idrc-crdi', 233],
        ['microsoftonline', 87], ['money', 406], ['stingray', 213], ['perfdrive', -1],
        ['alphagroup', 319], ['dayforce', -1], ['godaddy', 272], ['govstack', 465],
        ['houseful', 506], ['senecapolytechnic', 228], ['ulethbridge', 239],
    ],
    "germany": [
        ['immunocapexplorer', 278], ['mindcurvgroup', 418], ['lexware', 396],
        ['fully-kiosk', 413], ['goethe-university-frankfurt', 123], ['stroeer', 349],
        ['wiit', 155],
    ],
    "india": [
        ['ggsmch', 497], ['ddws', 445], ['bjmcpune', -1], ['digilocker', 126],
        ['linkedin', 13], ['poptin', 123],
    ],
    "singapore": [
        ['bydcars', 524], ['propertypages', 455], ['fca', 79], ['itiger', 82],
        ['kindtokind', 496], ['max', -1], ['mddi', 309], ['schwab', 87],
    ],
    "southafrica": [
        ['1grid', 102], ['bash', 149], ['nemisa2', 313], ['nsfas-application', 122],
        ['showmesa', 395], ['alexforbes', 380], ['amazon', -1], ['cemair', 489],
        ['momentumgroupltd', 471], ['ticketpro', 212],
    ],
    "southkorea": [
        ['etoos', -1], ['iteasy', 193], ['portone', 187], ['cbnu', 202],
        ['cjlogistics', 504], ['halfdomain', 127], ['niceid', 415],
        ['sooplive', 70], ['tason', 304], ['thepinkfongcompany', 115],
        ['tmapmobility', 172], ['ybm', 507],
    ],
    "spain": [
        ['aniyt', 414], ['olin', 508], ['pp', 372], ['udit', 472],
        ['cableworld', 504], ['mundodeportivo', -1],
    ],
    "unitedstates": [
        ["unity", 47], ["parse", 434], ["wyze", 457], ["x", 7],
    ],
}