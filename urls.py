from django.conf.urls.defaults import patterns

# All of the static content pages, which render directly to a template.
urlpatterns = patterns('django.views.generic.simple',
                       
    (r'^$', 'direct_to_template', {'template': 'diyTarot/index.html'}),
    (r'^faq/$', 'direct_to_template', {'template': 'diyTarot/faq.html'}),
    (r'^tarot/$', 'direct_to_template', {'template': 'diyTarot/tarot.html'}),
    (r'^reading/howitworks/$', 'direct_to_template', {'template': 'diyTarot/howitworks.html'}),
    (r'^about/$', 'direct_to_template', {'template': 'diyTarot/about.html'}),
    (r'^about/features/$', 'direct_to_template',  {'template': 'diyTarot/features.html'}),
    (r'^about/technical/$', 'direct_to_template', {'template': 'diyTarot/technical.html'})
)

# All of the dynamic content pages, which specify a view to process the information.
urlpatterns += patterns('',
                                              
    # decks -> list of decks
    (r'^decks/$', 'diyTarot.views.deck_list'),
    
    # cards -> list of all cards across all decks
    (r'^cards/$', 'diyTarot.views.card_list'),
    
    # cards/random -> detail on a randomly chosen card
    (r'^cards/random/$', 'diyTarot.views.random_card'),
    
    # decks/deck_id  -> browse a specific deck
    (r'^decks/(?P<deck_id>\d+)/$', 'diyTarot.views.deck_detail'),
    
    # cards/tarot_index/deck_id
    (r'^cards/(?P<tarot_index>\d+)/(?P<deck_id>\d+)/$', 'diyTarot.views.card_detail'),
    
    # cards/tarot_index/ - shows all the versions of a card, across decks
    (r'^cards/(?P<tarot_index>\d+)/$', 'diyTarot.views.tarot_card_detail'),
    
    # reading/ - gives you the reading page but with deck and spread chosen for you
    (r'^reading/$', 'diyTarot.views.random_reading'),
                  
    # reading/spread_id/deck_id -> reading using spread and deck   
    (r'^reading/(?P<spread_id>\d+)/(?P<deck_id>\d+)/$', 
     'diyTarot.views.reading'),
                        
    # reading/save_settings/spread_id -> update settings
    (r'^reading/save_settings/(?P<spread_id>\d+)/$', 'diyTarot.views.update_reading_settings'),
                       
    # spreads -> list of spreads
    (r'^spreads/$', 'diyTarot.views.spread_list'),
)
