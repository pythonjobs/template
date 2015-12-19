/* jshint strict: true, undef: true */
/* globals jQuery,window */
(function() {
  "use strict";  

  if (!Array.isArray) Array.isArray = function(arg) {
    return Object.prototype.toString.call(arg) === '[object Array]';
  };

  if (!Object.keys) Object.keys = function(o) {
    var k=[],p;
    for (p in o) if (Object.prototype.hasOwnProperty.call(o,p)) k.push(p);
    return k;
  };

  if (!Object.values) Object.values = function(o, f) {
      var v=[],p;
      if (f) { 
        for (p in o) if (Object.prototype.hasOwnProperty.call(o,p) && f(o[p])) v.push(o[p]);
      } else {
        for (p in o) if (Object.prototype.hasOwnProperty.call(o,p)) v.push(o[p]);
      }
      return v;
  };

  function escapeRegExp(str) {
   return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
  }

  jQuery(function ($) {

    var job_list = null;
    var root_index = null;
    var index_loading = false;

    var search_box = $("#text_search");
    var search_info = $("#search_info");
    var search_id = null;

    function load_index() {
      if (index_loading) { return; }
      index_loading = true;
      $.getJSON("/text_index.json")
        .then(function(data) {
          job_list = data[0];
          root_index = data[1];
          do_search();
        })
        .error(function(e) {
          window.console.log(e);
        });
    }

    function pend_search() {
      load_index();
      if (search_id) { return; }
      search_id = window.setTimeout(function() { search_id=null; do_search(); }, 100);
    }

    function find_leaves(node) {
      if (Array.isArray(node)) {
        return node;
      }
      var found = ("" in node) ? node[''] : [];
      for (var key in node) {
        var leaves = find_leaves(node[key]);
        found = found.concat(leaves);
      }
      return found;
    }

    function match_substr(lookup, value) {
      for (var i=1; i<=value.length; ++i){
        var test = value.slice(0,i);
        if (test in lookup) {
          return test;
        }
        for (var prefix in lookup) {
          if (prefix.indexOf(value) === 0) {
            return prefix;
          }
        }
      }
    }

    function find_matches(val) {
      var current = root_index;
      var rest = val;
      while (rest) {
        if (Array.isArray(current)) { return current; }
        var match = match_substr(current, rest);
        if (!match) { return []; }
        current = current[match];
        rest = rest.slice(match.length);
      }
      if (current !== root_index) {
        return find_leaves(current);
      }
      return [];
    }

    function clear_search(msg) {
      update_ui();

      search_info.toggleClass("hidden", msg ? false : true);
      if (msg) {
        search_info.text(msg);
      }
    }

    function update_ui(jobs) {
      var all_jobs, matched;

      if (jobs) {
        var job_lookup = {};
        $.each(jobs, function(index, job) {
          job_lookup[job.slug] = index;
        });

        var sort_info = function(el) {
          var slug = $(el).data('slug');
          var order = $(el).data('order');
          var score = job_lookup[slug].score;
          score = score > 20 ? 20 : score;
          return {score: score, order: parseInt(order, 10)};
        };

        all_jobs = $(".job");
        matched = all_jobs.filter(function() {
          return $(this).data('slug') in job_lookup;
        }).sort(function(el_a, el_b) {
          var a_info = sort_info(el_a);
          var b_info = sort_info(el_b);
          var score_diff = a_info.score - b_info.score;
          return score_diff || a_info.order - b_info.order;
        });
      } else {
        all_jobs = matched = $(".job").sort(function(a, b) {
          return parseInt($(a).data('order'), 10)-parseInt($(b).data('order'), 10);
        });
      }
      if (!matched.length) {
        return clear_search("No matches found");
      }
      all_jobs
        .removeClass("has_match")
        .find('.search_match')
        .text("");

      var not_matched = all_jobs.not(matched);
      not_matched.hide();
      matched.show();

      if (jobs){
        matched.addClass('needs_excerpt');
        not_matched.removeClass('needs_excerpt');
      } else {
        all_jobs.removeClass('needs_excerpt');
      }

      var num_jobs = all_jobs.length;
      var num_matches = matched.length;
      search_info.removeClass("hidden");
      search_info.text("Showing " + num_matches + " of " + num_jobs + " jobs");
      matched.detach().appendTo($("section.job_list"));
      load_an_excerpt();
    }

    search_box.change(function(){
      pend_search();
    });

    search_box.keyup(function() {
      pend_search();
    });

    var last_search_val = null;
    function do_search() {
      load_index();
      if (root_index === null ||  job_list === null) { return; }
      var search_text = search_box.val().toLowerCase();
      if (search_text == last_search_val) { return; }
      last_search_val = search_text;
      if (!search_text) { clear_search(); return; }
      var parts = search_text.split(/\W+/g);

      var results = {};

      function get_result(m) {
        if (!(m in results)) {
          results[m] = {
            slug: job_list[m],
            count: 0,
            score: 0
          };
        }
        return results[m];
      }

      parts.forEach(function(part) {
        var part_tally = {};
        var term = window.stemmer(part);
        var matches = find_matches(term);
        matches.forEach(function(m) {
          var match = m[0], value = m[1];
          var result = get_result(match);
          if (!(match in part_tally)) {
            part_tally[match] = true;
            result.count += 1;
          }
          result.score += value;
        });
      });

      results = Object.values(results);
      results = $.grep(results, function(result) {
        return result.count == parts.length;
      });
      update_ui(results);
      return results;
    }

    function highlight_matches(data){
      var parts = search_box.val().split(/\W+/g);
      var re_matcher = [];
      parts.forEach(function(part) { re_matcher.push(escapeRegExp(part));});
      var re = new RegExp("\\b(" + re_matcher.join("|") +")", 'ig');
      
      var offsets = [];
      var content = data.replace(re, function(match, _, offset) {
        var PADDING = 35;
        offsets.push({start: offset-PADDING, end: offset+match.length+PADDING});
        return match;
      })

      var spans = [];
      var MAX_LENGTH = 150;
      var total_length = 0;
      var current = null;
      for(var i=0; i<offsets.length; ++i) {
        var offset = offsets[i];
        if (current === null) {
          current = offset;
        } else {
          if (offset.start <= current.end) {
            current.end = offset.end;
            if (total_length + (current.end - current.start) >= MAX_LENGTH) break;
          } else {
            spans.push(current);
            total_length += (current.end - current.start);
            current = offset;
          }
        }
        if (total_length >= MAX_LENGTH) break;
      }
      if (current !== null) { spans.push(current); }
      if (!spans.length) return "";
      
      var output = '';
      spans.forEach(function(span) {
        var start = (span.start < 0) ? 0 : span.start;
        if (start !== 0) {
          output += '<span class="sep">&hellip;</span>';
        }
        var snippet = $("<div/>").text(content.slice(start, span.end)).html();
        var highlighted = snippet.replace(re, function(match, _, offset) {
          return '<span class="match">' + match + '</span>';
        });
        output += highlighted;
      })
      
      return output;
    }

    var excerpt_cache = {};
    function load_an_excerpt(el){
      var the_job = $(".job.needs_excerpt").first();
      if (!the_job.length) return;

      var slug = the_job.data('slug');

      function update_job(data) {
        the_job.removeClass('needs_excerpt');
        var excerpt = highlight_matches(data);
        if (excerpt) {
          the_job.addClass("has_match");
          $(".search_match", the_job).html(excerpt);
        }
        window.setTimeout(load_an_excerpt, 10);
      }

      if (slug in excerpt_cache) {
        update_job(excerpt_cache[slug]);
      } else {
        $.get("/excerpts/" + slug + ".txt")
          .then(function(data) {  
            excerpt_cache[slug] = data;
            update_job(data);
          })
      }
    }

  });
})();