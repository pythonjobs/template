"use strict";

if (!Array.isArray) Array.isArray = function(arg) {
	return Object.prototype.toString.call(arg) === '[object Array]';
}

if (!Object.keys) Object.keys = function(o) {
	var k=[],p;
	for (p in o) if (Object.prototype.hasOwnProperty.call(o,p)) k.push(p);
	return k;
}

if (!Object.values) Object.values = function(o, f) {
	var v=[],p;
	if (f) {
		for (p in o) if (Object.prototype.hasOwnProperty.call(o,p) && f(o[p])) v.push(o[p]);	
	} else {
		for (p in o) if (Object.prototype.hasOwnProperty.call(o,p)) v.push(o[p]);
	}
	return v;
}

jQuery(function ($) {
	"use strict"

	var job_list = null;
	var root_index = null;
	var index_loading = false;

	var search_box = $("#text_search");
	var search_info = $("#search_info");
	var search_id = null;

	function pend_search() {
		load_index();
		if (search_id) { return; }
		search_id = window.setTimeout(function() { search_id=null; do_search(); }, 100);
	}

	function load_index() {
		if (index_loading) { return; }
		index_loading = true;
		$.getJSON("/text_index.json")
			.then(function(data) {
				job_list = data[0];
				root_index = data[1];
				do_search()
			})
			.error(function(e) {
				console.log(e);
			})
	}

	function stem(term) {
		return term;
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
				if (prefix.indexOf(value) == 0) {
					return prefix;
				}
			}
		}
	}

	function find_matches(val) {
		var current = root_index;
		var rest = val;
		while (rest) {
			if (Array.isArray(current)) { return []; }
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
		if (jobs) {
			var job_lookup = {};
			$.each(jobs, function(index, job) {
				job_lookup[job.slug] = index;
			});

			function sort_info(el) {
				var slug = $(el).data('slug');
				var order = $(el).data('order');
				var score = job_lookup[slug].score;
				score = score > 8 ? 8 : score;
				return {score: score, order: parseInt(order, 10)};
			}

			var all_jobs = $(".job");
			var matched = all_jobs.filter(function() {
				return $(this).data('slug') in job_lookup;
			}).sort(function(el_a, el_b) {
				var a_info = sort_info(el_a);
				var b_info = sort_info(el_b);
				var score_diff = a_info.score - b_info.score;
				return score_diff || a_info.order - b_info.order;
			});
		} else {
			var all_jobs = matched = $(".job").sort(function(a, b) {
				return parseInt($(a).data('order'), 10)-parseInt($(b).data('order'), 10);
			});
		}
		if (matched.length == 0) {
			return clear_search("No matches found, or word too common");

		}
		all_jobs.hide();
		matched.show();

		var num_jobs = all_jobs.length;
		var num_matches = matched.length;
		search_info.removeClass("hidden");
		search_info.text("Showing " + num_matches + " of " + num_jobs + " jobs");
		matched.detach().appendTo($("section.job_list"));
		
	}

	function do_search() {
		load_index();
		if (root_index === null ||	job_list === null) { return; }
		var search_text = search_box.val().toLowerCase();
		if (!search_text) { clear_search(); return; }
		var parts = search_text.split(/\W+/g);
		
		var results = {};

		function get_result(m) {
			if (!(m in results)) {
				results[m] = {
					slug: job_list[m],
					count: 0,
					score: 0
				}
			}
			return results[m];
		}

		parts.forEach(function(part) {
			var part_tally = {};
			var term = stemmer(part)
			console.log(part, term)
			var matches = find_matches(term);
			matches.forEach(function(m) {
				var match = m[0], value = m[1];
				var result = get_result(match);
				if (!(match in part_tally)) {
					part_tally[match] = true;
					result.count += 1;
				}
				result.score += value;
			})
		});

		var results = Object.values(results);
		results = $.grep(results, function(result) { 
			return result.count == parts.length; 
		});
		update_ui(results);
		return results;
	}

	search_box.change(function(){
		pend_search();
	});

	search_box.keyup(function() {
		pend_search();
	})

});