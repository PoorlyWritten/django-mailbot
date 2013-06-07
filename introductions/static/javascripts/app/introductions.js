(function  ($) {
    window.Introduction = Backbone.Model.extend({
        urlRoot: INTRODUCTION_API
        emails: function() {
            return _.union(
                this.map( function(element, index, list) {return element.attributes.introducee1}),
                this.map(function(element, index, list) {return element.attributes.introducee2})
                );
            }
    });
    window.IntroductionCollection = Backbone.Model.extend({
        urlRoot: INTRODUCTION_API,
        model: Introduction
    });

    window.IntroductionCollectionView = Backbone.View.extend({
        // collection: Needs to be an instance of the IntroductionCollection
        tagName: "div",
        id: "introlistcontainer",
        initialize: function() {
            this.listenTo(this.collection, "change", this.render);
        }
    });

    window.app = window.app || {};
    app.introductions = new IntroductionCollection();
    app.introsview = new IntroductionCollectionView({collection: app.introductions});

})
