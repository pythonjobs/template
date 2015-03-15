//Array.prototype.indexOf may exist in all browsers according to MDN
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (item) {
        for (var i = 0; i < this.length; i++) {
            var it = this[i]
            if (it == item) {
                return i;
            }
        }
        return -1;
    };
}

Array.prototype.contains = function (item) {
    return this.indexOf(item) !== -1;
};

Array.prototype.containsAll = function (items) {
    for (var i = 0; i < items.length; i++) {
        var t = items[i];
        if (!this.contains(t)) return false;
    }
    return true;
};

Array.prototype.remove = function (item) {
    var idx = this.indexOf(item);
    if (idx !== -1) {
        this.splice(idx, 1);
    }
}

//set add method
Array.prototype.add = function (item) {
    if (!this.contains(item)) {
        this.push(item);
    }
}


jQuery(function ($) {
    var selected_tags = [];

    function save() {
        if (window.localStorage) {
            localStorage.selected_tags = JSON.stringify(selected_tags);
        }
    }

    function load() {
        if (window.localStorage && window.localStorage.selected_tags) {
            var tags = JSON.parse(localStorage.selected_tags);
            for (var i = 0; i < tags.length; i++) {
                createTagButton(tags[i]);
                selected_tags.add(tags[i]);
            }
            filterJobs();
        }
    }

    function createTagButton(name) {
        var tag = $('<b />').text(name);
        var close = $('<span>\u00D7</span>').appendTo(tag);
        tag.appendTo('#selected-tags');

        close.click(function (event) {
            tag.remove();
            selected_tags.remove(name);
            filterJobs();
            save();
        });
    }

    function addTag(name) {
        if (selected_tags.contains(name))
            return;
        selected_tags.add(name);
        createTagButton(name);
        filterJobs();
        save();
    }

    function filterJobs() {
        $('.job').each(function () {
            var tags = $(this).attr('data-tags').split(',');
            $(this).toggle(tags.containsAll(selected_tags));
        });

        var title;
        if (selected_tags.length == 0) {
            title = 'Most Recent Jobs';
        } else {
            var total = $('.job').length;
            var showing = $('.job:visible').length;
            title = 'Showing ' + showing + ' of ' + total + ' jobs';
        }
        $('#list-title').text(title);
    }

    $('<span class="close">\u00D7</span>').appendTo($('#filter')).click(function () {
        $('#filter').slideUp();
    });

    $('#filter-link').click(function (event) {
        event.preventDefault();
        $('#filter').slideToggle();
    });

    $('#filter a').click(function (event) {
        event.preventDefault();
        addTag($(this).text());
    });

    load();
});
