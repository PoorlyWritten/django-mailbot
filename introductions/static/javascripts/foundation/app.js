function eventer(event) {
            console.log("Got the signal (" + event + ") and this is " + this);
        };
function timesince(when) {
    var hour = 1000*60*60;
    var day = hour*24;
    var week = day*7;
    var month = day*30;
    var year = day*365;
    var today = new Date();
    var in_milliseconds = Math.ceil(today.getTime() - when.getTime());
    if (in_milliseconds < day*10){
        return ~~(in_milliseconds/day) + " days";
    }
    if (in_milliseconds < month * 3){
        return ~~(in_milliseconds/week) + " weeks";
    }
    return ~~(in_milliseconds/month) + " months";
};

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
    window.Introducee = Backbone.Model.extend({
        sync: function () { return true; },

    });
    window.IntroduceeCollection = Backbone.Collection.extend({
        model: Introducee,
        comparator: function(ab) {
            return -ab.get('length');
        },
    });
    window.IntroduceeView = Backbone.View.extend({
        // model: Needs to be an instance of the Introduction
        template: _.template("<li><span><%= length %></span> <%= email %></li>"),
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    window.IntroduceeCollectionView = Backbone.View.extend({
        // collection: Needs to be an instance of the IntroductionCollection
        childViews: [],
        initialize: function() {
            this.listenTo(this.collection, 'sort', this.render);
            //this.listenTo(this.collection, 'all', this.eventer);
        },
        addOne: function(introducee) {
            var myview = new IntroduceeView({model: introducee});
            $(this.$el).append(myview.render().el);

        },
        render: function() {

            var that = this;
            $(this.el).html('');
            this.collection.each(function(element, index, list){
                if (index < 5){
                    that.addOne(element);
                }
            });
        }

    });

    window.Introduction = Backbone.Model.extend({
        urlRoot: INTRODUCTION_API
    });
    window.IntroductionCollection = Backbone.Collection.extend({
        urlRoot: INTRODUCTION_API,
        model: Introduction,
        initialize: function() {
            this._sort_order = 'desc';
            this.listenTo(this, 'sync', this.build_introducee_collection);
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
        },
        build_introducee_collection: function() {
            var that = this;
            app.introducees.reset();
            _.each(
                this.emails(),
                function(email_addr, index, list){
                    var length = that.filter(function(element){
                        return (element.attributes.introducee1 == email_addr || element.attributes.introducee2 == email_addr)}).length;
                    app.introducees.create({email: email_addr, length: length, url: null});
                }
            );
        },
        graphdata: function(period) {
            if (period == "week") {
                var dates =  {};
                this.each( function(element, index, list) {
                    var date = new Date(element.get("created"));
                    var day = date.getDate() + 1;
                    var month = date.getMonth() + 1;
                    var datestring = month + "/" + day
                    if (datestring in dates){
                        dates[datestring] += 1
                    } else {
                        dates[datestring] = 1
                    }
                });
                return dates;
            }
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
            //this.listenTo(this.collection, 'all', eventer);

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
        render: function() {
            var that = this;
            $(this.el).html('');
            this.collection.each(function(element, index, list){
                that.addOne(element);
            })
        }

    });

    var IntrosRouter = Backbone.Router.extend({

      routes: {
        "dashboard":            "dashboard",    // #dashboard
        "*action": "defaultRoute"
      },

      dashboard: function() {
            console.log(" In the dashboard route");
            app.introductions = new IntroductionCollection();
            app.introducees = new IntroduceeCollection();
            app.introsview = new IntroductionCollectionView({collection: app.introductions, el: $(".introslist")});
            app.introduceesview = new IntroduceeCollectionView({collection: app.introducees, el: $("ul.leaderboard")});
            app.introductions.on('sync', function(){
                lineChartData.labels = new Array();
                lineChartData.datasets[0].data = new Array();
                for (x in app.introductions.graphdata("week")){
                    lineChartData.labels.push(x);
                    lineChartData.datasets[0].data.push(app.introductions.graphdata("week")[x]);
                }
                lineChartData.labels.reverse();
                lineChartData.datasets[0].data.reverse();
                var myLine = new Chart(
                    document.getElementById("canvas") .getContext("2d")
                    ).Line(lineChartData, lineChartDefaults);

            });
      },
      defaultRoute: function (action) {
        console.log(" In the default route");
        console.log(" action = " + action);
      },


    });

    window.app = window.app || {};
    window.router = new IntrosRouter();
    Backbone.history.start({ pushState: true });

});

