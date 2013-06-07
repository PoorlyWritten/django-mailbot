;(function ($, window, undefined) {
  'use strict';

  var $doc = $(document),
      Modernizr = window.Modernizr;

  $(document).ready(function() {
    $.fn.foundationAlerts           ? $doc.foundationAlerts() : null;
    $.fn.foundationButtons          ? $doc.foundationButtons() : null;
    $.fn.foundationAccordion        ? $doc.foundationAccordion() : null;
    $.fn.foundationNavigation       ? $doc.foundationNavigation() : null;
    $.fn.foundationTopBar           ? $doc.foundationTopBar() : null;
    $.fn.foundationCustomForms      ? $doc.foundationCustomForms() : null;
    $.fn.foundationMediaQueryViewer ? $doc.foundationMediaQueryViewer() : null;
    $.fn.foundationTabs             ? $doc.foundationTabs({callback : $.foundation.customForms.appendCustomMarkup}) : null;
    $.fn.foundationTooltips         ? $doc.foundationTooltips() : null;
    $.fn.foundationMagellan         ? $doc.foundationMagellan() : null;
    $.fn.foundationClearing         ? $doc.foundationClearing() : null;

    $.fn.placeholder                ? $('input, textarea').placeholder() : null;
  });

  // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
  // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
  // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
  // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
  // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

  // Hide address bar on mobile devices (except if #hash present, so we don't mess up deep linking).
  if (Modernizr.touch && !window.location.hash) {
    $(window).load(function () {
      setTimeout(function () {
        window.scrollTo(0, 1);
      }, 0);
    });
  }

})(jQuery, this);

$(document).ready(function() {
    window.Introducee = Backbone.Model.extend({});
    window.IntroduceeCollection = Backbone.Collection.extend({
        model: Introducee,
    });
    window.Introduction = Backbone.Model.extend({
        urlRoot: INTRODUCTION_API
    });
    window.IntroductionCollection = Backbone.Collection.extend({
        urlRoot: INTRODUCTION_API,
        model: Introduction,
        initialize: function() {
            this._sort_order = 'desc';
        },
        comparator: function(element) {
            var date = new Date(element.get('created'));
            return this._sort_order == 'desc'
                 ? -date.getTime()
                 :  date.getTime()
        },
        reverse: function() {
            this._sort_order = this._sort_order == 'desc' ? 'asc' : 'desc';
            this.sort();
        },
        emails: function() {
            return _.union(
                this.map( function(element, index, list) {return element.attributes.introducee1}),
                this.map(function(element, index, list) {return element.attributes.introducee2})
                );
            },
        email_popularity: function() {
            var that = this;
            var dict = {}
            var mymap = _.each(
                this.emails(),
                function(email_addr, index, list){
                    var length = that.filter(function(element){
                        return (element.attributes.introducee1 == email_addr || element.attributes.introducee2 == email_addr)}).length;
                    dict[email_addr] = length;
                    //{address: email_addr, length: length};
                }
            );
            return dict
        }
    });

    window.IntroductionView = Backbone.View.extend({
        // model: Needs to be an instance of the Introduction
        template: _.template("<div class='introitem'><div class='row'><div class='connectors'><h4><%= introducee1 %> &amp; <%= introducee2 %></h4></div></div><div class='row'><div class='introduction'><div class='row'><div class='details'><p class='subject'><%= subject %></p><p class='body'><%= message %></p></div><div class='feedback'><div class='feedback-button'>Request Feedback</div></div></div></div></div></div>"),
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    window.IntroductionCollectionView = Backbone.View.extend({
        // collection: Needs to be an instance of the IntroductionCollection
        childViews: [],
        initialize: function() {
            this.listenTo(this.collection, 'sort', this.render);
            //this.listenTo(this.collection, 'all', this.eventer);

            this.collection.fetch({
                success: function(collection, response, options){
                    console.log("Loaded collection in init for IntroductionCollectionView")
                },
                error: function(collection, response, options){
                    console.log("Failed to load collection in init for IntroductionCollectionView")
                },
            });
        },
        addOne: function(introduction) {
            var myview = new IntroductionView({model: introduction});
            $(this.$el).append(myview.render().el);

        },
        eventer: function(event) {
            console.log("Got the signal (" + event + ") and this is " + this);
        },
        render: function() {
            var that = this;
            $(this.el).html('');
            this.collection.each(function(element, index, list){
                that.addOne(element);
            })
        }

    });

    window.app = window.app || {};
    app.introductions = new IntroductionCollection();
    app.introducees = new IntroduceeCollection({ introductions: app.introductions });
    app.introsview = new IntroductionCollectionView({collection: app.introductions, el: $(".introslist")});

});
